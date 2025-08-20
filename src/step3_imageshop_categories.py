import requests
from pathlib import Path
from .config import IMAGESHOP, RESPONSES_DIR, TARGET_DATE
from .logger import get_logger
from .utils import load_json, save_json

log = get_logger("step3")

def run(imageshop_results_file: Path) -> Path:
    token = IMAGESHOP["token"]
    if not token:
        raise RuntimeError("IMAGESHOP_TOKEN must be set in .env")

    base = IMAGESHOP["base_url"]
    headers = {"Accept": "application/json", "token": token}
    url = f"{base}/Category/GetCategoryIdsByDocumentIds"

    entries = load_json(imageshop_results_file)
    if not isinstance(entries, list):
        raise ValueError("imageshop results JSON must be an array")

    out = []
    for entry in entries:
        infovalue = entry.get("InfoValue")
        resp_payload = entry.get("Response", [])

        if isinstance(resp_payload, list):
            doc_ids = resp_payload
        elif isinstance(resp_payload, dict) and "raw" in resp_payload:
            doc_ids = []
        else:
            doc_ids = [resp_payload] if isinstance(resp_payload, int) else []

        if doc_ids:
            params = {"documentIds": ",".join(str(x) for x in doc_ids)}
            try:
                r = requests.post(url, headers=headers, params=params, timeout=30)
                try:
                    cat_payload = r.json()
                except Exception:
                    cat_payload = {"raw": r.text}
            except requests.RequestException as e:
                log.error("Category lookup failed for %s: %s", infovalue, e)
                cat_payload = {"error": str(e)}
        else:
            cat_payload = []

        out.append({
            "InfoValue": infovalue,
            "DocumentIds": doc_ids,
            "CategoryResponse": cat_payload
        })

    out_path = RESPONSES_DIR / f"imageshop_categories_{TARGET_DATE}.json"
    save_json(out_path, out)
    log.info("Saved category lookups (%d entries) -> %s", len(out), out_path)
    return out_path
