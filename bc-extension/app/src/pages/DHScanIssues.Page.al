page 53126 "DH Scan Issues"
{
    PageType = List;
    SourceTable = "DH Scan Issue";
    Permissions = tabledata "DH Scan Issue" = R;
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'Scan Issues';
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;

    layout
    {
        area(Content)
        {
            group(EmptyState)
            {
                ShowCaption = false;
                Visible = EmptyStateVisible;
                field(EmptyStateText; EmptyStateTxt)
                {
                    ApplicationArea = All;
                    ShowCaption = false;
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains that no findings are available.';
                }
            }
            repeater(Issues)
            {
                field("Title"; CatalogTitle)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Title.';
                }
                field("Severity"; Rec."Severity")
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
                }
                field("Premium"; Rec."Premium Only")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Premium.';
                }
                field("Issue Code"; Rec."Issue Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issue Code.';
                }
            }
        }
    }

    trigger OnAfterGetRecord()
    begin
        UpdateCatalogText();
        EmptyStateVisible := false;
        SeverityStyle := GetSeverityStyle();
        ImpactTxt := GetImpactText();
    end;

    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
        EnsureSortFields();
        Rec.SetCurrentKey("Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
        EmptyStateTxt := NoFindingsLbl;
        EmptyStateVisible := Rec.IsEmpty();
    end;

    var
        CatalogTitle: Text[250];
        CatalogRecommendation: Text[2048];
        EmptyStateTxt: Text[100];
        EmptyStateVisible: Boolean;
        NoFindingsLbl: Label 'No findings are available.';
        SeverityStyle: Text[30];
        ImpactTxt: Text[50];

    local procedure EnsureSortFields()
    var
        Issue: Record "DH Scan Issue";
        NeedsUpdate: Boolean;
    begin
        Issue.CopyFilters(Rec);
        if Issue.FindSet() then
            repeat
                NeedsUpdate := false;

                if Issue."Severity Sort Order" <> GetSeveritySortOrder(Issue."Severity") then begin
                    Issue."Severity Sort Order" := GetSeveritySortOrder(Issue."Severity");
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
        case LowerCase(Rec."Severity") of
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

    local procedure UpdateCatalogText()
    var
        CheckCatalogMgt: Codeunit "DH Check Catalog Mgt.";
    begin
        CatalogTitle := CheckCatalogMgt.ResolveTitle(Rec."Issue Code");
        CatalogRecommendation := CheckCatalogMgt.ResolveRecommendation(Rec."Issue Code");
    end;
}
