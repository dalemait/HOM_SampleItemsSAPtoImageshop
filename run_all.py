from pathlib import Path
from src.config import TARGET_DATE
from src.logger import get_logger
from src.utils import write_last_run
from src.step1_hana_item_changes import run as step1_run
from src.step2_imageshop_documents import run as step2_run
from src.step3_imageshop_categories import run as step3_run
from src.step4_imageshop_setcategories import run as step4_run

log = get_logger("runner")

def main():
    write_last_run(status="started", summary={}, target_date=TARGET_DATE)
    try:
        # Step 1: HANA -> ItemCodes
        item_changes_path = step1_run()

        # Step 2: Document IDs
        imageshop_results_path = step2_run(Path(item_changes_path))

        # Step 3: Category IDs
        imageshop_categories_path = step3_run(Path(imageshop_results_path))

        # Step 4: Strip 57239 and PUT back
        setcategories_log_path = step4_run(Path(imageshop_categories_path))

        summary = {
            "had_item_changes_file": 1,
            "had_imageshop_results_file": 1,
            "had_imageshop_categories_file": 1,
            "had_setcategories_log_file": 1,
        }
        write_last_run(status="success", summary=summary, target_date=TARGET_DATE)
        log.info("Pipeline completed successfully for %s", TARGET_DATE)
    except Exception as e:
        log.exception("Pipeline failed: %s", e)
        write_last_run(status="error", summary={}, target_date=TARGET_DATE)
        raise

if __name__ == "__main__":
    main()
