from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import CheckDefinition, CheckTranslation


DEFAULT_LANGUAGE_CODE = "de-DE"
SECONDARY_LANGUAGE_CODE = "en-US"
REQUIRED_LANGUAGE_CODES = (DEFAULT_LANGUAGE_CODE, SECONDARY_LANGUAGE_CODE)
_LANGUAGE_CODE_PATTERN = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
_DEFAULTS_PATH = Path(__file__).resolve().parents[1] / "data" / "check_catalog_defaults.json"


class CheckCatalogValidationError(ValueError):
    pass


@dataclass(frozen=True)
class CheckText:
    check_id: str
    language_code: str
    title: str
    short_description: str
    recommendation: str


def canonicalize_language_code(value: object | None) -> str:
    raw = str(value or "").strip().replace("_", "-")
    if not raw:
        return SECONDARY_LANGUAGE_CODE
    if raw.lower() == "de":
        return DEFAULT_LANGUAGE_CODE
    if raw.lower() == "en":
        return SECONDARY_LANGUAGE_CODE
    if not _LANGUAGE_CODE_PATTERN.fullmatch(raw):
        raise CheckCatalogValidationError(f"Invalid language code: {raw}")
    parts = raw.split("-")
    normalized = [parts[0].lower()]
    for part in parts[1:]:
        normalized.append(part.upper() if len(part) in {2, 3} else part.title())
    return "-".join(normalized)


@lru_cache(maxsize=1)
def load_default_catalog() -> tuple[dict, ...]:
    payload = json.loads(_DEFAULTS_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise CheckCatalogValidationError("The default check catalog must be a JSON array.")
    validate_default_catalog(payload)
    return tuple(payload)


def validate_default_catalog(payload: list[dict] | tuple[dict, ...]) -> None:
    seen_ids: set[str] = set()
    errors: list[str] = []
    for item in payload:
        check_id = str(item.get("check_id") or "").strip()
        if not check_id:
            errors.append("A check is missing its check_id.")
            continue
        if check_id in seen_ids:
            errors.append(f"Duplicate check ID: {check_id}")
        seen_ids.add(check_id)
        if not str(item.get("module") or "").strip():
            errors.append(f"{check_id}: module is empty.")
        if not str(item.get("severity") or "").strip():
            errors.append(f"{check_id}: severity is empty.")
        translations = item.get("translations") or {}
        for language_code in REQUIRED_LANGUAGE_CODES:
            translation = translations.get(language_code)
            if not isinstance(translation, dict):
                errors.append(f"{check_id}: missing {language_code} translation.")
                continue
            for field in ("title", "short_description", "recommendation"):
                if not str(translation.get(field) or "").strip():
                    errors.append(f"{check_id}/{language_code}: {field} is empty.")
        for language_code in translations:
            try:
                canonicalize_language_code(language_code)
            except CheckCatalogValidationError as exc:
                errors.append(f"{check_id}: {exc}")
    if errors:
        raise CheckCatalogValidationError("\n".join(errors))


def _default_by_id(check_id: str) -> dict | None:
    return next((item for item in load_default_catalog() if item["check_id"] == check_id), None)


def ensure_default_check_catalog(db: Session) -> dict[str, int]:
    inserted_checks = inserted_translations = updated_system_translations = 0
    existing_checks = {
        row.check_id: row
        for row in db.scalars(
            select(CheckDefinition).options(selectinload(CheckDefinition.translations))
        ).all()
    }
    for default in load_default_catalog():
        check_id = default["check_id"]
        check = existing_checks.get(check_id)
        if check is None:
            check = CheckDefinition(
                check_id=check_id,
                module=default["module"],
                severity=default["severity"],
            )
            db.add(check)
            existing_checks[check_id] = check
            inserted_checks += 1
        else:
            check.module = default["module"]
            check.severity = default["severity"]

        translations = {row.language_code: row for row in check.translations}
        for language_code, standard in default["translations"].items():
            translation = translations.get(language_code)
            if translation is None:
                db.add(
                    CheckTranslation(
                        check_id=check_id,
                        language_code=language_code,
                        title=standard["title"].strip(),
                        short_description=standard["short_description"].strip(),
                        recommendation=standard["recommendation"].strip(),
                        is_customized=False,
                    )
                )
                inserted_translations += 1
            elif not translation.is_customized:
                standard_values = (
                    standard["title"].strip(),
                    standard["short_description"].strip(),
                    standard["recommendation"].strip(),
                )
                current_values = (
                    translation.title,
                    translation.short_description,
                    translation.recommendation,
                )
                if current_values != standard_values:
                    translation.title, translation.short_description, translation.recommendation = standard_values
                    translation.updated_at_utc = datetime.now(timezone.utc)
                    updated_system_translations += 1
    db.flush()
    return {
        "inserted_checks": inserted_checks,
        "inserted_translations": inserted_translations,
        "updated_system_translations": updated_system_translations,
    }


def _resolve_from_rows(check_id: str, requested: str, rows: list[CheckTranslation]) -> CheckText:
    by_language = {row.language_code: row for row in rows}
    candidates = tuple(dict.fromkeys((requested, DEFAULT_LANGUAGE_CODE, SECONDARY_LANGUAGE_CODE)))

    def resolve_field(field: str) -> tuple[str, str]:
        for language_code in candidates:
            row = by_language.get(language_code)
            value = str(getattr(row, field, "") or "").strip() if row else ""
            if value:
                return value, language_code
        return check_id, "technical"

    title, resolved_language = resolve_field("title")
    short_description, _ = resolve_field("short_description")
    recommendation, _ = resolve_field("recommendation")
    return CheckText(check_id, resolved_language, title, short_description, recommendation)


def resolve_check_texts(
    db: Session,
    check_ids: list[str] | tuple[str, ...] | set[str],
    language: object | None,
) -> dict[str, CheckText]:
    requested = canonicalize_language_code(language)
    unique_ids = tuple(dict.fromkeys(str(check_id) for check_id in check_ids if str(check_id)))
    if not unique_ids:
        return {}
    rows = db.scalars(
        select(CheckTranslation).where(CheckTranslation.check_id.in_(unique_ids))
    ).all()
    grouped: dict[str, list[CheckTranslation]] = {check_id: [] for check_id in unique_ids}
    for row in rows:
        grouped.setdefault(row.check_id, []).append(row)
    return {
        check_id: _resolve_from_rows(check_id, requested, grouped.get(check_id, []))
        for check_id in unique_ids
    }


def resolve_check_text(db: Session, check_id: str, language: object | None) -> CheckText:
    return resolve_check_texts(db, [check_id], language)[check_id]


def update_check_translation(
    db: Session,
    check_id: str,
    language_code: object,
    *,
    title: str,
    short_description: str,
    recommendation: str,
) -> CheckTranslation:
    language = canonicalize_language_code(language_code)
    values = {
        "title": str(title or "").strip(),
        "short_description": str(short_description or "").strip(),
        "recommendation": str(recommendation or "").strip(),
    }
    empty_fields = [name for name, value in values.items() if not value]
    if empty_fields:
        raise CheckCatalogValidationError(
            f"Title, short description and recommendation are required ({', '.join(empty_fields)})."
        )
    check = db.get(CheckDefinition, check_id)
    if check is None:
        raise CheckCatalogValidationError(f"Unknown check ID: {check_id}")
    translation = db.get(CheckTranslation, (check_id, language))
    if translation is None:
        translation = CheckTranslation(check_id=check_id, language_code=language, **values)
        db.add(translation)
    else:
        translation.title = values["title"]
        translation.short_description = values["short_description"]
        translation.recommendation = values["recommendation"]
    translation.is_customized = True
    translation.updated_at_utc = datetime.now(timezone.utc)
    db.flush()
    return translation


def restore_standard_texts(db: Session, check_id: str | None = None) -> int:
    defaults = load_default_catalog()
    if check_id is not None:
        default = _default_by_id(check_id)
        if default is None:
            raise CheckCatalogValidationError(f"Unknown check ID: {check_id}")
        defaults = (default,)
    restored = 0
    for default in defaults:
        for language_code, standard in default["translations"].items():
            translation = db.get(CheckTranslation, (default["check_id"], language_code))
            if translation is None:
                translation = CheckTranslation(
                    check_id=default["check_id"],
                    language_code=language_code,
                )
                db.add(translation)
            translation.title = standard["title"].strip()
            translation.short_description = standard["short_description"].strip()
            translation.recommendation = standard["recommendation"].strip()
            translation.is_customized = False
            translation.updated_at_utc = datetime.now(timezone.utc)
            restored += 1
    db.flush()
    return restored
