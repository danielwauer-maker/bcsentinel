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
            action(SetRegistrationInvite)
            {
                Caption = 'Set registration invite';
                ToolTip = 'Stores the temporary registration invite only for BCS-FINDING-QA in a SaaS sandbox.';
                Image = Setup;
                trigger OnAction()
                begin
                    ApplyRegistrationInvite();
                end;
            }
            action(ClearRegistrationInvite)
            {
                Caption = 'Clear registration invite';
                ToolTip = 'Clears the temporary registration invite from the BCS-FINDING-QA setup.';
                Image = Delete;
                trigger OnAction()
                begin
                    RemoveRegistrationInvite();
                end;
            }
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

    local procedure ApplyRegistrationInvite()
    var
        InviteDialog: Page "BCS Finding QA Invite";
        InviteMgt: Codeunit "BCS Finding QA Invite Mgt.";
        InviteCode: Text[100];
    begin
        RequireQASandbox();
        Clear(InviteDialog);
        if InviteDialog.RunModal() <> Action::OK then
            exit;

        InviteCode := InviteDialog.GetInviteCode();
        InviteMgt.SetRegistrationInvite(InviteCode);
        Message(InviteStoredMsg);
    end;

    local procedure RemoveRegistrationInvite()
    var
        InviteMgt: Codeunit "BCS Finding QA Invite Mgt.";
    begin
        RequireQASandbox();
        if not Confirm(ClearInviteQst, false) then
            exit;

        InviteMgt.ClearRegistrationInvite();
        Message(InviteClearedMsg);
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
        QAOnlyErr: Label 'This QA helper requires the BCS-FINDING-QA company in a SaaS sandbox.';
        ClearInviteQst: Label 'Clear the temporary registration invite code from BCS-FINDING-QA?';
        InviteStoredMsg: Label 'The temporary registration invite code was stored for BCS-FINDING-QA.';
        InviteClearedMsg: Label 'The temporary registration invite code was cleared from BCS-FINDING-QA.';
}
