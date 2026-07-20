-- Anonymous GL-EXT-P0E upgrade fixture for schema revision 0021.
-- Contains no production identifiers, credentials, or personal data.
INSERT INTO tenants (
    tenant_id, environment_name, app_version, created_at_utc,
    last_seen_at_utc, current_plan, license_status, preferred_language
) VALUES (
    'ten_p0e_legacy', 'Legacy Sandbox', '1.0.2.1',
    '2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z',
    'premium', 'active', 'en'
);

INSERT INTO tenant_product_purchases (
    tenant_id, product_code, provider, provider_checkout_session_id,
    status, currency, amount_total, source, created_at_utc, updated_at_utc
) VALUES (
    'ten_p0e_legacy', 'full_analysis', 'manual', 'p0e_legacy_checkout',
    'paid', 'EUR', 49.00, 'p0e_fixture',
    '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z'
);

INSERT INTO tenant_scan_credits (
    tenant_id, product_code, status, source, source_purchase_id,
    created_at_utc
) VALUES (
    'ten_p0e_legacy', 'full_analysis', 'available', 'p0e_fixture',
    (SELECT id FROM tenant_product_purchases WHERE provider_checkout_session_id = 'p0e_legacy_checkout'),
    '2026-01-01T00:00:00Z'
);

INSERT INTO scans (
    scan_id, tenant_id, scan_type, generated_at_utc, data_score,
    checks_count, issues_count, premium_available,
    summary_headline, summary_rating, total_records
) VALUES (
    'scan_p0e_legacy', 'ten_p0e_legacy', 'deep',
    '2026-01-01T01:00:00Z', 72, 12, 1, true,
    'Anonymous legacy scan', 'needs_attention', 100
);

INSERT INTO scan_issues (
    scan_id, code, title, severity, affected_count,
    premium_only, recommendation_preview, estimated_impact_eur, category
) VALUES (
    'scan_p0e_legacy', 'P0E_LEGACY_FINDING', 'Anonymous legacy finding',
    'medium', 1, true, 'Anonymous recommendation', 10.00, 'SYSTEM'
);

INSERT INTO scan_run_statuses (
    run_id, tenant_id, company_name, environment_name, scan_mode,
    status, progress_percent, updated_at_utc, heartbeat_at_utc,
    total_modules, completed_modules, failed_modules
) VALUES (
    'run_p0e_legacy', 'ten_p0e_legacy', 'Legacy Company',
    'Legacy Sandbox', 'assessment', 'running', 40,
    '2026-01-01T01:10:00Z', '2026-01-01T01:10:00Z', 10, 4, 0
);
