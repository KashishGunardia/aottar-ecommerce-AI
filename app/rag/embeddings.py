from langchain_community.embeddings import FastEmbedEmbeddings


def get_embedding_model():
    # FastEmbed runs this model on onnxruntime (CPU), not PyTorch.
    # Same model/dimensions (384) as before, so the existing bundled FAISS
    # index (app/rag/product_index/) stays compatible - but it skips
    # installing torch + transformers + the CUDA wheels those pull in
    # (over 2GB of downloads, several hundred MB of RAM at runtime), which
    # is what was causing this app to get OOM-killed on Render's free tier
    # (512MB RAM limit).
    embeddings = FastEmbedEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings
