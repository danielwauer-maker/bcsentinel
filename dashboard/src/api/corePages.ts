import { apiRequest, ApiError, type TenantSession } from './client';
import type {
  AnalyticsDashboardData,
  ExecutiveReport,
  RemediationAction,
  RemediationMetrics,
  ScanExceptionSnapshot,
  ScanRuntimeStatus,
} from '../core/types';

const encode = (value: string) => encodeURIComponent(value);

export async function loadAnalyticsDashboard(
  session: TenantSession,
  scanId?: string | null,
): Promise<AnalyticsDashboardData> {
  const params = new URLSearchParams({
    company: 'BCSentinel',
    environment: 'Business Central',
  });
  const tokenResponse = await apiRequest<{ token: string }>(`/analytics/get-token?${params.toString()}`, session);
  const dataParams = new URLSearchParams({ embed_token: tokenResponse.token });
  if (scanId) dataParams.set('scan_id', scanId);
  return apiRequest<AnalyticsDashboardData>(`/analytics/embed/data?${dataParams.toString()}`, session);
}

export async function loadRemediationMetrics(session: TenantSession): Promise<RemediationMetrics> {
  return apiRequest<RemediationMetrics>('/remediation/metrics', session);
}

export async function loadRemediationActions(
  session: TenantSession,
  filters: { status?: string; priority?: string } = {},
): Promise<RemediationAction[]> {
  const params = new URLSearchParams({ limit: '200', offset: '0' });
  if (filters.status) params.set('status', filters.status);
  if (filters.priority) params.set('priority', filters.priority);
  const response = await apiRequest<{ items: RemediationAction[] }>(`/remediation/actions?${params.toString()}`, session);
  return response.items;
}

export async function loadExecutiveReport(session: TenantSession, scanId: string): Promise<ExecutiveReport> {
  return apiRequest<ExecutiveReport>(`/reports/executive/${encode(scanId)}`, session);
}

export async function loadLatestScanStatus(session: TenantSession): Promise<ScanRuntimeStatus | null> {
  try {
    return await apiRequest<ScanRuntimeStatus>('/scan/status/latest', session);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export async function loadScanExceptions(session: TenantSession, scanId: string): Promise<ScanExceptionSnapshot> {
  return apiRequest<ScanExceptionSnapshot>(`/scans/${encode(scanId)}/exceptions`, session);
}
