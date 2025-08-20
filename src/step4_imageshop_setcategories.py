import requests
from pathlib import Path
from .config import IMAGESHOP, RESPONSES_DIR, TARGET_DATE
from .logger import get_logger
from .utils import load_json, save_json

log = get_logger("step4")

STRIP_CATEGORY_ID = 57239

def run(imageshop_categories_file: Path) -> Path:
    token = IMAGESHOP["token"]
    if not token:
        raise RuntimeError("IMAGESHOP_TOKEN must be set in .env")

    base = IMAGESHOP["base_url"]
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "token": token
    }
    url = f"{base}/Document/SetCategories"

    entries = load_json(imageshop_categories_file)
    if not isinstance(entries, list):
        raise ValueError("imageshop categories JSON must be an array")

    results = []
    for entry in entries:
        info_value = entry.get("InfoValue")
        cat_resp = entry.get("CategoryResponse", [])
        if not isinstance(cat_resp, list):
            continue

        for doc in cat_resp:
            doc_id = doc.get("documentId")
            cats = doc.get("documentCategoryIds", [])

            cleaned = []
            for c in cats:
                try:
                    cid = int(c)
                    if cid != STRIP_CATEGORY_ID:
                        cleaned.append(cid)
                except Exception:
                    if c != str(STRIP_CATEGORY_ID):
                        cleaned.append(c)

            if doc_id is None:
                results.append({
                    "InfoValue": info_value,
                    "documentId": doc_id,
                    "sentCategories": cleaned,
                    "error": "Missing documentId"
                })
                continue

            try:
                r = requests.put(url, headers=headers, params={"documentId": str(doc_id)}, json=cleaned, timeout=30)
                try:
                    payload = r.json()
                except Exception:
                    payload = {"raw": r.text}
                results.append({
                    "InfoValue": info_value,
                    "documentId": doc_id,
                    "sentCategories": cleaned,
                    "status_code": r.status_code,
                    "response": payload
                })
            except requests.RequestException as e:
                log.error("SetCategories failed for doc %s (InfoValue %s): %s", doc_id, info_value, e)
                results.append({
                    "InfoValue": info_value,
                    "documentId": doc_id,
                    "sentCategories": cleaned,
                    "error": str(e)
                })

    out_path = RESPONSES_DIR / f"imageshop_setcategories_{TARGET_DATE}.json"
    save_json(out_path, results)
    log.info("Saved SetCategories results (%d docs) -> %s", len(results), out_path)
    return out_path
