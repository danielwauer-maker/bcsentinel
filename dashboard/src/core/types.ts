export type ExperienceMode = 'free' | 'assessment' | 'monitoring';

export type TrendPoint = {
  scan_id: string;
  label: string;
  timestamp: string;
  value: number;
  scan_type?: string;
  is_selected?: boolean;
};

export type Finding = {
  code: string;
  title: string;
  severity: string;
  severity_label?: string;
  count: number;
  impact_eur: number;
  group: string;
  recommendation_preview?: string;
  premium_only?: boolean;
  open_in_bc_url?: string | null;
};

export type ScanSummary = {
  scan_id: string;
  generated_at: string;
  scan_type: string;
  data_score: number;
  issues_count: number;
  headline?: string;
  is_selected?: boolean;
  is_valid?: boolean;
};

export type AnalyticsDashboardData = {
  title: string;
  language: string;
  subtitle: string;
  scan_mode_label: string;
  last_updated: string;
  selected_scan_id: string | null;
  current_plan: string;
  product_access?: {
    monitoring_active?: boolean;
    assessment_access_active?: boolean;
    validation_access_active?: boolean;
    can_view_dashboard?: boolean;
    can_view_issue_details?: boolean;
    can_view_executive_report?: boolean;
    [key: string]: unknown;
  };
  visibility: {
    is_premium: boolean;
    show_findings: boolean;
    show_trends: boolean;
    show_upgrade_preview: boolean;
  };
  hero: {
    eyebrow: string;
    headline_prefix: string;
    headline_highlight: string;
    headline_suffix: string;
  };
  kpis: {
    health_score: number;
    total_records: number;
    affected_records: number;
    estimated_premium_price_monthly: number;
    estimated_loss_eur: number;
    potential_saving_eur: number;
    roi_eur: number;
    checks_run: number;
    issues_count: number;
  };
  module_scores: Array<{ name: string; label?: string; score: number; value?: number; variant?: string }>;
  issue_groups: Array<{ name: string; count: number }>;
  top_findings: Finding[];
  premium_preview_findings: Array<Pick<Finding, 'title' | 'group' | 'count' | 'impact_eur' | 'recommendation_preview'>>;
  recent_scans: ScanSummary[];
  score_trend: TrendPoint[];
  loss_trend: TrendPoint[];
};

export type RemediationMetrics = {
  total: number;
  open: number;
  in_progress: number;
  blocked: number;
  completed: number;
  cancelled: number;
  overdue: number;
  validated_resolved: number | null;
  note: string;
};

export type RemediationAction = {
  action_id: string;
  tenant_id: string;
  company_id: string;
  finding_key: string;
  title: string;
  description: string;
  recommendation_ref?: string | null;
  status: 'open' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';
  priority: 'critical' | 'high' | 'medium' | 'low';
  owner_display_name?: string | null;
  due_at_utc?: string | null;
  completed_at_utc?: string | null;
  blocked_reason?: string | null;
  completion_note?: string | null;
  validation_result_ref?: string | null;
  updated_at_utc: string;
};

export type ExecutiveReportFinding = {
  rank: number;
  code: string;
  title: string;
  category: string;
  severity: string;
  affected_count: number;
  estimated_impact_eur: number;
  recommendation: string;
};

export type ExecutiveReport = {
  report_id: string;
  scan_id: string;
  generated_at_utc: string;
  scan_generated_at_utc: string;
  company_label: string;
  environment_label: string;
  executive_summary: string;
  data_health_score: number;
  score_status: string;
  total_records: number;
  checks_count: number;
  issues_count: number;
  affected_records: number;
  estimated_loss_eur: number;
  potential_saving_eur: number;
  headline: string;
  rating: string;
  top_risks: ExecutiveReportFinding[];
  critical_findings: ExecutiveReportFinding[];
  recommended_actions: string[];
  next_steps: string[];
};

export type ScanRuntimeStatus = {
  run_id?: string;
  scan_id?: string;
  status?: string;
  progress_percent?: number;
  current_module?: string | null;
  current_step?: string | null;
  updated_at_utc?: string;
};

export type ScanExceptionItem = {
  source_exception_entry_no: number;
  company_id?: string | null;
  table_id: number;
  record_no?: string | null;
  record_caption?: string | null;
  issue_code: string;
  reason: string;
  exception_created_by?: string | null;
  exception_created_at_utc?: string | null;
  captured_at_utc: string;
};

export type ScanExceptionSnapshot = {
  scan_id: string;
  tenant_id: string;
  snapshot_captured: boolean;
  captured_at_utc?: string | null;
  exception_count: number;
  exceptions_applied: boolean;
  exceptions: ScanExceptionItem[];
};

export function experienceMode(data: AnalyticsDashboardData): ExperienceMode {
  if (data.product_access?.monitoring_active) return 'monitoring';
  if (
    data.visibility.is_premium ||
    data.product_access?.assessment_access_active ||
    data.product_access?.validation_access_active ||
    data.product_access?.can_view_dashboard
  ) return 'assessment';
  return 'free';
}
