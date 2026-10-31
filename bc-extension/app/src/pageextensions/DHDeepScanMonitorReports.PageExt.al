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

                action(OpenFreeHealthPdf)
                {
                    Caption = 'Free Health PDF';
                    ApplicationArea = All;
                    Image = Print;
                    ToolTip = 'Open the aggregate-only BCSentinel Free Health Report as PDF.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenReport(Rec."Run ID", 'free-health', 'pdf');
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

                action(OpenAssessmentPdf)
                {
                    Caption = 'Assessment PDF';
                    ApplicationArea = All;
                    Image = Print;
                    ToolTip = 'Open the detailed BCSentinel Assessment Report as PDF.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenReport(Rec."Run ID", 'assessment', 'pdf');
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

                action(OpenValidationPdf)
                {
                    Caption = 'Validation PDF';
                    ApplicationArea = All;
                    Image = Print;
                    ToolTip = 'Open the before/after BCSentinel Validation Report as PDF.';

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenReport(Rec."Run ID", 'validation', 'pdf');
                    end;
                }
            }
        }
    }
}
