from hdbcli import dbapi
from pathlib import Path
from .config import HANA, RESPONSES_DIR, TARGET_DATE
from .logger import get_logger
from .utils import save_json

log = get_logger("step1")

def run() -> Path:
    if not HANA["schema"]:
        raise RuntimeError("HANA_SCHEMA must be set in .env")

    sql = f'''
    SELECT 
        T0."ItemCode"
    FROM "{HANA["schema"]}"."AITM" T0
    INNER JOIN "{HANA["schema"]}"."OITM" T1 ON T0."ItemCode" = T1."ItemCode"
    WHERE T0."UpdateDate" >= ?
      AND T0."LogInstanc" > 1
      AND EXISTS (
            SELECT 1 
            FROM "{HANA["schema"]}"."AITM" H
            WHERE H."ItemCode" = T0."ItemCode"
              AND H."LogInstanc" = T0."LogInstanc" - 1
              AND H."QryGroup15" = 'Y'
              AND T0."QryGroup15" = 'N'
        )
    ORDER BY T0."ItemCode";
    '''

    out_path = RESPONSES_DIR / f"item_changes_{TARGET_DATE}.json"
    conn = None
    cur = None
    try:
        conn = dbapi.connect(
            address=HANA["host"],
            port=HANA["port"],
            user=HANA["user"],
            password=HANA["password"],
            encrypt=HANA["encrypt"],
            sslValidateCertificate=HANA["sslValidateCertificate"],
        )
        cur = conn.cursor()
        cur.execute(sql, [TARGET_DATE])
        rows = cur.fetchall()
        values = [r[0] for r in rows]
        save_json(out_path, values)
        log.info("Saved %d ItemCodes -> %s", len(values), out_path)
        return out_path
    finally:
        try:
            if cur is not None: cur.close()
        finally:
            if conn is not None: conn.close()
