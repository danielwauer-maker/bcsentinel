SELECT 'tenants' AS metric, count(*) AS row_count FROM tenants
UNION ALL
SELECT 'dashboard_users', count(*) FROM dashboard_users
UNION ALL
SELECT 'memberships', count(*) FROM dashboard_user_tenant_memberships
UNION ALL
SELECT 'missing_normalized_email', count(*) FROM dashboard_users WHERE normalized_email IS NULL
UNION ALL
SELECT 'orphan_memberships', count(*)
FROM dashboard_user_tenant_memberships m
LEFT JOIN dashboard_users u ON u.id = m.dashboard_user_id
LEFT JOIN tenants t ON t.tenant_id = m.tenant_id
WHERE u.id IS NULL OR t.tenant_id IS NULL
UNION ALL
SELECT 'duplicate_memberships', count(*)
FROM (
    SELECT dashboard_user_id, tenant_id
    FROM dashboard_user_tenant_memberships
    GROUP BY dashboard_user_id, tenant_id
    HAVING count(*) > 1
) duplicates;
