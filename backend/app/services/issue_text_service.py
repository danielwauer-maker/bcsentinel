from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.check_catalog_service import resolve_check_text
from app.services.localization_service import normalize_language


@dataclass(frozen=True)
class IssueText:
    title: str
    recommendation: str


def issue_text(db: Session, issue_code: str, language: object | None) -> IssueText:
    resolved = resolve_check_text(db, issue_code, language)
    return IssueText(title=resolved.title, recommendation=resolved.recommendation)


def summary_headline(score: int, language: object | None) -> str:
    lang = normalize_language(language)
    if score >= 90:
        return "Gute Datenqualität mit einzelnen Lücken" if lang == "de" else "Good data quality with a few gaps"
    if score >= 75:
        return "Ordentliche Datenqualität mit erkennbarem Verbesserungspotenzial" if lang == "de" else "Sound data quality with clear room for improvement"
    return "Erhöhter Handlungsbedarf bei der Datenqualität" if lang == "de" else "Data quality requires increased attention"
