from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Scan, ScanIssueRecord, Tenant
from app.schemas.monitoring_report import (
    MonitoringBusinessAreaTrend,
    MonitoringCoverage,
    MonitoringFindingLifecycle,
    MonitoringReport,
    MonitoringTrendPoint,
)
from app.services.localization_service import tenant_language
from app.services.product_license_service import build_product_access_snapshot
from app.services.quick_finding_selection_service import normalize_severity

MAX_MONITORING_SCANS = 12
SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
BUSINESS_AREAS = (
    "Finance",
    "Sales",
    "Purchasing",
    "Inventory",
    "CRM",
    "Manufacturing",
    "Service",
    "Jobs",
    "HR",
    "System",
)
BUSINESS_AREA_SCORE_ATTRS = {
    "Finance": "finance_score",
    "Sales": "sales_score",
    "Purchasing": "purchasing_score",
    "Inventory": "inventory_score",
    "CRM": "crm_score",
    "Manufacturing": "manufacturing_score",
    "Service": "service_score",
    "Jobs": "jobs_score",
    "HR": "hr_score",
    "System": "system_score",
}
BUSINESS_AREA_LABELS_DE = {
    "Finance": "Finanzen",
    "Sales": "Verkauf",
    "Purchasing": "Einkauf",
    "Inventory": "Lager & Artikel",
    "CRM": "CRM & Stammdaten",
    "Manufacturing": "Produktion",
    "Service": "Service",
    "Jobs": "Projekte",
    "HR": "Personal",
    "System": "System & Plattform",
}


def _safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: object) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_category(value: str | None, code: str | None = None) -> str:
    raw = str(value or "").strip().lower()
    code_upper = str(code or "").upper()
    mapping = {
        "finance": "Finance",
        "sales": "Sales",
        "sale": "Sales",
        "purchase": "Purchasing",
        "purchasing": "Purchasing",
        "inventory": "Inventory",
        "item": "Inventory",
        "crm": "CRM",
        "customer": "CRM",
        "vendor": "Purchasing",
        "manufacturing": "Manufacturing",
        "service": "Service",
        "jobs": "Jobs",
        "job": "Jobs",
        "hr": "HR",
        "system": "System",
    }
    if raw in mapping:
        return mapping[raw]
    if code_upper.startswith(("CUSTOMER", "CUSTOMERS")):
        return "CRM"
    if code_upper.startswith(("VENDOR", "VENDORS", "PURCHASE", "PURCH")):
        return "Purchasing"
    if code_upper.startswith(("ITEM", "ITEMS", "INVENTORY", "WAREHOUSE", "VALUE")):
        return "Inventory"
    if code_upper.startswith(("SALE", "SALES")):
        return "Sales"
    if "LEDGER" in code_upper or code_upper.startswith(("GL_", "G_L_")):
        return "Finance"
    return "System"


def _area_label(area: str, language: str) -> str:
    if language == "de":
        return BUSINESS_AREA_LABELS_DE.get(area, BUSINESS_AREA_LABELS_DE["System"])
    return area if area in BUSINESS_AREAS else "System"


def _affected_records(issues: list[ScanIssueRecord]) -> int:
    return sum(max(0, _safe_int(issue.affected_count)) for issue in issues)


def _impact(issues: list[ScanIssueRecord]) -> float:
    return round(sum(max(0.0, _safe_float(issue.estimated_impact_eur)) for issue in issues), 2)


def _load_scans(db: Session, tenant: Tenant, current_scan_id: str | None) -> list[Scan]:
    base_filters = [Scan.tenant_id == tenant.tenant_id, Scan.scan_type != "quick"]
    if current_scan_id:
        current = db.scalar(
            select(Scan).where(
                Scan.tenant_id == tenant.tenant_id,
                Scan.scan_id == current_scan_id,
            )
        )
        if current is None:
            raise HTTPException(status_code=404, detail="Monitoring report scan not found.")
        if (current.scan_type or "").strip().lower() == "quick":
            raise HTTPException(status_code=409, detail="Monitoring reports use deep-scan history; Quick scans are excluded.")
        rows = db.scalars(
            select(Scan)
            .where(
                *base_filters,
                or_(
                    Scan.generated_at_utc < current.generated_at_utc,
                    and_(Scan.generated_at_utc == current.generated_at_utc, Scan.id <= current.id),
                ),
            )
            .order_by(Scan.generated_at_utc.desc(), Scan.id.desc())
            .limit(MAX_MONITORING_SCANS)
        ).all()
    else:
        rows = db.scalars(
            select(Scan)
            .where(*base_filters)
            .order_by(Scan.generated_at_utc.desc(), Scan.id.desc())
            .limit(MAX_MONITORING_SCANS)
        ).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Monitoring report requires at least one completed deep scan.")
    return list(reversed(rows))


def _issue_maps(db: Session, scan_ids: list[str]) -> dict[str, dict[str, ScanIssueRecord]]:
    result: dict[str, dict[str, ScanIssueRecord]] = {scan_id: {} for scan_id in scan_ids}
    if not scan_ids:
        return result
    rows = db.scalars(
        select(ScanIssueRecord)
        .where(ScanIssueRecord.scan_id.in_(scan_ids))
        .order_by(ScanIssueRecord.scan_id.asc(), ScanIssueRecord.code.asc())
    ).all()
    for row in rows:
        result.setdefault(row.scan_id, {})[row.code] = row
    return result


def _trend_points(scans: list[Scan], issues_by_scan: dict[str, dict[str, ScanIssueRecord]]) -> list[MonitoringTrendPoint]:
    points: list[MonitoringTrendPoint] = []
    for scan in scans:
        issues = list(issues_by_scan.get(scan.scan_id, {}).values())
        points.append(
            MonitoringTrendPoint(
                scan_id=scan.scan_id,
                generated_at_utc=scan.generated_at_utc,
                data_health_score=max(0, min(100, _safe_int(scan.data_score))),
                findings_count=len(issues),
                affected_records=_affected_records(issues),
                modeled_business_impact_eur=_impact(issues),
            )
        )
    return points


def _area_metrics(scan: Scan, issues: dict[str, ScanIssueRecord]) -> dict[str, dict[str, int | float]]:
    result = {
        area: {
            "score": max(0, min(100, _safe_int(getattr(scan, BUSINESS_AREA_SCORE_ATTRS[area], 0)))),
            "findings": 0,
            "impact": 0.0,
        }
        for area in BUSINESS_AREAS
    }
    for issue in issues.values():
        area = _normalize_category(issue.category, issue.code)
        result[area]["findings"] = int(result[area]["findings"]) + 1
        result[area]["impact"] = float(result[area]["impact"]) + max(0.0, _safe_float(issue.estimated_impact_eur))
    return result


def _area_trend(score_delta: int, impact_delta: float) -> str:
    if score_delta > 0 and impact_delta <= 0:
        return "improving"
    if score_delta < 0 and impact_delta >= 0:
        return "deteriorating"
    if impact_delta < -0.01 and score_delta >= 0:
        return "improving"
    if impact_delta > 0.01 and score_delta <= 0:
        return "deteriorating"
    return "stable"


def _business_area_trends(
    scans: list[Scan],
    issues_by_scan: dict[str, dict[str, ScanIssueRecord]],
    language: str,
) -> list[MonitoringBusinessAreaTrend]:
    baseline = scans[0]
    current = scans[-1]
    previous = scans[-2] if len(scans) > 1 else current
    baseline_metrics = _area_metrics(baseline, issues_by_scan[baseline.scan_id])
    previous_metrics = _area_metrics(previous, issues_by_scan[previous.scan_id])
    current_metrics = _area_metrics(current, issues_by_scan[current.scan_id])
    rows: list[MonitoringBusinessAreaTrend] = []
    for area in BUSINESS_AREAS:
        b = baseline_metrics[area]
        p = previous_metrics[area]
        c = current_metrics[area]
        score_delta_previous = int(c["score"]) - int(p["score"])
        impact_delta_previous = round(float(c["impact"]) - float(p["impact"]), 2)
        rows.append(
            MonitoringBusinessAreaTrend(
                name=area,
                label=_area_label(area, language),
                baseline_score=int(b["score"]),
                previous_score=int(p["score"]),
                current_score=int(c["score"]),
                score_delta_previous=score_delta_previous,
                score_delta_baseline=int(c["score"]) - int(b["score"]),
                baseline_findings_count=int(b["findings"]),
                previous_findings_count=int(p["findings"]),
                current_findings_count=int(c["findings"]),
                findings_delta_previous=int(c["findings"]) - int(p["findings"]),
                baseline_impact_eur=round(float(b["impact"]), 2),
                previous_impact_eur=round(float(p["impact"]), 2),
                current_impact_eur=round(float(c["impact"]), 2),
                impact_delta_previous_eur=impact_delta_previous,
                trend=_area_trend(score_delta_previous, impact_delta_previous),
            )
        )
    return rows


def _finding_status(previous: ScanIssueRecord, current: ScanIssueRecord) -> str:
    prev_severity = SEVERITY_RANK[normalize_severity(previous.severity)]
    cur_severity = SEVERITY_RANK[normalize_severity(current.severity)]
    prev_affected = max(0, _safe_int(previous.affected_count))
    cur_affected = max(0, _safe_int(current.affected_count))
    prev_impact = max(0.0, _safe_float(previous.estimated_impact_eur))
    cur_impact = max(0.0, _safe_float(current.estimated_impact_eur))
    if cur_severity > prev_severity or cur_affected > prev_affected or cur_impact > prev_impact + 0.01:
        return "regressing"
    if cur_severity < prev_severity or cur_affected < prev_affected or cur_impact < prev_impact - 0.01:
        return "improving"
    return "persistent"


def _finding_lifecycle(
    scans: list[Scan],
    issues_by_scan: dict[str, dict[str, ScanIssueRecord]],
    language: str,
) -> list[MonitoringFindingLifecycle]:
    histories: dict[str, list[tuple[int, Scan, ScanIssueRecord]]] = defaultdict(list)
    for index, scan in enumerate(scans):
        for issue in issues_by_scan.get(scan.scan_id, {}).values():
            histories[issue.code].append((index, scan, issue))

    current_index = len(scans) - 1
    previous_index = max(0, current_index - 1)
    rows: list[MonitoringFindingLifecycle] = []
    for code, history in histories.items():
        first_index, first_scan, _ = history[0]
        _, last_scan, last_issue = history[-1]
        by_index = {index: issue for index, _, issue in history}
        current = by_index.get(current_index)
        previous = by_index.get(previous_index) if current_index > 0 else current

        if current is None:
            status = "resolved"
            source = last_issue
        elif first_index == current_index:
            status = "new"
            source = current
        elif current_index > 0 and previous is None:
            status = "reopened"
            source = current
        elif previous is not None:
            status = _finding_status(previous, current)
            source = current
        else:
            status = "persistent"
            source = current

        area = _normalize_category(source.category, source.code)
        rows.append(
            MonitoringFindingLifecycle(
                code=code,
                title=source.title,
                category=area,
                category_label=_area_label(area, language),
                status=status,
                first_seen_at_utc=first_scan.generated_at_utc,
                last_seen_at_utc=last_scan.generated_at_utc,
                scans_seen=len(history),
                current_severity=normalize_severity(current.severity) if current else None,
                previous_severity=normalize_severity(previous.severity) if previous else None,
                current_affected_records=max(0, _safe_int(current.affected_count)) if current else 0,
                previous_affected_records=max(0, _safe_int(previous.affected_count)) if previous else 0,
                current_impact_eur=round(max(0.0, _safe_float(current.estimated_impact_eur)), 2) if current else 0.0,
                previous_impact_eur=round(max(0.0, _safe_float(previous.estimated_impact_eur)), 2) if previous else 0.0,
            )
        )
    status_order = {"regressing": 0, "reopened": 1, "new": 2, "persistent": 3, "improving": 4, "resolved": 5}
    rows.sort(
        key=lambda row: (
            status_order.get(row.status, 9),
            -SEVERITY_RANK.get(row.current_severity or row.previous_severity or "info", 0),
            -row.current_impact_eur,
            row.code,
        )
    )
    return rows


def _freshness(latest_at: datetime) -> tuple[float, str]:
    hours = max(0.0, (datetime.now(timezone.utc) - _as_utc(latest_at)).total_seconds() / 3600.0)
    if hours <= 48:
        return round(hours, 1), "current"
    if hours <= 168:
        return round(hours, 1), "aging"
    return round(hours, 1), "stale"


def _coverage(scans: list[Scan], monitoring_access_until: str | None) -> MonitoringCoverage:
    baseline = scans[0]
    current = scans[-1]
    previous = scans[-2] if len(scans) > 1 else None
    freshness_hours, data_freshness = _freshness(current.generated_at_utc)
    return MonitoringCoverage(
        period_start_utc=baseline.generated_at_utc,
        period_end_utc=current.generated_at_utc,
        scans_in_period=len(scans),
        latest_scan_at_utc=current.generated_at_utc,
        previous_scan_at_utc=previous.generated_at_utc if previous else None,
        baseline_scan_at_utc=baseline.generated_at_utc,
        freshness_hours=freshness_hours,
        monitoring_access_until=monitoring_access_until,
        data_freshness=data_freshness,
    )


def _management_interpretation(
    *,
    language: str,
    score_delta_baseline: int,
    business_impact_delta_baseline: float,
    areas: list[MonitoringBusinessAreaTrend],
    lifecycle: list[MonitoringFindingLifecycle],
) -> list[str]:
    attention = [row for row in lifecycle if row.status in {"regressing", "reopened", "new"}]
    improving_areas = sorted(
        [row for row in areas if row.trend == "improving"],
        key=lambda row: (row.score_delta_previous, -row.impact_delta_previous_eur),
        reverse=True,
    )
    deteriorating_areas = sorted(
        [row for row in areas if row.trend == "deteriorating"],
        key=lambda row: (row.score_delta_previous, -row.impact_delta_previous_eur),
    )
    if language == "de":
        result = [
            f"Seit Monitoring-Beginn beträgt die Score-Veränderung {score_delta_baseline:+d} Punkte und das Delta des modellierten Business Impacts {business_impact_delta_baseline:+.0f} EUR."
        ]
        if improving_areas:
            row = improving_areas[0]
            result.append(
                f"Aktuell stärkste Bereichsentwicklung: {row.label} mit {row.score_delta_previous:+d} Score-Punkten gegenüber dem vorherigen Scan."
            )
        if deteriorating_areas or attention:
            area_text = deteriorating_areas[0].label if deteriorating_areas else None
            if area_text:
                result.append(
                    f"Weiterer Fokus erforderlich: {area_text} entwickelt sich negativ; zusätzlich bestehen {len(attention)} neue, wieder aufgetretene oder sich verschlechternde Findings."
                )
            else:
                result.append(
                    f"Weiterer Fokus erforderlich: {len(attention)} Findings sind neu, wieder aufgetreten oder haben sich verschlechtert."
                )
        else:
            result.append("Im letzten Scan wurden keine neuen, wieder aufgetretenen oder sich verschlechternden Findings erkannt.")
        return result[:3]

    result = [
        f"Since Monitoring began, Data Health Score changed by {score_delta_baseline:+d} points and modeled Business Impact changed by {business_impact_delta_baseline:+.0f} EUR."
    ]
    if improving_areas:
        row = improving_areas[0]
        result.append(
            f"Strongest current area development: {row.label}, {row.score_delta_previous:+d} score points versus the previous scan."
        )
    if deteriorating_areas or attention:
        area_text = deteriorating_areas[0].label if deteriorating_areas else None
        if area_text:
            result.append(
                f"Further attention is required: {area_text} is deteriorating and {len(attention)} findings are new, reopened or regressing."
            )
        else:
            result.append(f"Further attention is required: {len(attention)} findings are new, reopened or regressing.")
    else:
        result.append("No new, reopened or regressing findings were detected in the latest scan.")
    return result[:3]


def build_monitoring_report(
    db: Session,
    tenant: Tenant,
    current_scan_id: str | None = None,
) -> MonitoringReport:
    access = build_product_access_snapshot(db, tenant)
    if not access["monitoring_active"]:
        raise HTTPException(status_code=402, detail="Monitoring Report access requires an active Monitoring subscription.")

    scans = _load_scans(db, tenant, current_scan_id)
    scan_ids = [scan.scan_id for scan in scans]
    issues_by_scan = _issue_maps(db, scan_ids)
    language = tenant_language(tenant)
    trend_points = _trend_points(scans, issues_by_scan)
    areas = _business_area_trends(scans, issues_by_scan, language)
    lifecycle = _finding_lifecycle(scans, issues_by_scan, language)

    baseline = scans[0]
    current = scans[-1]
    previous = scans[-2] if len(scans) > 1 else current
    current_issues = list(issues_by_scan[current.scan_id].values())
    previous_issues = list(issues_by_scan[previous.scan_id].values())
    baseline_issues = list(issues_by_scan[baseline.scan_id].values())

    current_affected = _affected_records(current_issues)
    previous_affected = _affected_records(previous_issues)
    current_impact = _impact(current_issues)
    previous_impact = _impact(previous_issues)
    baseline_impact = _impact(baseline_issues)

    counts = defaultdict(int)
    for row in lifecycle:
        counts[row.status] += 1

    priority_statuses = {"regressing", "reopened", "new", "persistent"}
    top_priorities = [row for row in lifecycle if row.status in priority_statuses and row.current_severity is not None][:10]
    score_delta_baseline = _safe_int(current.data_score) - _safe_int(baseline.data_score)
    business_impact_delta_baseline = round(current_impact - baseline_impact, 2)

    critical = sum(1 for issue in current_issues if normalize_severity(issue.severity) == "critical")
    high = sum(1 for issue in current_issues if normalize_severity(issue.severity) == "high")

    return MonitoringReport(
        tenant_id=tenant.tenant_id,
        company_name=tenant.tenant_id,
        environment_name=tenant.environment_name,
        language=language,
        current_scan_id=current.scan_id,
        previous_scan_id=previous.scan_id if len(scans) > 1 else None,
        baseline_scan_id=baseline.scan_id,
        current_data_health_score=_safe_int(current.data_score),
        previous_data_health_score=_safe_int(previous.data_score),
        baseline_data_health_score=_safe_int(baseline.data_score),
        score_delta_previous=_safe_int(current.data_score) - _safe_int(previous.data_score),
        score_delta_baseline=score_delta_baseline,
        current_findings_count=len(current_issues),
        previous_findings_count=len(previous_issues),
        findings_delta_previous=len(current_issues) - len(previous_issues),
        current_affected_records=current_affected,
        previous_affected_records=previous_affected,
        affected_records_delta_previous=current_affected - previous_affected,
        current_business_impact_eur=current_impact,
        previous_business_impact_eur=previous_impact,
        business_impact_delta_previous_eur=round(current_impact - previous_impact, 2),
        business_impact_delta_baseline_eur=business_impact_delta_baseline,
        current_critical_findings=critical,
        current_high_findings=high,
        trend_points=trend_points,
        business_areas=areas,
        finding_lifecycle=lifecycle,
        new_findings_count=counts["new"],
        resolved_findings_count=counts["resolved"],
        persistent_findings_count=counts["persistent"],
        improving_findings_count=counts["improving"],
        regressing_findings_count=counts["regressing"],
        reopened_findings_count=counts["reopened"],
        top_priorities=top_priorities,
        management_interpretation=_management_interpretation(
            language=language,
            score_delta_baseline=score_delta_baseline,
            business_impact_delta_baseline=business_impact_delta_baseline,
            areas=areas,
            lifecycle=lifecycle,
        ),
        coverage=_coverage(scans, access.get("monitoring_access_until")),
    )
