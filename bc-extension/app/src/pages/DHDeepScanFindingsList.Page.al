page 53160 "DH Deep Scan Findings List"
{
    PageType = List;
    SourceTable = "DH Deep Scan Finding";
    SourceTableTemporary = true;
    Permissions = tabledata "DH Deep Scan Finding" = R;
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'Deep Scan Findings';
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
            repeater(Findings)
            {
                field(Category; Rec.Category)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the finding category.';
                }

                field(Title; CatalogTitle)
                {
                    ApplicationArea = All;
                    Caption = 'Finding';
                    ToolTip = 'Specifies the title of the detected data-quality finding.';
                    Visible = ShowPremiumDetails;

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        if not ShowPremiumDetails then
                            exit;

                        IssueDrilldownMgt.OpenDeepScanFinding(Rec);
                    end;
                }

                field(Severity; Rec.Severity)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the severity assigned to the finding.';
                    StyleExpr = SeverityStyle;
                }

                field("Affected Count"; Rec."Affected Count")
                {
                    ApplicationArea = All;
                    Caption = 'Affected Records';
                    ToolTip = 'Specifies the affected record count. In Free mode this is aggregated by category and severity.';

                    trigger OnDrillDown()
                    var
                        IssueDrilldownMgt: Codeunit "DH Issue Drilldown Mgt.";
                    begin
                        if not ShowPremiumDetails then
                            exit;

                        IssueDrilldownMgt.OpenDeepScanFinding(Rec);
                    end;
                }

                field(ImpactDisplay; ImpactTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Impact';
                    ToolTip = 'Shows the estimated financial impact for Full Analysis. In Free mode the amount is protected.';
                }

                field(Access; AccessText)
                {
                    ApplicationArea = All;
                    Caption = 'Access';
                    ToolTip = 'Specifies whether detailed findings are available.';
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
        UpdateAccessState();
        LoadPageData();
        EmptyStateTxt := NoFindingsLbl;
        EmptyStateVisible := Rec.IsEmpty();
    end;

    var
        CatalogTitle: Text[250];
        EmptyStateTxt: Text[100];
        EmptyStateVisible: Boolean;
        NoFindingsLbl: Label 'No findings are available.';
        SeverityStyle: Text[30];
        ShowPremiumDetails: Boolean;
        AccessText: Text[80];
        ImpactTxt: Text[50];
        ProtectedImpactLbl: Label '•••• EUR';

    local procedure LoadPageData()
    var
        SourceFinding: Record "DH Deep Scan Finding";
        NextTempEntryNo: Integer;
    begin
        SourceFinding.CopyFilters(Rec);
        Rec.Reset();
        Rec.DeleteAll();
        NextTempEntryNo := 1;

        if SourceFinding.FindSet() then
            repeat
                if ShowPremiumDetails then begin
                    Rec := SourceFinding;
                    Rec.Insert();
                end else
                    AddFreeAggregate(SourceFinding, NextTempEntryNo);
            until SourceFinding.Next() = 0;

        Rec.Reset();
        Rec.SetCurrentKey("Deep Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value");
        Rec.Ascending(true);
    end;

    local procedure AddFreeAggregate(SourceFinding: Record "DH Deep Scan Finding"; var NextTempEntryNo: Integer)
    begin
        Rec.Reset();
        Rec.SetRange(Category, SourceFinding.Category);
        Rec.SetRange(Severity, SourceFinding.Severity);

        if Rec.FindFirst() then begin
            Rec."Affected Count" += SourceFinding."Affected Count";
            Rec."Affected Count Sort Value" := -Rec."Affected Count";
            Rec.Modify();
        end else begin
            Rec.Init();
            Rec."Entry No." := NextTempEntryNo;
            NextTempEntryNo += 1;
            Rec."Deep Scan Entry No." := SourceFinding."Deep Scan Entry No.";
            Rec.Category := SourceFinding.Category;
            Rec.Severity := SourceFinding.Severity;
            Rec."Affected Count" := SourceFinding."Affected Count";
            Rec."Severity Sort Order" := GetSeveritySortOrder(SourceFinding.Severity);
            Rec."Affected Count Sort Value" := -SourceFinding."Affected Count";
            Rec.Insert();
        end;

        Rec.Reset();
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
        BuyFullAnalysisLbl: Label 'Start Assessment for detailed insights';
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
        if not ShowPremiumDetails then
            exit(ProtectedImpactLbl);

        exit(CurrencyMgt.FormatLocalAmount(Rec."Estimated Impact (EUR)"));
    end;

    local procedure UpdateCatalogText()
    var
        CheckCatalogMgt: Codeunit "DH Check Catalog Mgt.";
    begin
        Clear(CatalogTitle);
        if not ShowPremiumDetails then
            exit;

        CatalogTitle := CheckCatalogMgt.ResolveTitle(Rec."Issue Code");
    end;
}
