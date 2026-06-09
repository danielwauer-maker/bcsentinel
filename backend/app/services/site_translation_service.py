from __future__ import annotations

import json
import os
import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LANDINGPAGE_DIR = REPO_ROOT / "landingpage"
LANDINGPAGE_DIR = DEFAULT_LANDINGPAGE_DIR
DE_TRANSLATIONS_PATH = DEFAULT_LANDINGPAGE_DIR / "lang" / "de.json"
EN_TRANSLATIONS_PATH = DEFAULT_LANDINGPAGE_DIR / "lang" / "en.json"

GROUP_ORDER = [
    "home",
    "help",
    "docs",
    "privacy",
    "terms",
    "support",
    "security",
    "billing",
    "contact",
    "impressum",
    "partner",
    "loss_examples",
    "common",
]

GROUP_LABELS = {
    "home": "Home / Landingpage",
    "help": "Help",
    "docs": "Docs",
    "privacy": "Privacy",
    "terms": "Terms / EULA",
    "support": "Support",
    "security": "Security",
    "billing": "Billing",
    "contact": "Contact",
    "impressum": "Impressum",
    "partner": "Partner",
    "loss_examples": "Loss Examples",
    "common": "Common / Shared",
}

COMMON_PREFIXES = (
    "brand_",
    "nav_",
    "footer_",
    "theme_",
    "cta_",
    "price_",
    "pricing_",
    "product_",
    "plan_",
    "faq_",
    "trust_",
    "mockup_",
    "status_",
    "error_",
    "success_",
    "cancel_",
    "save_",
)

PAGE_PREFIXES = {
    "help_": "help",
    "docs_": "docs",
    "privacy_": "privacy",
    "terms_": "terms",
    "support_": "support",
    "security_": "security",
    "billing_": "billing",
    "contact_": "contact",
    "impressum_": "impressum",
    "partner_": "partner",
    "partners_": "partner",
    "loss_": "loss_examples",
}

HOME_PREFIXES = (
    "hero_",
    "metric_",
    "problem_",
    "impact_",
    "demo_",
    "solution_",
    "how_",
    "step_",
    "value_",
    "security_card_",
)

ALLOWED_IDENTICAL_TEXTS = {
    "BCSentinel",
    "Business Central",
    "Deep Scan",
    "Quick Scan",
    "Data Health Score",
    "Dashboard",
    "Monitoring",
    "Assessment",
    "Validation Check",
    "Executive Report",
    "API Token",
    "API-Token",
    "FAQ",
    "CRM",
    "HR",
    "ROI",
    "EUR",
}

I18N_ATTR_RE = re.compile(r"""data-i18n(?:-[a-z-]+)?=["']([^"']+)["']""")


@dataclass(frozen=True)
class SiteTranslationRow:
    key: str
    de: str
    en: str
    status: str
    group: str


class SiteTranslationConfigError(ValueError):
    def __init__(self, message: str, *, details: dict[str, str | list[str]]):
        super().__init__(message)
        self.details = details


def _translations_dir() -> Path:
    configured = (os.getenv("SITE_TRANSLATIONS_PATH") or "").strip()
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path
    return DEFAULT_LANDINGPAGE_DIR / "lang"


def _translation_paths() -> tuple[Path, Path]:
    # Test suites may monkeypatch the historical path constants directly.
    if DE_TRANSLATIONS_PATH != DEFAULT_LANDINGPAGE_DIR / "lang" / "de.json":
        return DE_TRANSLATIONS_PATH, EN_TRANSLATIONS_PATH
    translations_dir = _translations_dir()
    return translations_dir / "de.json", translations_dir / "en.json"


def _landingpage_dir() -> Path:
    if LANDINGPAGE_DIR != DEFAULT_LANDINGPAGE_DIR:
        return LANDINGPAGE_DIR
    translations_dir = _translations_dir()
    if translations_dir.name == "lang":
        return translations_dir.parent
    return DEFAULT_LANDINGPAGE_DIR


def _ensure_translation_files() -> tuple[Path, Path]:
    de_path, en_path = _translation_paths()
    missing = [str(path) for path in (de_path, en_path) if not path.exists()]
    if missing:
        existing = [str(path) for path in (de_path, en_path) if path.exists()]
        raise SiteTranslationConfigError(
            "Landingpage translation files are not available.",
            details={
                "configured_path": str(_translations_dir()),
                "resolved_de_path": str(de_path),
                "resolved_en_path": str(en_path),
                "missing_files": missing,
                "existing_files": existing,
            },
        )
    return de_path, en_path


def load_site_translation_json(path: Path) -> OrderedDict[str, str]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
    except FileNotFoundError as exc:
        raise ValueError(f"Translation file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Translation file is not valid JSON: {path}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"Translation file must contain a JSON object: {path}")

    result: OrderedDict[str, str] = OrderedDict()
    for key, value in raw.items():
        normalized_key = str(key).strip()
        if not normalized_key:
            raise ValueError(f"Translation file contains an empty key: {path}")
        if not isinstance(value, str):
            raise ValueError(f"Translation value for {normalized_key} must be a string.")
        result[normalized_key] = value
    return result


def discover_landingpage_i18n_keys() -> set[str]:
    keys: set[str] = set()
    for path in _landingpage_dir().glob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        keys.update(match.strip() for match in I18N_ATTR_RE.findall(text) if match.strip())
    return keys


def ordered_translation_keys(
    de_translations: dict[str, str],
    en_translations: dict[str, str],
    discovered_keys: set[str],
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for source in (de_translations.keys(), en_translations.keys(), sorted(discovered_keys)):
        for key in source:
            if key not in seen:
                ordered.append(key)
                seen.add(key)
    return ordered


def group_translation_key(key: str) -> str:
    if key.startswith(COMMON_PREFIXES):
        return "common"
    for prefix, group in PAGE_PREFIXES.items():
        if key.startswith(prefix):
            return group
    if key.startswith(HOME_PREFIXES):
        return "home"
    return "common"


def _status_for_row(key: str, de_value: str, en_value: str) -> str:
    warnings: list[str] = []
    if not de_value.strip():
        warnings.append("DE fehlt")
    if not en_value.strip():
        warnings.append("EN fehlt")
    if (
        de_value.strip()
        and en_value.strip()
        and de_value.strip() == en_value.strip()
        and de_value.strip() not in ALLOWED_IDENTICAL_TEXTS
    ):
        warnings.append("DE/EN identisch pruefen")
    if not warnings:
        return "OK"
    return "; ".join(warnings)


def load_site_translation_groups() -> list[dict]:
    de_path, en_path = _ensure_translation_files()
    de_translations = load_site_translation_json(de_path)
    en_translations = load_site_translation_json(en_path)
    discovered_keys = discover_landingpage_i18n_keys()
    keys = ordered_translation_keys(de_translations, en_translations, discovered_keys)

    grouped: dict[str, list[SiteTranslationRow]] = {group: [] for group in GROUP_ORDER}
    for key in keys:
        de_value = de_translations.get(key, "")
        en_value = en_translations.get(key, "")
        group = group_translation_key(key)
        grouped[group].append(
            SiteTranslationRow(
                key=key,
                de=de_value,
                en=en_value,
                status=_status_for_row(key, de_value, en_value),
                group=group,
            )
        )

    return [
        {
            "key": group,
            "label": GROUP_LABELS[group],
            "rows": grouped[group],
        }
        for group in GROUP_ORDER
        if grouped[group] or group == "common"
    ]


def _write_translation_json(path: Path, values: OrderedDict[str, str]) -> None:
    encoded = json.dumps(values, ensure_ascii=False, indent=2)
    path.write_text(encoded + "\n", encoding="utf-8")


def update_site_translations(
    keys: list[str],
    de_values: list[str],
    en_values: list[str],
) -> dict:
    if not (len(keys) == len(de_values) == len(en_values)):
        raise ValueError("Translation form payload is incomplete.")

    de_path, en_path = _ensure_translation_files()
    current_de = load_site_translation_json(de_path)
    current_en = load_site_translation_json(en_path)
    allowed_keys = set(ordered_translation_keys(current_de, current_en, discover_landingpage_i18n_keys()))

    updates_de: OrderedDict[str, str] = OrderedDict()
    updates_en: OrderedDict[str, str] = OrderedDict()
    for idx, raw_key in enumerate(keys):
        key = (raw_key or "").strip()
        if not key:
            raise ValueError("Translation key must not be empty.")
        if key not in allowed_keys:
            raise ValueError(f"Unknown translation key: {key}")
        updates_de[key] = str(de_values[idx])
        updates_en[key] = str(en_values[idx])

    ordered_keys = ordered_translation_keys(current_de, current_en, set(updates_de.keys()) | set(updates_en.keys()))
    next_de: OrderedDict[str, str] = OrderedDict()
    next_en: OrderedDict[str, str] = OrderedDict()
    changed_keys: list[str] = []
    for key in ordered_keys:
        de_value = updates_de[key] if key in updates_de else current_de.get(key, "")
        en_value = updates_en[key] if key in updates_en else current_en.get(key, "")
        next_de[key] = de_value
        next_en[key] = en_value
        if current_de.get(key, "") != de_value or current_en.get(key, "") != en_value:
            changed_keys.append(key)

    _write_translation_json(de_path, next_de)
    _write_translation_json(en_path, next_en)

    # Parse again after writing so failed writes or invalid encoding cannot pass silently.
    load_site_translation_json(de_path)
    load_site_translation_json(en_path)

    return {
        "changed_count": len(changed_keys),
        "changed_keys": changed_keys,
    }
