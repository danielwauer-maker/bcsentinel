-- FULL-SCOPE-01 read-only audit
-- PostgreSQL/psql. All statements are SELECTs; no transaction mutation is used.
-- Required psql variable: scan_id
-- Example: psql "$DEV_DATABASE_URL" -v scan_id='RUN_...' -f this-file.sql

\echo '1) Scan identity and scope versions'
WITH p AS (SELECT :'scan_id'::text AS scan_id),
scope_ranked AS (
    SELECT s.*, row_number() OVER (PARTITION BY s.scan_id ORDER BY s.version DESC) AS rn,
           row_number() OVER (PARTITION BY s.scan_id, s.state ORDER BY s.version DESC) AS state_rn
    FROM assessment_scope_snapshots s JOIN p ON p.scan_id = s.scan_id
)
SELECT sc.scan_id, sc.tenant_id, sc.bc_company_id, sc.lcy_code,
       sc.data_score, sc.issues_count AS stored_issues_count,
       rs.run_id, rs.status AS run_status, rs.scan_mode,
       auto.version AS auto_scope_version, auto.source AS auto_scope_source,
       auto.score_value AS auto_scope_score, auto.included_modules_count AS auto_included_modules,
       auto.unknown_modules_count AS auto_unknown_modules,
       confirmed.version AS confirmed_scope_version,
       confirmed.state AS confirmed_scope_state,
       confirmed.score_value AS confirmed_scope_score,
       confirmed.included_modules_count AS confirmed_included_modules,
       confirmed.unknown_modules_count AS confirmed_unknown_modules
FROM scans sc JOIN p ON p.scan_id = sc.scan_id
LEFT JOIN scan_run_statuses rs ON rs.run_id = sc.scan_id AND rs.tenant_id = sc.tenant_id
LEFT JOIN scope_ranked auto ON auto.scan_id = sc.scan_id AND auto.state = 'auto' AND auto.state_rn = 1
LEFT JOIN scope_ranked confirmed ON confirmed.scan_id = sc.scan_id AND confirmed.state = 'confirmed' AND confirmed.state_rn = 1;

\echo '2) Scan profile and persisted automatic module detection'
WITH p AS (SELECT :'scan_id'::text AS scan_id)
SELECT sc.scan_id, sc.enabled_modules,
       sc.customers_count, sc.vendors_count, sc.items_count,
       sc.customer_ledger_entries_count, sc.vendor_ledger_entries_count,
       sc.item_ledger_entries_count, sc.sales_headers_count, sc.sales_lines_count,
       sc.purchase_headers_count, sc.purchase_lines_count, sc.gl_entries_count,
       sc.value_entries_count, sc.warehouse_entries_count,
       sm.module_code, sm.display_name, sm.detection_status, sm.decision,
       sm.included_in_score, sm.confidence, sm.detection_reason, sm.module_score
FROM scans sc JOIN p ON p.scan_id = sc.scan_id
LEFT JOIN assessment_scope_snapshots ss ON ss.scan_id = sc.scan_id AND ss.state = 'auto'
LEFT JOIN assessment_scope_modules sm ON sm.snapshot_id = ss.id
ORDER BY sm.module_code;

\echo '3) Confirmed customer decisions'
WITH p AS (SELECT :'scan_id'::text AS scan_id), confirmed AS (
    SELECT s.id, s.version
    FROM assessment_scope_snapshots s JOIN p ON p.scan_id = s.scan_id
    WHERE s.state = 'confirmed'
    ORDER BY s.version DESC LIMIT 1
)
SELECT c.version AS confirmed_scope_version, m.module_code, m.display_name,
       m.detection_status, m.decision, m.included_in_score,
       m.confidence, m.detection_reason, m.module_score
FROM confirmed c JOIN assessment_scope_modules m ON m.snapshot_id = c.id
ORDER BY m.module_code;

\echo '4) Every original finding with Full classification and reason'
WITH p AS (SELECT :'scan_id'::text AS scan_id),
confirmed AS (
    SELECT s.id, s.version
    FROM assessment_scope_snapshots s JOIN p ON p.scan_id = s.scan_id
    WHERE s.state = 'confirmed'
    ORDER BY s.version DESC LIMIT 1
),
classified AS (
    SELECT i.*, CASE lower(trim(coalesce(i.category, '')))
        WHEN 'finance' THEN 'finance' WHEN 'sales' THEN 'sales'
        WHEN 'purchase' THEN 'purchasing' WHEN 'purchasing' THEN 'purchasing'
        WHEN 'inventory' THEN 'inventory' WHEN 'item' THEN 'inventory'
        WHEN 'crm' THEN 'crm' WHEN 'customer' THEN 'crm'
        WHEN 'manufacturing' THEN 'manufacturing' WHEN 'service' THEN 'service'
        WHEN 'jobs' THEN 'jobs' WHEN 'job' THEN 'jobs'
        WHEN 'hr' THEN 'hr' WHEN 'system' THEN 'system' WHEN 'setup' THEN 'system'
        ELSE '__unsupported__' END AS full_module
    FROM scan_issues i JOIN p ON p.scan_id = i.scan_id
),
joined AS (
    SELECT c.*, m.decision, m.included_in_score,
           CASE
             WHEN c.full_module = '__unsupported__' THEN 'unsupported_or_unmapped_original_category'
             WHEN m.module_code IS NULL THEN 'module_missing_from_confirmed_scope'
             WHEN m.included_in_score = 0 THEN 'confirmed_module_excluded'
             ELSE 'included_in_confirmed_scope'
           END AS full_scope_reason
    FROM classified c
    LEFT JOIN confirmed s ON true
    LEFT JOIN assessment_scope_modules m ON m.snapshot_id = s.id AND m.module_code = c.full_module
)
SELECT finding_id, code, category, full_module, decision, included_in_score,
       full_scope_reason, severity, title, affected_count, estimated_impact_eur
FROM joined
ORDER BY full_scope_reason, full_module, code, finding_id;

\echo '5) Counts by module/category and exclusion reason'
WITH p AS (SELECT :'scan_id'::text AS scan_id),
confirmed AS (
    SELECT s.id
    FROM assessment_scope_snapshots s JOIN p ON p.scan_id = s.scan_id
    WHERE s.state = 'confirmed'
    ORDER BY s.version DESC LIMIT 1
),
classified AS (
    SELECT i.*, CASE lower(trim(coalesce(i.category, '')))
        WHEN 'finance' THEN 'finance' WHEN 'sales' THEN 'sales'
        WHEN 'purchase' THEN 'purchasing' WHEN 'purchasing' THEN 'purchasing'
        WHEN 'inventory' THEN 'inventory' WHEN 'item' THEN 'inventory'
        WHEN 'crm' THEN 'crm' WHEN 'customer' THEN 'crm'
        WHEN 'manufacturing' THEN 'manufacturing' WHEN 'service' THEN 'service'
        WHEN 'jobs' THEN 'jobs' WHEN 'job' THEN 'jobs'
        WHEN 'hr' THEN 'hr' WHEN 'system' THEN 'system' WHEN 'setup' THEN 'system'
        ELSE '__unsupported__' END AS full_module
    FROM scan_issues i JOIN p ON p.scan_id = i.scan_id
),
scoped AS (
    SELECT c.*, CASE WHEN c.full_module <> '__unsupported__' AND m.included_in_score = 1 THEN 1 ELSE 0 END AS included
    FROM classified c LEFT JOIN confirmed s ON true
    LEFT JOIN assessment_scope_modules m ON m.snapshot_id = s.id AND m.module_code = c.full_module
)
SELECT full_module, CASE WHEN included = 1 THEN 'included' ELSE 'excluded' END AS result,
       count(*) AS finding_count, sum(affected_count) AS affected_count,
       round(sum(coalesce(estimated_impact_eur, 0))::numeric, 2) AS impact_eur
FROM scoped GROUP BY full_module, result ORDER BY full_module, result;

\echo '6) Free/Full count, score, affected and impact reconciliation'
WITH p AS (SELECT :'scan_id'::text AS scan_id),
confirmed AS (
    SELECT s.id, s.score_value
    FROM assessment_scope_snapshots s JOIN p ON p.scan_id = s.scan_id
    WHERE s.state = 'confirmed' ORDER BY s.version DESC LIMIT 1
),
classified AS (
    SELECT i.*, CASE lower(trim(coalesce(i.category, '')))
        WHEN 'finance' THEN 'finance' WHEN 'sales' THEN 'sales'
        WHEN 'purchase' THEN 'purchasing' WHEN 'purchasing' THEN 'purchasing'
        WHEN 'inventory' THEN 'inventory' WHEN 'item' THEN 'inventory'
        WHEN 'crm' THEN 'crm' WHEN 'customer' THEN 'crm'
        WHEN 'manufacturing' THEN 'manufacturing' WHEN 'service' THEN 'service'
        WHEN 'jobs' THEN 'jobs' WHEN 'job' THEN 'jobs'
        WHEN 'hr' THEN 'hr' WHEN 'system' THEN 'system' WHEN 'setup' THEN 'system'
        ELSE '__unsupported__' END AS full_module
    FROM scan_issues i JOIN p ON p.scan_id = i.scan_id
),
scoped AS (
    SELECT c.* FROM classified c CROSS JOIN confirmed s
    JOIN assessment_scope_modules m ON m.snapshot_id = s.id AND m.module_code = c.full_module AND m.included_in_score = 1
), totals AS (
    SELECT sc.scan_id, sc.issues_count, sc.data_score, sc.estimated_loss_eur, sc.potential_saving_eur,
           count(i.finding_id) AS physical_finding_rows,
           sum(i.affected_count) AS free_affected, sum(coalesce(i.estimated_impact_eur,0)) AS free_impact
    FROM scans sc JOIN p ON p.scan_id = sc.scan_id
    LEFT JOIN scan_issues i ON i.scan_id = sc.scan_id GROUP BY sc.scan_id, sc.data_score, sc.issues_count, sc.estimated_loss_eur, sc.potential_saving_eur
)
SELECT t.scan_id, t.issues_count AS stored_count, t.physical_finding_rows,
       (SELECT count(*) FROM scoped) AS full_scoped_count,
       t.data_score AS free_score, (SELECT score_value FROM confirmed) AS confirmed_full_score,
       t.free_affected, (SELECT coalesce(sum(affected_count),0) FROM scoped) AS full_affected,
       round(t.free_impact::numeric, 2) AS free_issue_impact_eur,
       round((SELECT coalesce(sum(estimated_impact_eur),0) FROM scoped)::numeric, 2) AS full_issue_impact_eur,
       t.estimated_loss_eur AS stored_scan_loss_eur,
       t.potential_saving_eur AS stored_scan_saving_eur
FROM totals t;
