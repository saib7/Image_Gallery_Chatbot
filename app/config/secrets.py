import dotenv
import os
from app.config import config


dotenv.load_dotenv(dotenv_path=config.ENV_FILE_PATH)
gemini_api_key = os.getenv(config.API_KEY_ENV_VAR)

