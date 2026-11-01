pageextension 53201 "DH Deep Scan Monitor Reports" extends "DH Deep Scan Monitor"
{
    actions
    {
        modify(OpenExecutiveReport)
        {
            Visible = false;
        }
        modify(OpenExecutivePdf)
        {
            Visible = false;
        }

        addafter(OpenExternalDashboard)
        {
            group(BCSentinelReports)
            {
                Caption = 'BCSentinel Reports';

                action(OpenBestAvailableReport)
                {
                    Caption = 'Open BCSentinel Report';
                    ApplicationArea = All;
                    Image = Report;
                    ToolTip = 'Open the highest BCSentinel report level available for this scan. The backend automatically selects Validation, Assessment, Quick Assessment, or Free Health.';
                    Promoted = true;
                    PromotedCategory = Process;
                    PromotedIsBig = true;

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenBestAvailableReport(Rec."Run ID", 'html');
                    end;
                }

                action(OpenBestAvailablePdf)
                {
                    Caption = 'Open BCSentinel PDF';
                    ApplicationArea = All;
                    Image = Print;
                    ToolTip = 'Open the highest BCSentinel report level available for this scan as PDF.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenBestAvailableReport(Rec."Run ID", 'pdf');
                    end;
                }

                action(OpenFreeHealthReport)
                {
                    Caption = 'Free Health Report';
                    ApplicationArea = All;
                    Image = Report;
                    ToolTip = 'Open the aggregate-only BCSentinel Free Health Report for this scan.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenReport(Rec."Run ID", 'free-health', 'html');
                    end;
                }

                action(OpenQuickAssessmentReport)
                {
                    Caption = 'Quick Assessment Report';
                    ApplicationArea = All;
                    Image = Report;
                    ToolTip = 'Open the prioritized Top 5 BCSentinel Quick Assessment report when Quick or a higher product level is available.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenReport(Rec."Run ID", 'quick-assessment', 'html');
                    end;
                }

                action(OpenAssessmentReport)
                {
                    Caption = 'Assessment Report';
                    ApplicationArea = All;
                    Image = Report;
                    ToolTip = 'Open the detailed BCSentinel Assessment Report. Active Assessment, Validation, or Monitoring access is required.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenReport(Rec."Run ID", 'assessment', 'html');
                    end;
                }

                action(OpenValidationReport)
                {
                    Caption = 'Validation Report';
                    ApplicationArea = All;
                    Image = CompareCost;
                    ToolTip = 'Open the before/after BCSentinel Validation Report for a completed Validation scan.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenReport(Rec."Run ID", 'validation', 'html');
                    end;
                }
            }
        }
    }
}
