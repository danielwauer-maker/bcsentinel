SELECT 'dashboard_users' AS metric, count(*) AS row_count FROM dashboard_users
UNION ALL
SELECT 'missing_tenant_id', count(*) FROM dashboard_users WHERE tenant_id IS NULL;
