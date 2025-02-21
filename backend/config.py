import os
from dotenv import load_dotenv


env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

load_dotenv(dotenv_path=env_path)

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")
LOG_FILE = os.getenv("LOG_FILE", "logs/summary.log")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
REDIS_ENABLED = False
REDIS_URL = os.getenv("REDIS_URL", "Not Found")

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("llm_api_key")

print(f"Loaded Config: REDIS_URL={REDIS_URL}, CACHE_TTL={CACHE_TTL}")