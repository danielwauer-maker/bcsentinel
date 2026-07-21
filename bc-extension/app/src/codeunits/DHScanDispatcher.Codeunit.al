codeunit 53135 "DH Scan Dispatcher"
{
    procedure StartScan(var Setup: Record "DH Setup")
    var
        DeepScanRun: Record "DH Deep Scan Run";
        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
        EntryNo: Integer;
    begin
        EnsureSetupReady(Setup);
        if Setup."Can Run Data Health Score" and not Setup."Data Health Score Completed" then begin
            EntryNo := DeepScanMgt.QueueDataHealthScore(Setup);
            if EntryNo = 0 then
                exit;
            Setup.Get('SETUP');
            Setup."Data Health Score Completed" := true;
            Setup."Can Run Data Health Score" := false;
            Setup.Modify(true);
        end else
            EntryNo := DeepScanMgt.QueueDeepScan(Setup);

        if EntryNo = 0 then
            exit;
        if DeepScanRun.Get(EntryNo) then
            Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
    end;

    local procedure EnsureSetupReady(var Setup: Record "DH Setup")
    begin
        if Setup."API Base URL" = '' then
            Error(ConfigureApiBaseUrlErr);

        if Setup."Tenant ID" = '' then
            Error(RegisterTenantErr);
    end;

    var
        ConfigureApiBaseUrlErr: Label 'Configure the API Base URL first.';
        RegisterTenantErr: Label 'Register the tenant first.';
}
