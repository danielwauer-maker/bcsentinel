page 53135 "DH Dashboard Issues"
{
    PageType = ListPart;
    SourceTable = "DH Dashboard Issue";
    Permissions = tabledata "DH Dashboard Issue" = R;
    ApplicationArea = All;
    UsageCategory = None;
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
                    Caption = 'Severity';
                    ToolTip = 'Specifies the severity assigned to the finding.';
                    StyleExpr = SeverityStyle;
                }

                field(Title; CatalogTitle)
                {
                    ApplicationArea = All;
                    Caption = 'Finding';
                    ToolTip = 'Specifies the title of the detected data-quality finding.';

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        IssueDrilldownMgt.OpenDashboardIssue(Rec);
                    end;
                }

                field("Affected Count"; Rec."Affected Count")
                {
                    ApplicationArea = All;
                    Caption = 'Affected Records';
                    ToolTip = 'Specifies how many records are affected by the finding.';

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        IssueDrilldownMgt.OpenDashboardIssue(Rec);
                    end;
                }

                field(ImpactDisplay; ImpactTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Estimated Impact';
                    ToolTip = 'Specifies the estimated financial impact in the company currency.';
                }

                field("Recommendation Review"; CatalogRecommendation)
                {
                    ApplicationArea = All;
                    Caption = 'Recommendation';
                    ToolTip = 'Specifies the recommended action for resolving the finding.';
                    Visible = ShowPremiumDetails;
                }

                field(Access; AccessText)
                {
                    ApplicationArea = All;
                    Caption = 'Access';
                    ToolTip = 'Specifies whether the detailed recommendation is available.';
                }
            }
        }
    }

    trigger OnAfterGetRecord()
    begin
        UpdateCatalogText();
        UpdateAccessState();
        SeverityStyle := GetSeverityStyle();
        ImpactTxt := GetImpactText();
    end;

    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
        EnsureSortFields();
        UpdateAccessState();
        Rec.SetCurrentKey("Dashboard Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
    end;

    var
        CatalogTitle: Text[250];
        CatalogRecommendation: Text[2048];
        SeverityStyle: Text[30];
        ShowPremiumDetails: Boolean;
        AccessText: Text[80];
        ImpactTxt: Text[50];

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
            'critical':
                exit(0);
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
            'critical':
                exit('Unfavorable');
            'high':
                exit('Unfavorable');
            'medium':
                exit('Ambiguous');
            'low':
                exit('Favorable');
        end;

        exit('Standard');
    end;

    local procedure UpdateAccessState()
    var
        Setup: Record "DH Setup";
        StartAssessmentLbl: Label 'Start Assessment for detailed insights';
        UnlockedLbl: Label 'Unlocked';
    begin
        ShowPremiumDetails := false;
        AccessText := StartAssessmentLbl;

        if Setup.Get('SETUP') then
            if Setup."Premium Enabled" then begin
                ShowPremiumDetails := true;
                AccessText := UnlockedLbl;
            end;
    end;

    trigger OnAfterGetCurrRecord()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
    end;

    local procedure GetImpactText(): Text[50]
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.FormatLocalAmount(Rec."Estimated Impact (EUR)"));
    end;

    procedure SetDashboardScanEntryNo(DashboardScanEntryNo: Integer)
    begin
        Rec.Reset();
        Rec.SetRange("Dashboard Scan Entry No.", DashboardScanEntryNo);
        EnsureSortFields();
        Rec.SetCurrentKey("Dashboard Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
        CurrPage.Update(false);
    end;

    local procedure UpdateCatalogText()
    var
        CheckCatalogMgt: Codeunit "DH Check Catalog Mgt.";
    begin
        CatalogTitle := CheckCatalogMgt.ResolveTitle(Rec."Issue Code");
        CatalogRecommendation := CheckCatalogMgt.ResolveRecommendation(Rec."Issue Code");
    end;
}
