from pathlib import Path
import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

# Load .env once for the whole process
load_dotenv()

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
RESPONSES_DIR = BASE_DIR / "responses"
LOGS_DIR = BASE_DIR / "logs"
STATE_DIR = BASE_DIR / "state"
for d in (RESPONSES_DIR, LOGS_DIR, STATE_DIR):
    d.mkdir(exist_ok=True)

# Timezone & target date
OSLO_TZ = ZoneInfo("Europe/Oslo")
if os.getenv("TARGET_DATE"):
    TARGET_DATE = os.getenv("TARGET_DATE")
else:
    # Yesterday in Europe/Oslo as YYYY-MM-DD
    TARGET_DATE = (datetime.now(OSLO_TZ) - timedelta(days=1)).date().strftime("%Y-%m-%d")

# HANA
HANA = {
    "host": os.getenv("HANA_HOST"),
    "port": int(os.getenv("HANA_PORT", "30015")),
    "user": os.getenv("HANA_USER"),
    "password": os.getenv("HANA_PASSWORD"),
    "schema": os.getenv("HANA_SCHEMA"),
    "encrypt": os.getenv("HANA_ENCRYPT", "false").lower() == "true",
    "sslValidateCertificate": os.getenv("HANA_SSL_VALIDATECERT", "false").lower() == "true",
}

# ImageShop
IMAGESHOP = {
    "base_url": os.getenv("IMAGESHOP_BASE_URL", "https://api.imageshop.no").rstrip("/"),
    "token": os.getenv("IMAGESHOP_TOKEN"),
    "documentinfoid": os.getenv("IMAGESHOP_DOCUMENTINFOID", "487"),
}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
