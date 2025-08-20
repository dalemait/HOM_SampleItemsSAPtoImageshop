import requests
from pathlib import Path
from .config import IMAGESHOP, RESPONSES_DIR, TARGET_DATE
from .logger import get_logger
from .utils import load_json, save_json

log = get_logger("step2")

def run(item_changes_file: Path) -> Path:
    token = IMAGESHOP["token"]
    if not token:
        raise RuntimeError("IMAGESHOP_TOKEN must be set in .env")

    base = IMAGESHOP["base_url"]
    documentinfoid = IMAGESHOP["documentinfoid"]

    values = load_json(item_changes_file)
    if not isinstance(values, list):
        raise ValueError("item changes JSON must be an array")

    headers = {"Accept": "application/json", "token": token}
    url = f"{base}/Document/GetDocumentIdByDocumentInfo"

    results = []
    for infovalue in values:
        params = {"_DocumentinfoID": str(documentinfoid), "_InfoValue": str(infovalue)}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            try:
                payload = resp.json()
            except Exception:
                payload = {"raw": resp.text}
            results.append({
                "InfoValue": infovalue,
                "Response": payload if isinstance(payload, list) else payload
            })
        except requests.RequestException as e:
            log.error("Document lookup failed for %s: %s", infovalue, e)
            results.append({"InfoValue": infovalue, "Response": {"error": str(e)}})

    out_path = RESPONSES_DIR / f"imageshop_results_{TARGET_DATE}.json"
    save_json(out_path, results)
    log.info("Saved document lookups (%d entries) -> %s", len(results), out_path)
    return out_path
