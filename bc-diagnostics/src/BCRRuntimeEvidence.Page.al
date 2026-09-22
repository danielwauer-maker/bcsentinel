page 53451 "BCR Runtime Evidence"
{
    PageType = Card;
    ApplicationArea = All;
    UsageCategory = Administration;
    Caption = 'BCSentinel Runtime Evidence';
    Editable = false;
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            group(ExportScope)
            {
                Caption = 'Read-only DEV evidence';
                field(Scope; ScopeText)
                {
                    ApplicationArea = All;
                    Caption = 'Scope';
                    ToolTip = 'Exports the completed DEV scan and aggregate ownership evidence without changing business or scan data.';
                    MultiLine = true;
                }
            }
        }
    }
    actions
    {
        area(Processing)
        {
            action(DownloadEvidence)
            {
                ApplicationArea = All;
                Caption = 'Download DEV evidence';
                ToolTip = 'Downloads a JSON file of persisted findings, run totals and current aggregate scenario counts. No scan or generator is started.';
                Image = Export;
                trigger OnAction()
                var
                    EvidenceExport: Codeunit "BCR Evidence Export";
                begin
                    EvidenceExport.DownloadEvidence();
                end;
            }
        }
    }
    trigger OnOpenPage()
    begin
        ScopeText := ScopeLbl;
    end;

    var
        ScopeText: Text;
        ScopeLbl: Label 'BCS-PERF-DEV only. Completed scan from 16 September 2026; generator Run 1. Read-only export; no cleanup, rerun or repair.';
}
