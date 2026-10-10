import { apiFetch } from './client';

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

export type NotificationSettings = {
  tenant_id?: string;
  company_id?: string | null;
  enabled?: boolean;
  channels?: string[];
  template_languages?: string[];
  configured_event_types?: string[];
  enabled_event_types?: string[];
  recipient_count?: number;
  delivery_attempt_count?: number;
  sent_count?: number;
  failed_count?: number;
  success_rate?: number | null;
  last_successful_delivery_at_utc?: string | null;
  last_failure_summary?: string | null;
};

export async function getSubscriptionStatus() {
  return apiFetch<SubscriptionStatus>('/billing/subscription/status');
}

export async function openBillingPortal(tenantId: string) {
  return apiFetch<BillingPortalResponse>('/billing/portal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tenant_id: tenantId }),
  });
}

export async function getNotificationSettings() {
  return apiFetch<NotificationSettings>('/notifications/settings');
}
