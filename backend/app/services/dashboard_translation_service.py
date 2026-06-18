from __future__ import annotations

import json
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_TRANSLATIONS_DIR = REPO_ROOT / "backend" / "app" / "translations" / "dashboard"

DASHBOARD_GROUP_ORDER = [
    "navigation",
    "overview",
    "analytics_scans",
    "issues_actions",
    "reports_subscription",
    "settings",
    "common",
]

DASHBOARD_GROUP_LABELS = {
    "navigation": "Navigation / Header / Footer",
    "overview": "Overview Dashboard",
    "analytics_scans": "Analytics / Scans",
    "issues_actions": "Issues / Actions",
    "reports_subscription": "Reports / Subscription",
    "settings": "Settings",
    "common": "Common / Empty States",
}

ALLOWED_IDENTICAL_DASHBOARD_TEXTS = {
    "BCSentinel",
    "Business Central",
    "BC",
    "CRM",
    "HR",
    "ROI",
    "EUR",
    "Monitoring",
    "Assessment",
    "Validation Check",
    "Full Analysis",
    "Free",
    "Settings",
    "Reports",
    "Actions",
    "Issues",
    "Analytics",
    "Subscription & Access",
}

DEFAULT_DASHBOARD_TRANSLATIONS = {
    "en": OrderedDict(
        [
            ("overview", "Overview"),
            ("analytics", "Analytics"),
            ("scans", "Scans"),
            ("issues", "Issues"),
            ("actions", "Actions"),
            ("reports", "Reports"),
            ("subscription", "Subscription"),
            ("settings", "Settings"),
            ("support", "Support"),
            ("documentation", "Documentation"),
            ("logout", "Logout"),
            ("language", "Language"),
            ("dark_mode", "Dark mode"),
            ("credits_needed", "Credits needed"),
            ("loading", "Loading..."),
            ("last_updated", "Last updated"),
            ("overview_subtitle", "Executive overview of your data quality and business impact"),
            ("analytics_subtitle", "Score, loss and distribution analysis for the selected scan"),
            ("scans_subtitle", "Available scan runs and dashboard context"),
            ("issues_subtitle", "Review detected data quality issues, business impact and affected records."),
            ("issue_detail", "Issue detail"),
            ("issue_detail_subtitle", "Detailed issue context, impact and recommendation"),
            ("actions_subtitle", "Prioritized actions to reduce data quality risk and business impact."),
            ("reports_subtitle", "Generate and review executive, operational and impact reports."),
            ("subscription_access", "Subscription & Access"),
            ("subscription_subtitle", "Manage your product access, monitoring status and available scan credits."),
            ("settings_subtitle", "Configure your account and preferences"),
            ("health_score", "Health Score"),
            ("estimated_annual_loss", "Estimated Annual Loss"),
            ("potential_savings", "Potential Savings"),
            ("scanned_records", "Scanned records"),
            ("checks_run", "Checks run"),
            ("module_scores", "Data Scores by BC module"),
            ("module_scores_helper", "Score per module - 0 to 100"),
            ("issues_by_module", "Issues by BC module"),
            ("issues_by_module_helper", "Affected findings per module"),
            ("recent_scans", "Recent Scans"),
            ("recent_scans_helper", "Click a scan to load it"),
            ("score_trend", "Score Trend"),
            ("score_trend_helper", "History of selected scans"),
            ("loss_trend", "Loss Trend"),
            ("loss_trend_helper", "Estimated annual impact"),
            ("paid_scan_access", "Full Analysis access"),
            ("scan_preview", "Scan preview"),
            ("scan_preview_helper", "Record details, recommendations, actions"),
            ("estimated_monitoring_pricing", "Estimated monitoring pricing"),
            ("findings", "Findings"),
            ("findings_helper", "Visible with paid scan access, actionable in Business Central"),
            ("paid_access", "Paid Access"),
            ("open_in_bc", "Open in BC"),
            ("preview_after_scan", "The paid scan preview will appear after the next scan."),
            ("recommendations_available", "Recommendations available"),
            ("affected", "affected"),
            ("monitoring_active", "Monitoring active"),
            ("assessment_validation_active", "Full Analysis / Validation active"),
            ("assessment_needed", "Full Analysis needed"),
            ("buy_assessment", "Buy Full Analysis"),
            ("start_monitoring", "Start Monitoring"),
            ("buy_more_credits", "Buy More Credits"),
            ("manage_subscription", "Manage subscription"),
            ("static_active_issues", "Active Issues"),
            ("static_recent_critical_issues", "Recent Critical Issues"),
            ("static_recent_critical_helper", "Highest impact findings from the selected scan"),
            ("static_recommended_actions", "Recommended Actions"),
            ("static_recommended_actions_helper", "Highest impact actions based on the selected scan."),
            ("static_module_distribution_records", "Module Distribution & Records"),
            ("static_issue_distribution_percent", "Issue Distribution (by %)"),
            ("static_records_by_module", "Records by Module"),
            ("static_business_impact_breakdown", "Business Impact Breakdown"),
            ("static_view_all_issues", "View all issues"),
            ("static_view_all_modules", "View all modules"),
            ("static_view_full_impact_report", "View full impact report"),
            ("static_unlock_next_step", "Unlock the next step"),
            ("static_unlock_next_step_helper", "Choose the access level that matches what you want to do next."),
            ("static_feature_comparison", "Feature Comparison"),
            ("static_feature_comparison_helper", "Free Score, paid scan access and Monitoring at a glance."),
            ("static_feature", "Feature"),
            ("static_free", "Free"),
            ("full_analysis", "Full Analysis"),
            ("validation_check", "Validation Check"),
            ("monitoring", "Monitoring"),
            ("static_validation", "Validation"),
            ("static_assessment", "Assessment"),
            ("static_date", "Date"),
            ("static_type", "Type"),
            ("static_score", "Score"),
            ("static_status", "Status"),
            ("static_headline", "Headline"),
            ("static_back_to_issues", "Back to Issues"),
            ("static_issue_detail_empty", "Issue detail is available from the Issues page."),
            ("static_current_access", "Current Access"),
            ("static_monitoring_status", "Monitoring Status"),
            ("static_scan_credits", "Scan Credits"),
            ("static_available_scan_credits", "Available Scan Credits"),
            ("static_products", "Products"),
            ("static_issue_code", "Issue Code"),
            ("static_module_category", "Module / Category"),
            ("static_general", "General"),
            ("static_open", "Open"),
            ("static_locked", "Locked"),
            ("static_not_available", "Not available"),
            ("static_not_calculated_yet", "Not calculated yet"),
            ("static_affected_records", "Affected Records"),
            ("static_estimated_impact_loss", "Estimated Impact / Loss"),
            ("static_last_scan_updated", "Last Scan / Last Updated"),
            ("static_estimated_loss", "Estimated Loss"),
            ("static_potential_savings", "Potential Savings"),
            ("static_unlock_issue_details", "Unlock full issue details"),
            ("static_bc_link_unavailable", "Business Central link not available"),
            ("static_locked_access", "Locked access"),
            ("static_full_issue_access", "Full issue access"),
            ("static_no_scan_timestamp", "No scan timestamp"),
            ("static_saving_pending", "Saving pending"),
            ("static_full_action_access", "Full action access"),
            ("static_high_priority", "High Priority"),
            ("static_open_actions", "Open Actions"),
            ("static_prioritized_recommendations", "Prioritized recommendations"),
            ("static_critical_high_priority", "Critical and high priority"),
            ("static_potential_saving", "Potential Saving"),
            ("static_executive_summary", "Executive Summary"),
            ("static_data_quality_report", "Data Quality Report"),
            ("static_issue_detail_report", "Issue Detail Report"),
            ("static_business_impact_report", "Business Impact Report"),
            ("static_action_plan_report", "Action Plan Report"),
            ("static_trend_report", "Trend Report"),
            ("static_after_scan", "After scan"),
            ("static_available_after_scan", "Available after scan"),
            ("static_unlock_reports", "Unlock reports"),
            ("static_monitoring_only", "Monitoring only"),
            ("static_available", "Available"),
            ("static_current_plan", "Current Plan"),
            ("static_product_access", "Product Access"),
            ("static_dashboard_access", "Dashboard Access"),
            ("static_issue_access", "Issue Access"),
            ("static_active", "Active"),
            ("static_inactive", "Inactive"),
            ("static_expired", "Expired"),
            ("static_trial", "Trial"),
            ("static_renewal_date", "Renewal Date"),
            ("static_period_end", "Period End"),
            ("static_yes", "Yes"),
            ("static_no", "No"),
            ("static_buy_now", "Buy Now"),
            ("static_contact_sales", "Contact Sales"),
            ("static_company_tenant", "Company & Tenant"),
            ("static_language_localization", "Language & Localization"),
            ("static_dashboard_preferences", "Dashboard Preferences"),
            ("static_contact", "Contact"),
            ("static_notification_settings", "Notification Settings"),
            ("severity_critical", "Critical"),
            ("severity_high", "High"),
            ("severity_medium", "Medium"),
            ("severity_low", "Low"),
            ("severity_unknown", "Unknown"),
            ("active_critical_issues", "Critical Issues"),
            ("active_high_issues", "High Issues"),
            ("active_medium_issues", "Medium Issues"),
            ("active_low_issues", "Low Issues"),
        ]
    ),
    "de": OrderedDict(
        [
            ("overview", "Überblick"),
            ("analytics", "Analytics"),
            ("scans", "Scans"),
            ("issues", "Issues"),
            ("actions", "Actions"),
            ("reports", "Reports"),
            ("subscription", "Produktzugriff"),
            ("settings", "Settings"),
            ("support", "Support"),
            ("documentation", "Dokumentation"),
            ("logout", "Logout"),
            ("language", "Sprache"),
            ("dark_mode", "Dark Mode"),
            ("credits_needed", "Credits benötigt"),
            ("loading", "Wird geladen..."),
            ("last_updated", "Zuletzt aktualisiert"),
            ("overview_subtitle", "Executive Overview deiner Datenqualität und Business-Auswirkung"),
            ("analytics_subtitle", "Score-, Verlust- und Verteilungsanalyse für den ausgewählten Scan"),
            ("scans_subtitle", "Verfügbare Scan-Läufe und Dashboard-Kontext"),
            ("issues_subtitle", "Prüfe erkannte Datenqualitäts-Issues, Business Impact und betroffene Datensätze."),
            ("issue_detail", "Issue Detail"),
            ("issue_detail_subtitle", "Detaillierter Issue-Kontext, Impact und Empfehlung"),
            ("actions_subtitle", "Priorisierte Aktionen zur Reduzierung von Datenqualitätsrisiko und Business Impact."),
            ("reports_subtitle", "Reports erstellen und Executive-, Operational- und Impact-Auswertungen prüfen."),
            ("subscription_access", "Subscription & Access"),
            ("subscription_subtitle", "Verwalte Produktzugriff, Monitoring-Status und verfügbare Scan Credits."),
            ("settings_subtitle", "Account und Präferenzen konfigurieren"),
            ("health_score", "Health Score"),
            ("estimated_annual_loss", "Geschätzter Jahresverlust"),
            ("potential_savings", "Potenzielle Einsparungen"),
            ("scanned_records", "Gescannte Datensätze"),
            ("checks_run", "Geprüfte Checks"),
            ("module_scores", "Data Scores nach BC-Modul"),
            ("module_scores_helper", "Score je Modul - 0 bis 100"),
            ("issues_by_module", "Issues nach BC-Modul"),
            ("issues_by_module_helper", "Betroffene Findings je Modul"),
            ("recent_scans", "Letzte Scans"),
            ("recent_scans_helper", "Scan anklicken, um ihn zu laden"),
            ("score_trend", "Score-Trend"),
            ("score_trend_helper", "Historie der ausgewählten Scans"),
            ("loss_trend", "Verlust-Trend"),
            ("loss_trend_helper", "Geschätzter Jahresimpact"),
            ("paid_scan_access", "Full-Analysis-Zugriff"),
            ("scan_preview", "Scan-Vorschau"),
            ("scan_preview_helper", "Datensätze, Empfehlungen, Aktionen"),
            ("estimated_monitoring_pricing", "Geschätzter Monitoring-Preis"),
            ("findings", "Findings"),
            ("findings_helper", "Sichtbar mit bezahltem Scan-Zugriff, umsetzbar in Business Central"),
            ("paid_access", "Bezahlter Zugriff"),
            ("open_in_bc", "In BC öffnen"),
            ("preview_after_scan", "Die bezahlte Scan-Vorschau erscheint nach dem nächsten Scan."),
            ("recommendations_available", "Empfehlungen verfügbar"),
            ("affected", "betroffen"),
            ("monitoring_active", "Monitoring aktiv"),
            ("assessment_validation_active", "Full Analysis / Validation aktiv"),
            ("assessment_needed", "Full Analysis benötigt"),
            ("buy_assessment", "Full Analysis kaufen"),
            ("start_monitoring", "Monitoring starten"),
            ("buy_more_credits", "Weitere Credits kaufen"),
            ("manage_subscription", "Abo verwalten"),
            ("static_active_issues", "Aktive Issues"),
            ("static_recent_critical_issues", "Aktuelle kritische Issues"),
            ("static_recent_critical_helper", "Findings mit höchstem Impact aus dem ausgewählten Scan"),
            ("static_recommended_actions", "Empfohlene Aktionen"),
            ("static_recommended_actions_helper", "Aktionen mit höchstem Impact basierend auf dem ausgewählten Scan."),
            ("static_module_distribution_records", "Modulverteilung & Datensätze"),
            ("static_issue_distribution_percent", "Issue-Verteilung (in %)"),
            ("static_records_by_module", "Datensätze nach Modul"),
            ("static_business_impact_breakdown", "Business Impact Aufschlüsselung"),
            ("static_view_all_issues", "Alle Issues anzeigen"),
            ("static_view_all_modules", "Alle Module anzeigen"),
            ("static_view_full_impact_report", "Vollständigen Impact Report anzeigen"),
            ("static_unlock_next_step", "Nächsten Schritt freischalten"),
            ("static_unlock_next_step_helper", "Wähle den Zugriff, der zu deinem nächsten Schritt passt."),
            ("static_feature_comparison", "Feature-Vergleich"),
            ("static_feature_comparison_helper", "Free Score, bezahlter Scan-Zugriff und Monitoring auf einen Blick."),
            ("static_feature", "Feature"),
            ("static_free", "Free"),
            ("full_analysis", "Full Analysis"),
            ("validation_check", "Validation Check"),
            ("monitoring", "Monitoring"),
            ("static_validation", "Validation"),
            ("static_assessment", "Assessment"),
            ("static_date", "Datum"),
            ("static_type", "Typ"),
            ("static_score", "Score"),
            ("static_status", "Status"),
            ("static_headline", "Headline"),
            ("static_back_to_issues", "Zurück zu Issues"),
            ("static_issue_detail_empty", "Issue Details sind über die Issues-Seite verfügbar."),
            ("static_current_access", "Aktueller Zugriff"),
            ("static_monitoring_status", "Monitoring-Status"),
            ("static_scan_credits", "Scan Credits"),
            ("static_available_scan_credits", "Verfügbare Scan Credits"),
            ("static_products", "Produkte"),
            ("static_issue_code", "Issue-Code"),
            ("static_module_category", "Modul / Kategorie"),
            ("static_general", "Allgemein"),
            ("static_open", "Offen"),
            ("static_locked", "Gesperrt"),
            ("static_not_available", "Nicht verfügbar"),
            ("static_not_calculated_yet", "Noch nicht berechnet"),
            ("static_affected_records", "Betroffene Datensätze"),
            ("static_estimated_impact_loss", "Geschätzter Impact / Verlust"),
            ("static_last_scan_updated", "Letzter Scan / Letzte Aktualisierung"),
            ("static_estimated_loss", "Geschätzter Verlust"),
            ("static_potential_savings", "Potenzielle Einsparungen"),
            ("static_unlock_issue_details", "Issue Details freischalten"),
            ("static_bc_link_unavailable", "Business-Central-Link nicht verfügbar"),
            ("static_locked_access", "Gesperrter Zugriff"),
            ("static_full_issue_access", "Voller Issue-Zugriff"),
            ("static_no_scan_timestamp", "Kein Scan-Zeitpunkt"),
            ("static_saving_pending", "Einsparung ausstehend"),
            ("static_full_action_access", "Voller Actions-Zugriff"),
            ("static_high_priority", "Hohe Priorität"),
            ("static_open_actions", "Offene Aktionen"),
            ("static_prioritized_recommendations", "Priorisierte Empfehlungen"),
            ("static_critical_high_priority", "Kritische und hohe Priorität"),
            ("static_potential_saving", "Potenzielle Einsparung"),
            ("static_executive_summary", "Executive Summary"),
            ("static_data_quality_report", "Data Quality Report"),
            ("static_issue_detail_report", "Issue Detail Report"),
            ("static_business_impact_report", "Business Impact Report"),
            ("static_action_plan_report", "Action Plan Report"),
            ("static_trend_report", "Trend Report"),
            ("static_after_scan", "Nach Scan"),
            ("static_available_after_scan", "Nach Scan verfügbar"),
            ("static_unlock_reports", "Reports freischalten"),
            ("static_monitoring_only", "Nur Monitoring"),
            ("static_available", "Verfügbar"),
            ("static_current_plan", "Aktueller Plan"),
            ("static_product_access", "Produktzugriff"),
            ("static_dashboard_access", "Dashboard-Zugriff"),
            ("static_issue_access", "Issue-Zugriff"),
            ("static_active", "Aktiv"),
            ("static_inactive", "Inaktiv"),
            ("static_expired", "Abgelaufen"),
            ("static_trial", "Testphase"),
            ("static_renewal_date", "Verlängerungsdatum"),
            ("static_period_end", "Periodenende"),
            ("static_yes", "Ja"),
            ("static_no", "Nein"),
            ("static_buy_now", "Jetzt kaufen"),
            ("static_contact_sales", "Sales kontaktieren"),
            ("static_company_tenant", "Unternehmen & Tenant"),
            ("static_language_localization", "Sprache & Lokalisierung"),
            ("static_dashboard_preferences", "Dashboard-Präferenzen"),
            ("static_contact", "Kontakt"),
            ("static_notification_settings", "Benachrichtigungseinstellungen"),
            ("severity_critical", "Kritisch"),
            ("severity_high", "Hoch"),
            ("severity_medium", "Mittel"),
            ("severity_low", "Niedrig"),
            ("severity_unknown", "Unbekannt"),
            ("active_critical_issues", "Kritische Issues"),
            ("active_high_issues", "Hohe Issues"),
            ("active_medium_issues", "Mittlere Issues"),
            ("active_low_issues", "Niedrige Issues"),
        ]
    ),
}


@dataclass(frozen=True)
class DashboardTranslationRow:
    key: str
    de: str
    en: str
    status: str
    group: str


def _dashboard_translation_paths() -> tuple[Path, Path]:
    return DASHBOARD_TRANSLATIONS_DIR / "de.json", DASHBOARD_TRANSLATIONS_DIR / "en.json"


def _write_json(path: Path, values: OrderedDict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(values, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_json(path: Path, defaults: OrderedDict[str, str]) -> OrderedDict[str, str]:
    if not path.exists():
        _write_json(path, defaults)
        return OrderedDict(defaults)
    raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
    if not isinstance(raw, dict):
        raise ValueError(f"Dashboard translation file must contain an object: {path}")
    merged = OrderedDict(defaults)
    for key, value in raw.items():
        if key in merged and isinstance(value, str):
            merged[key] = value
    return merged


def load_dashboard_translation_json(language: str) -> OrderedDict[str, str]:
    de_path, en_path = _dashboard_translation_paths()
    if language == "de":
        return _load_json(de_path, DEFAULT_DASHBOARD_TRANSLATIONS["de"])
    return _load_json(en_path, DEFAULT_DASHBOARD_TRANSLATIONS["en"])


def dashboard_ui_translations(language: str) -> dict[str, str]:
    return dict(load_dashboard_translation_json("de" if language == "de" else "en"))


def _group_key(key: str) -> str:
    if key in {"overview", "analytics", "scans", "issues", "actions", "reports", "subscription", "settings", "support", "documentation", "logout", "language", "dark_mode"}:
        return "navigation"
    if key.startswith(("static_active_", "static_recent_", "static_recommended_", "static_module_", "static_issue_", "static_records_", "static_business_", "static_view_", "static_unlock_", "static_feature_", "active_", "health_", "estimated_", "potential_", "scanned_", "checks_", "module_")):
        return "overview"
    if key.startswith(("score_trend", "loss_trend", "recent_scans", "scan_", "issues_by_module")):
        return "analytics_scans"
    if key.startswith(("issue", "severity_", "findings", "actions", "open_in_bc", "paid_access", "affected")):
        return "issues_actions"
    if key.startswith(("reports", "subscription", "monitoring", "assessment", "buy_", "start_", "manage_", "paid_scan", "estimated_monitoring", "preview_", "recommendations_")):
        return "reports_subscription"
    if key.startswith(("settings",)):
        return "settings"
    return "common"


def _status(key: str, de_value: str, en_value: str) -> str:
    warnings: list[str] = []
    if not de_value.strip():
        warnings.append("DE fehlt")
    if not en_value.strip():
        warnings.append("EN fehlt")
    if de_value.strip() and en_value.strip() and de_value.strip() == en_value.strip() and de_value.strip() not in ALLOWED_IDENTICAL_DASHBOARD_TEXTS:
        warnings.append("DE/EN identisch pruefen")
    return "OK" if not warnings else "; ".join(warnings)


def load_dashboard_translation_groups() -> list[dict]:
    de_values = load_dashboard_translation_json("de")
    en_values = load_dashboard_translation_json("en")
    grouped: dict[str, list[DashboardTranslationRow]] = {group: [] for group in DASHBOARD_GROUP_ORDER}
    for key in DEFAULT_DASHBOARD_TRANSLATIONS["en"].keys():
        group = _group_key(key)
        de_value = de_values.get(key, "")
        en_value = en_values.get(key, "")
        grouped[group].append(
            DashboardTranslationRow(
                key=key,
                de=de_value,
                en=en_value,
                status=_status(key, de_value, en_value),
                group=group,
            )
        )

    result: list[dict] = []
    for group in DASHBOARD_GROUP_ORDER:
        rows = grouped[group]
        missing_count = sum(1 for row in rows if not row.de.strip() or not row.en.strip())
        warning_count = sum(1 for row in rows if row.status != "OK")
        result.append(
            {
                "key": group,
                "label": DASHBOARD_GROUP_LABELS[group],
                "rows": rows,
                "key_count": len(rows),
                "missing_count": missing_count,
                "warning_count": warning_count,
            }
        )
    return result


def update_dashboard_translations(keys: list[str], de_values: list[str], en_values: list[str]) -> dict:
    if not (len(keys) == len(de_values) == len(en_values)):
        raise ValueError("Translation form payload is incomplete.")

    allowed_keys = set(DEFAULT_DASHBOARD_TRANSLATIONS["en"].keys())
    current_de = load_dashboard_translation_json("de")
    current_en = load_dashboard_translation_json("en")
    next_de = OrderedDict(current_de)
    next_en = OrderedDict(current_en)
    changed_keys: list[str] = []

    for idx, raw_key in enumerate(keys):
        key = (raw_key or "").strip()
        if key not in allowed_keys:
            raise ValueError(f"Unknown dashboard translation key: {key}")
        de_value = str(de_values[idx])
        en_value = str(en_values[idx])
        if next_de.get(key, "") != de_value or next_en.get(key, "") != en_value:
            changed_keys.append(key)
        next_de[key] = de_value
        next_en[key] = en_value

    de_path, en_path = _dashboard_translation_paths()
    _write_json(de_path, next_de)
    _write_json(en_path, next_en)
    return {"changed_count": len(changed_keys), "changed_keys": changed_keys}
