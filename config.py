import os
import hvac
from dotenv import load_dotenv

load_dotenv()

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
VAULT_PATH = os.getenv("VAULT_PATH", "secret/data/gpsd/escalation-mgmt")

def get_vault_client():
    if not VAULT_TOKEN:
        return None
    
    client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
    if not client.is_authenticated():
        print("Warning: Vault client failed to authenticate")
        return None
    
    return client

def get_secret(key, default=None):
    client = get_vault_client()
    if client:
        try:
            secret = client.secrets.kv.v2.read_secret_version(path=VAULT_PATH.split('/data/')[1])
            data = secret.get('data', {}).get('data', {})
            if key in data:
                return data[key]
        except Exception as e:
            print(f"Warning: Couldn't retrieve {key} from Vault: {e}")
    
    return os.getenv(key, default)

OPENAI_API_KEY = get_secret("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
PREDICTHQ_API_KEY = get_secret("PREDICTHQ_API_KEY", os.getenv("PREDICTHQ_API_KEY"))
PREDICTHQ_SEARCH_URL = os.getenv("PREDICTHQ_SEARCH_URL")
ACCESS_API_KEYS = get_secret("ACCESS_API_KEYS", os.getenv("ACCESS_API_KEYS", "")).split(",")

REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_HOST = get_secret("REDIS_HOST", os.getenv("REDIS_HOST"))
REDIS_PASSWORD = get_secret("REDIS_PASSWORD", os.getenv("REDIS_PASSWORD"))
REDIS_DB_NAME = get_secret("REDIS_DB_NAME", os.getenv("REDIS_DB_NAME"))
