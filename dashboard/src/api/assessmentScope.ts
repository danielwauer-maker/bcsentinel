import { apiRequest, type TenantSession } from './client';

export type AssessmentScopeModule = {
  module_code: string;
  display_name: string;
  support_status: string;
  detection_status: 'active' | 'not_detected' | 'unknown' | string;
  decision: 'include' | 'exclude' | 'inherit' | string;
  included_in_score: boolean;
  confidence: number;
  detection_reason: string;
  module_score: number;
};

export type AssessmentScopeResponse = {
  scan_id: string;
  version: number;
  state: 'auto' | 'confirmed' | string;
  score_type: 'preliminary' | 'confirmed_baseline' | string;
  score: number;
  supported_modules: number;
  included_modules: number;
  unknown_modules: number;
  custom_extensions_scored: boolean;
  unsupported_extensions: string[];
  confirmed_at_utc?: string | null;
  modules?: AssessmentScopeModule[];
};

export function getAssessmentScope(session: TenantSession, scanId: string) {
  return apiRequest<AssessmentScopeResponse>(`/scans/${encodeURIComponent(scanId)}/assessment-scope`, session);
}

export function confirmAssessmentScope(session: TenantSession, scanId: string, decisions: Record<string, 'include' | 'exclude' | 'inherit'>) {
  return apiRequest<AssessmentScopeResponse>(`/scans/${encodeURIComponent(scanId)}/assessment-scope/confirm`, session, {
    method: 'POST',
    body: JSON.stringify({ decisions }),
  });
}
