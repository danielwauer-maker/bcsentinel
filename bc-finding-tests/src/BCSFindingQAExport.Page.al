page 53461 "BCS Finding QA Export"
{
    PageType = List;
    SourceTable = "DH Deep Scan Run";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'BCSentinel Finding QA Evidence';
    Editable = false;
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Runs)
            {
                field(RunId; Rec."Run ID") { ToolTip = 'Specifies the selected scan run.'; }
                field(Status; Rec.Status) { ToolTip = 'Specifies the scan status.'; }
                field(Findings; Rec."Issues Count") { ToolTip = 'Specifies the persisted finding row count.'; }
            }
        }
    }
    actions
    {
        area(Processing)
        {
            action(DownloadEvidence)
            {
                Caption = 'Download group evidence';
                ToolTip = 'Downloads finding identities, counts and impacts without changing the scan.';
                Image = Export;
                trigger OnAction()
                begin
                    ExportEvidence();
                end;
            }
        }
    }
    trigger OnOpenPage()
    begin
        RequireQASandbox();
    end;

    local procedure RequireQASandbox()
    var
        EnvironmentInformation: Codeunit "Environment Information";
    begin
        if not EnvironmentInformation.IsSaaS() or not EnvironmentInformation.IsSandbox() or EnvironmentInformation.IsProduction() then
            Error(QAOnlyErr);
        if CompanyName() <> 'BCS-FINDING-QA' then
            Error(QAOnlyErr);
    end;

    local procedure ExportEvidence()
    var
        Finding: Record "DH Deep Scan Finding";
        TempBlob: Codeunit "Temp Blob";
        Evidence: JsonObject;
        Row: JsonObject;
        Rows: JsonArray;
        OutputStream: OutStream;
        InputStream: InStream;
        FileName: Text;
        Occurrences: BigInteger;
        Impact: Decimal;
    begin
        RequireQASandbox();
        Evidence.Add('company', CompanyName());
        Evidence.Add('run_id', Rec."Run ID");
        Evidence.Add('status', Format(Rec.Status));
        Evidence.Add('sync_status', Format(Rec."Backend Sync Status"));
        Evidence.Add('score', Rec."Deep Score");
        Evidence.Add('checks', Rec."Checks Count");
        Evidence.Add('run_impact_eur', Rec."Estimated Loss (EUR)");
        Finding.SetRange("Deep Scan Entry No.", Rec."Entry No.");
        if Finding.FindSet() then
            repeat
                Clear(Row);
                Row.Add('finding_id', LowerCase(DelChr(Format(Finding.SystemId), '=', '{}')));
                Row.Add('entry_no', Finding."Entry No.");
                Row.Add('check_id', Finding."Issue Code");
                Row.Add('group_key', Finding."Group Key");
                Row.Add('count', Finding."Affected Count");
                Row.Add('impact_eur', Finding."Estimated Impact (EUR)");
                Rows.Add(Row);
                Occurrences += Finding."Affected Count";
                Impact += Finding."Estimated Impact (EUR)";
            until Finding.Next() = 0;
        Evidence.Add('rows', Rows);
        Evidence.Add('row_count', Rows.Count());
        Evidence.Add('occurrences', Occurrences);
        Evidence.Add('row_impact_eur', Impact);
        TempBlob.CreateOutStream(OutputStream, TextEncoding::UTF8);
        Evidence.WriteTo(OutputStream);
        TempBlob.CreateInStream(InputStream, TextEncoding::UTF8);
        FileName := 'BCSentinel-Finding-QA.json';
        DownloadFromStream(InputStream, '', '', '', FileName);
    end;

    var
        QAOnlyErr: Label 'This read-only export requires the BCS-FINDING-QA company in a SaaS sandbox.';
}
