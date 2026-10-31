page 53131 "DH Deep Scan Findings"
{
    PageType = ListPart;
    SourceTable = "DH Deep Scan Finding";
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'Deep Scan Findings';
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Findings)
            {
                field(Category; Rec.Category)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Category.';
                }

                field("Issue Code"; Rec."Issue Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issue Code.';
                    Visible = ShowPremiumDetails;
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
                        EnsureIssueDetailsAllowed();
                        IssueDrilldownMgt.OpenDeepScanFinding(Rec);
                    end;
                }

                field(Severity; Rec.Severity)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Severity.';
                    StyleExpr = SeverityStyle;
                }

                field("Affected Count"; Rec."Affected Count")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Affected Count.';
                }

                field("Estimated Impact (EUR)"; Rec."Estimated Impact (EUR)")
                {
                    ApplicationArea = All;
                    Caption = 'Impact EUR';
                    ToolTip = 'Specifies Impact EUR.';
                    Visible = ShowPremiumDetails;
                }

                field("Recommendation Preview"; Rec."Recommendation Preview")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Recommendation Preview.';
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
        UpdateAccessState(false);
        SeverityStyle := GetSeverityStyle();
    end;

    trigger OnOpenPage()
    begin
        EnsureSortFields();
        UpdateAccessState(true);
        Rec.SetCurrentKey("Deep Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
    end;

    var
        SeverityStyle: Text[30];
        ShowPremiumDetails: Boolean;
        AccessText: Text[80];

    local procedure EnsureSortFields()
    var
        Issue: Record "DH Deep Scan Finding";
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

    local procedure UpdateAccessState(RefreshFromBackend: Boolean)
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        ShowPremiumDetails := false;
        AccessText := 'Assessment required for detailed findings';

        if not Setup.Get('SETUP') then
            exit;

        if RefreshFromBackend and (Setup."Tenant ID" <> '') then
            ApiClient.RefreshLicenseStatus(Setup);

        ShowPremiumDetails := Setup."Can View Issue Details";
        if ShowPremiumDetails then
            AccessText := 'Unlocked';
    end;

    local procedure EnsureIssueDetailsAllowed()
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        if not Setup.Get('SETUP') then
            Error('BCSentinel setup was not found.');

        if Setup."Tenant ID" <> '' then
            ApiClient.RefreshLicenseStatus(Setup);

        if not Setup."Can View Issue Details" then
            Error('Detailed findings require an active Assessment, Validation Check, or Monitoring access.');
    end;

    procedure SetDeepScanEntryNo(DeepScanEntryNo: Integer)
    begin
        Rec.Reset();
        Rec.SetRange("Deep Scan Entry No.", DeepScanEntryNo);
        EnsureSortFields();
        Rec.SetCurrentKey("Deep Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
        CurrPage.Update(false);
    end;
}
