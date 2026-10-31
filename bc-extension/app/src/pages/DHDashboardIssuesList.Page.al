page 53161 "DH Dashboard Issues List"
{
    PageType = List;
    SourceTable = "DH Dashboard Issue";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'BCSentinel Issues';
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Issues)
            {
                field(Severity; Rec.Severity)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Severity.';
                    StyleExpr = SeverityStyle;
                }

                field(Title; Rec.Title)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Title.';
                    Visible = ShowPremiumDetails;

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        EnsureDetailedAccess();
                        IssueDrilldownMgt.OpenDashboardIssue(Rec);
                    end;
                }

                field("Affected Count"; Rec."Affected Count")
                {
                    ApplicationArea = All;
                    Caption = 'Count';
                    ToolTip = 'Specifies Count.';

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        EnsureDetailedAccess();
                        IssueDrilldownMgt.OpenDashboardIssue(Rec);
                    end;
                }

                field("Estimated Impact (EUR)"; Rec."Estimated Impact (EUR)")
                {
                    ApplicationArea = All;
                    Caption = 'Impact EUR';
                    ToolTip = 'Specifies Impact EUR.';
                    Visible = ShowPremiumDetails;
                }

                field("Recommendation Review"; Rec."Recommendation Preview")
                {
                    ApplicationArea = All;
                    Caption = 'Recommendation';
                    ToolTip = 'Specifies Recommendation.';
                    Visible = ShowPremiumDetails;
                }

                field(Access; AccessText)
                {
                    ApplicationArea = All;
                    Caption = 'Access';
                    ToolTip = 'Specifies Access.';
                }
            }
        }
    }

    trigger OnAfterGetRecord()
    begin
        SeverityStyle := GetSeverityStyle();
    end;

    trigger OnOpenPage()
    begin
        RefreshAccessState();
        EnsureSortFields();
        Rec.SetCurrentKey("Dashboard Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
    end;

    var
        SeverityStyle: Text[30];
        ShowPremiumDetails: Boolean;
        AccessText: Text[80];

    local procedure RefreshAccessState()
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        ShowPremiumDetails := false;
        AccessText := 'Assessment required for detailed findings';

        if not Setup.Get('SETUP') then
            exit;

        if Setup.Registered then
            ApiClient.RefreshLicenseStatus(Setup);

        ShowPremiumDetails := Setup."Can View Issue Details";
        if ShowPremiumDetails then
            AccessText := 'Unlocked';
    end;

    local procedure EnsureDetailedAccess()
    begin
        if not ShowPremiumDetails then
            Error('Detailed findings are available with an active Assessment, Validation, or Monitoring access period.');
    end;

    local procedure EnsureSortFields()
    var
        Issue: Record "DH Dashboard Issue";
        NeedsUpdate: Boolean;
    begin
        Issue.CopyFilters(Rec);
        if Issue.FindSet() then
            repeat
                NeedsUpdate := false;

                if Issue."Severity Sort Order" <> GetSeveritySortOrder(Issue.Severity) then begin
                    Issue."Severity Sort Order" := GetSeveritySortOrder(Issue.Severity);
                    NeedsUpdate := true;
                end;

                if Issue."Affected Count Sort Value" <> -Issue."Affected Count" then begin
                    Issue."Affected Count Sort Value" := -Issue."Affected Count";
                    NeedsUpdate := true;
                end;

                if NeedsUpdate then
                    Issue.Modify(true);
            until Issue.Next() = 0;
    end;

    local procedure GetSeveritySortOrder(SeverityValue: Code[20]): Integer
    begin
        case LowerCase(SeverityValue) of
            'high':
                exit(1);
            'medium':
                exit(2);
            'low':
                exit(3);
        end;

        exit(99);
    end;

    local procedure GetSeverityStyle(): Text
    begin
        case LowerCase(Rec.Severity) of
            'high':
                exit('Unfavorable');
            'medium':
                exit('Ambiguous');
            'low':
                exit('Favorable');
        end;

        exit('Standard');
    end;
}
