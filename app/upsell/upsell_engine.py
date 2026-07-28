class UpsellEngine:

    def __init__(self):

        self.mapping = {

            "Smart Door Locks": [
                "Smart Doorbells",
                "Video Doorbells",
                "Installation Service"
            ],

            "CCTV Cameras": [
                "Hard Disk",
                "Power Supply",
                "Installation Service"
            ],

            "Smart Touch Switches": [
                "Smart Curtain Motors",
                "Smart Lights"
            ],

            "Smart Doorbells": [
                "Smart Door Locks",
                "Smart Switches"
            ],

            "Smart Curtain Motors": [
                "Smart Switches",
                "Home Automation"
            ]
        }

    def recommend(self, category):

        return self.mapping.get(category, [])