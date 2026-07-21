page 53121 "DH Issues Part"
{
    PageType = ListPart;
    SourceTable = "DH Dashboard Issue";
    Permissions = tabledata "DH Dashboard Issue" = R;
    ApplicationArea = All;
    Caption = 'Issues';
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;
    UsageCategory = None;

    layout
    {
        area(Content)
        {
            repeater(General)
            {
                field("Source Type"; Rec."Source Type")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Source Type.';
                }

                field(Title; CatalogTitle)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Title.';

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        IssueDrilldownMgt.OpenDashboardIssue(Rec);
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
                        IssueDrilldownMgt.OpenDashboardIssue(Rec);
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
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(OpenAllIssues)
            {
                Caption = 'Show All Issues';
                ToolTip = 'Runs Show All Issues.';
                ApplicationArea = All;
                Image = List;

                trigger OnAction()
                var
                    DashboardIssue: Record "DH Dashboard Issue";
                begin
                    DashboardIssue.SetRange("Dashboard Scan Entry No.", Rec."Dashboard Scan Entry No.");
                    Page.Run(Page::"DH Dashboard Issues List", DashboardIssue);
                end;
            }
        }
    }

    trigger OnAfterGetRecord()
    begin
        UpdateCatalogText();
        SeverityStyle := GetSeverityStyle();
        ImpactTxt := GetImpactText();
    end;

    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
        EnsureSortFields();
        Rec.SetCurrentKey("Dashboard Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
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

    var
        CatalogTitle: Text[250];
        CatalogRecommendation: Text[2048];
        SeverityStyle: Text[30];
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

