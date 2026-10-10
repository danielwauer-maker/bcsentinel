import type { TenantSession } from './client';
import { apiRequest } from './client';

export type SubscriptionStatus = {
  tenant_id: string;
  current_plan: string;
  license_status: string;
  subscription_status?: string | null;
  provider?: string | null;
  provider_subscription_id?: string | null;
  current_period_end_utc?: string | null;
  cancel_at_period_end: boolean;
  amount_monthly: number;
  currency: string;
};

export type BillingPortalResponse = {
  provider: string;
  tenant_id: string;
  portal_url: string;
};

export type NotificationSettingsItem = {
  tenant_id: string;
  company_id: string;
  notifications_enabled: boolean;
  preferred_language: string;
  configured_event_types: string[];
  enabled_event_types: string[];
  recipient_summary: { configured: number; enabled: number };
  channel_summary: string[];
  template_language_summary: string[];
  delivery_summary: {
    sent: number;
    failed: number;
    suppressed: number;
    success_rate_pct: number | null;
    last_successful_delivery_at_utc?: string | null;
    last_failed_delivery_at_utc?: string | null;
    safe_last_failure_summary?: string | null;
  };
  bc_updated_at_utc?: string | null;
  synced_at_utc?: string | null;
  manage_in_business_central_hint: boolean;
  dashboard_mode: 'read_only';
};

export type NotificationSettingsResponse = {
  items: NotificationSettingsItem[];
  dashboard_mode: 'read_only';
  manage_in_business_central_hint: boolean;
};

export const getSubscriptionStatus = (session: TenantSession) =>
  apiRequest<SubscriptionStatus>('/billing/subscription/status', session);

export const openBillingPortal = (session: TenantSession) =>
  apiRequest<BillingPortalResponse>('/billing/portal', session, {
    method: 'POST',
    body: JSON.stringify({ tenant_id: session.tenantId }),
  });

export const getNotificationSettings = (session: TenantSession) =>
  apiRequest<NotificationSettingsResponse>('/notifications/settings', session);
