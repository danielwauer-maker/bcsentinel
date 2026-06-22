page 53195 "DH Scan Checks"
{
    PageType = List;
    SourceTable = "DH Scan Check Selection";
    Caption = 'Scan Checks';
    ApplicationArea = All;
    UsageCategory = Administration;
    InsertAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Checks)
            {
                field(Enabled; Rec.Enabled)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies whether this check is considered by Monitoring scans.';
                }
                field("Check Code"; Rec."Check Code")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the technical check code.';
                }
                field(Module; Rec."Module")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the Business Central module or area.';
                }
                field(Name; Rec.Name)
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the check name.';
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the check description.';
                }
                field("Risk Level"; Rec."Risk Level")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the risk level.';
                }
                field("Last Run At"; Rec."Last Run At")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies when this check last produced a scan result.';
                }
                field("Last Finding Count"; Rec."Last Finding Count")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the last finding count for this check.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(RefreshSelection)
            {
                Caption = 'Refresh Selection';
                ToolTip = 'Updates the local list of available BCSentinel scan checks.';
                ApplicationArea = All;
                Image = Refresh;

                trigger OnAction()
                var
                    ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
                begin
                    ScanCheckMgt.EnsureMonitoringAccess(true);
                    ScanCheckMgt.EnsureDefaultChecks();
                    CurrPage.Update(false);
                end;
            }
            action(EnableAll)
            {
                Caption = 'Enable All';
                ToolTip = 'Enables all scan checks.';
                ApplicationArea = All;
                Image = Approve;

                trigger OnAction()
                var
                    ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
                begin
                    ScanCheckMgt.EnsureMonitoringAccess(false);
                    ScanCheckMgt.EnableAll();
                    CurrPage.Update(false);
                end;
            }
            action(DisableAll)
            {
                Caption = 'Disable All';
                ToolTip = 'Disables all scan checks.';
                ApplicationArea = All;
                Image = Cancel;

                trigger OnAction()
                var
                    ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
                begin
                    ScanCheckMgt.EnsureMonitoringAccess(false);
                    ScanCheckMgt.DisableAll();
                    CurrPage.Update(false);
                end;
            }
            action(RestoreDefaults)
            {
                Caption = 'Restore Defaults';
                ToolTip = 'Restores the default scan check selection.';
                ApplicationArea = All;
                Image = Restore;

                trigger OnAction()
                var
                    ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
                begin
                    ScanCheckMgt.EnsureMonitoringAccess(false);
                    ScanCheckMgt.RestoreDefaults();
                    CurrPage.Update(false);
                end;
            }
        }
    }

    trigger OnOpenPage()
    var
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
    begin
        ScanCheckMgt.EnsureMonitoringAccess(true);
        ScanCheckMgt.EnsureDefaultChecks();
        Rec.SetCurrentKey("Sort Order", "Module", "Check Code");
    end;
}
