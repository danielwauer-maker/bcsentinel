-- Anonymous GL-PILOT-01-FIX01 migration fixture for schema revision 0024.
-- Contains no production identifiers, credentials, or personal data.
INSERT INTO tenants (
    tenant_id, environment_name, app_version, created_at_utc,
    current_plan, license_status, preferred_language
) VALUES (
    'ten_fix01_legacy', 'Legacy Sandbox', '1.0.2.4',
    '2026-01-01T00:00:00Z', 'free', 'trial', 'en'
);

INSERT INTO dashboard_users (
    tenant_id, email, status, must_change_password,
    created_at_utc, updated_at_utc, invite_mail_status
) VALUES (
    'ten_fix01_legacy', 'fix01-legacy@example.invalid', 'active', false,
    '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', 'sent'
);
