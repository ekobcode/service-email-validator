import os

API_KEYS = [
    "app_prod_0f8fad5b-d9cb-469f-a165-70867728950e_Y8a2XW",
    "app_dev_1c6c7cbe-bdbb-41d2-a1e0-1cfb10ec93d4_Qz9PpK",
    os.getenv("API_KEY_ENV", "app_local_dev_default_Zx81bV")
]
