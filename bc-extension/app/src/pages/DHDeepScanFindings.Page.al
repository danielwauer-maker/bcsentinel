page 53131 "DH Deep Scan Findings"
{
    PageType = ListPart;
    SourceTable = "DH Deep Scan Finding";
    Permissions = tabledata "DH Deep Scan Finding" = R;
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

                field(Title; CatalogTitle)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Title.';

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
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

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        IssueDrilldownMgt.OpenDeepScanFinding(Rec);
                    end;
                }

                field(ImpactDisplay; ImpactTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Impact';
                    ToolTip = 'Specifies the estimated impact in local currency.';
                }

                field("Recommendation Preview"; CatalogRecommendation)
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
        Rec.SetCurrentKey("Deep Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
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
        BuyFullAnalysisLbl: Label 'Buy Full Analysis';
        UnlockedLbl: Label 'Unlocked';
    begin
        ShowPremiumDetails := false;
        AccessText := BuyFullAnalysisLbl;

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


    procedure SetDeepScanEntryNo(DeepScanEntryNo: Integer)
    begin
        Rec.Reset();
        Rec.SetRange("Deep Scan Entry No.", DeepScanEntryNo);
        EnsureSortFields();
        Rec.SetCurrentKey("Deep Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
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
