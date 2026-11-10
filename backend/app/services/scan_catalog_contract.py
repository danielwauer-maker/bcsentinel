"""Pinned catalog inventory; not an attestation of actual BC execution."""
from functools import lru_cache
import json
from pathlib import Path

CHECK_MODULE_TO_RUN_MODULE = {
    "SYSTEM": "SYSTEM", "CUSTOMER": "FINANCE", "VENDOR": "FINANCE",
    "LEDGER": "FINANCE", "FINANCE": "FINANCE", "SALES": "SALES",
    "PURCHASE": "PURCHASING", "ITEM": "INVENTORY", "INVENTORY": "INVENTORY",
    "CRM": "CRM", "MANUFACTURING": "MANUFACTURING", "SERVICE": "SERVICE",
    "JOB": "JOBS", "HR": "HR",
}


@lru_cache(maxsize=1)
def catalog_1_0_2_57() -> tuple[str, str, frozenset[tuple[str, str]]]:
    path = Path(__file__).resolve().parents[1] / "data" / "scan_catalog_1_0_2_57.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    pairs = [(item["code"], item["module"]) for item in data["checks"]]
    if len(pairs) != 199 or len({code for code, _ in pairs}) != len(pairs):
        raise RuntimeError("The pinned BC scan catalog is incomplete or contains duplicates")
    return data["catalog_version"], data["methodology_version"], frozenset(pairs)
