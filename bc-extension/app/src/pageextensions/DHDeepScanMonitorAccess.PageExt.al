pageextension 53202 "DH Deep Scan Monitor Access" extends "DH Deep Scan Monitor"
{
    layout
    {
        modify(Headline)
        {
            Visible = ShowPremiumDetails;
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
            Visible = ShowPremiumDetails;
        }
        modify(OpenExecutivePdf)
        {
            Visible = ShowPremiumDetails;
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
