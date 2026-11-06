pageextension 53201 "DH Deep Scan Monitor Reports" extends "DH Deep Scan Monitor"
{
    layout
    {
        modify(Headline)
        {
            Visible = false; // Unified scan headline is rendered by the V2 Control Add-in.
        }
    }

    actions
    {
        modify(OpenAllIssues)
        {
            Visible = ShowPremiumDetails;
        }
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
                    Caption = 'Open Report';
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
                    Caption = 'Open PDF';
                    ApplicationArea = All;
                    Image = Print;
                    ToolTip = 'Open the report level authorized for this scan as PDF.';
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    var
                        ReportMgt: Codeunit "DH Report Link Mgt.";
                    begin
                        ReportMgt.OpenBestAvailableReport(Rec."Run ID", 'pdf');
                    end;
                }


            }
        }
    }

    trigger OnOpenPage()
    begin
        RefreshAccessState();
    end;

    var
        ShowPremiumDetails: Boolean;

    local procedure RefreshAccessState()
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        ShowPremiumDetails := false;
        if not Setup.Get('SETUP') then
            exit;
        if Setup.Registered then
            ApiClient.RefreshLicenseStatus(Setup);
        ShowPremiumDetails := Setup."Can View Issue Details";
    end;
}
