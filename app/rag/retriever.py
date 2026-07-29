import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.logger import logger
from app.rag.embeddings import get_embedding_model
from app.retrieval.product_loader import load_products

INDEX_PATH = os.path.join(os.path.dirname(__file__), "product_index")


def _bootstrap_documents():
    """
    Builds a minimal set of Documents to index when no pre-built FAISS
    index is on disk (app/rag/product_index/ is gitignored as a generated
    artifact, so a fresh clone/deploy never has it). Uses whatever
    load_products() can get (cache, or a live WooCommerce fetch, or [] if
    that fails too - see app/retrieval/product_loader.py) so the app can
    still start and serve something instead of crashing. The scheduled
    sync job (app/services/product_sync_service.py) rebuilds a fuller
    index with descriptions shortly after startup and hot-swaps it in.
    """

    products = load_products()

    if not products:
        logger.warning(
            "⚠️ No products available to build a FAISS index from yet "
            "(no cache, WooCommerce fetch failed/unreachable). Starting "
            "with a placeholder index - the scheduled product sync will "
            "populate it once WooCommerce is reachable."
        )
        return [Document(page_content="No products indexed yet.", metadata={})]

    documents = []

    for p in products:
        text = (
            f"Product Name: {p.get('name', '')}\n"
            f"Brand: {p.get('brand', '')}\n"
            f"Category: {p.get('category', '')}\n"
            f"Price: ₹{p.get('price', '')}"
        )
        documents.append(Document(page_content=text, metadata=p))

    return documents


def get_retriever():

    embeddings = get_embedding_model()

    try:
        db = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    except Exception as exc:
        logger.warning(
            f"⚠️ No FAISS index found on disk at {INDEX_PATH} ({exc}). "
            f"Building one in memory instead."
        )

        db = FAISS.from_documents(_bootstrap_documents(), embeddings)

        # Best-effort persist so a plain process restart (not a fresh
        # deploy/clone) doesn't have to rebuild it again. Fine if this
        # fails (e.g. read-only filesystem) - it's just a cache.
        try:
            os.makedirs(INDEX_PATH, exist_ok=True)
            db.save_local(INDEX_PATH)
        except Exception:
            logger.warning("Could not persist the bootstrapped FAISS index (non-fatal)")

    retriever = db.as_retriever(
        search_kwargs={"k": 25}
    )

    return retriever