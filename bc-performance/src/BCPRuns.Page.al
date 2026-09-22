page 53401 "BCP Runs"
{
    Caption = 'INTERNAL QA - Performance runs';
    PageType = List;
    SourceTable = "BCP Run";
    ApplicationArea = All;
    UsageCategory = Administration;
    Editable = false;
    layout
    {
        area(Content)
        {
            repeater(Runs)
            {
                field(RunId; Rec."Run ID") { ApplicationArea = All; ToolTip = 'Identifies this company-scoped generator run.'; }
                field(Profile; Rec.Profile) { ApplicationArea = All; ToolTip = 'Shows the dataset profile.'; }
                field(Seed; Rec.Seed) { ApplicationArea = All; ToolTip = 'Shows the deterministic seed.'; }
                field(ErrorRate; Rec."Error Rate") { ApplicationArea = All; ToolTip = 'Shows the requested scenario percentage.'; }
                field(Status; Rec.Status) { ApplicationArea = All; ToolTip = 'Shows the last committed run status. Refresh to see updates.'; }
                field(Phase; Rec."Current Phase") { ApplicationArea = All; ToolTip = 'Shows the last committed entity phase.'; }
                field(Progress; Rec.Progress()) { ApplicationArea = All; Caption = 'Progress (%)'; ToolTip = 'Shows generated business records as a percentage of the target.'; }
                field(Target; Rec.TargetCount()) { ApplicationArea = All; Caption = 'Target business records'; ToolTip = 'Excludes supporting and ownership records.'; }
                field(Customers; Rec.Customers) { ApplicationArea = All; ToolTip = 'Shows committed customers.'; }
                field(Vendors; Rec.Vendors) { ApplicationArea = All; ToolTip = 'Shows committed vendors.'; }
                field(Items; Rec.Items) { ApplicationArea = All; ToolTip = 'Shows committed items.'; }
                field(Scenarios; Rec."Expected Scenarios") { ApplicationArea = All; ToolTip = 'Shows injected problems, not the number of aggregate finding rows.'; }
                field(StartedAt; Rec."Started At") { ApplicationArea = All; ToolTip = 'Shows the generation start time.'; }
                field(EndedAt; Rec."Ended At") { ApplicationArea = All; ToolTip = 'Shows the generation end time.'; }
                field(Duration; Elapsed) { ApplicationArea = All; Caption = 'Duration'; ToolTip = 'Shows elapsed generation wall time including interruptions.'; }
                field(Throughput; RecordsPerSecond) { ApplicationArea = All; Caption = 'Records/sec'; ToolTip = 'Shows average business records per second of wall time.'; }
                field(Batch; Rec."Current Batch") { ApplicationArea = All; ToolTip = 'Shows committed generation batches.'; }
                field(Failures; Rec."Failed Batches") { ApplicationArea = All; ToolTip = 'Shows caught batch failures, including cleanup.'; }
                field(ErrorText; Rec."Error Text") { ApplicationArea = All; ToolTip = 'Shows the most recent failure diagnostic.'; }
                field(Cleaned; Rec."Cleanup Count") { ApplicationArea = All; ToolTip = 'Shows deleted business and support records.'; }
            }
        }
    }
    actions
    {
        area(Processing)
        {
            action(NewRun)
            {
                Caption = 'Create DEV / LARGE / XL / STRESS / Custom';
                ApplicationArea = All;
                Image = New;
                ToolTip = 'Configure and create a pending sandbox run.';
                trigger OnAction()
                var
                    NewRun: Page "BCP New Run";
                begin
                    if NewRun.RunModal() = Action::OK then
                        if Confirm(CreateQst, false) then begin
                            NewRun.Create();
                            CurrPage.Update(false);
                        end;
                end;
            }
            action(Resume)
            {
                Caption = 'Start / resume';
                ApplicationArea = All;
                Image = Start;
                ToolTip = 'Run committed batches until completion. Interrupted runs can resume from their checkpoint.';
                trigger OnAction()
                begin
                    if Confirm(StartQst, false, Rec."Run ID", Rec.TargetCount()) then
                        Management.Execute(Rec."Run ID", false);
                    CurrPage.Update(false);
                end;
            }
            action(NextBatch)
            {
                Caption = 'Run one batch';
                ApplicationArea = All;
                Image = NextRecord;
                ToolTip = 'Generate one bounded batch for smoke tests or controlled progress.';
                trigger OnAction()
                begin
                    if Confirm(StartQst, false, Rec."Run ID", Rec.TargetCount()) then
                        Management.Execute(Rec."Run ID", true);
                    CurrPage.Update(false);
                end;
            }
            action(CancelRun)
            {
                Caption = 'Cancel run';
                ApplicationArea = All;
                Image = Cancel;
                ToolTip = 'Cancel after the current transaction releases its lock. Generated data remains tracked.';
                trigger OnAction()
                begin
                    Management.Cancel(Rec."Run ID");
                    CurrPage.Update(false);
                end;
            }
            action(PreviewCleanup)
            {
                Caption = 'Preview cleanup';
                ApplicationArea = All;
                Image = View;
                ToolTip = 'Count tracked candidates. Identity and dependency checks run again before each deletion.';
                trigger OnAction()
                begin
                    Message(PreviewMsg, Cleanup.Preview(Rec."Run ID"));
                end;
            }
            action(CleanupRun)
            {
                Caption = 'Cleanup run';
                ApplicationArea = All;
                Image = Delete;
                ToolTip = 'Delete only unchanged owned records, using standard business delete triggers.';
                trigger OnAction()
                begin
                    if Confirm(CleanupQst, false, Cleanup.Preview(Rec."Run ID")) then
                        Cleanup.Clean(Rec."Run ID");
                    CurrPage.Update(false);
                end;
            }
            action(CleanupAll)
            {
                Caption = 'Cleanup all runs';
                ApplicationArea = All;
                Image = Delete;
                ToolTip = 'Clean terminal runs in this company. Cancel active runs first. No company or setup data is deleted.';
                trigger OnAction()
                var
                    GenerationRun: Record "BCP Run";
                begin
                    if not Confirm(CleanupQst, false, Cleanup.Preview(0)) then
                        exit;
                    if GenerationRun.FindSet() then
                        repeat
                            if GenerationRun.Status <> GenerationRun.Status::Cleaned then
                                Cleanup.Clean(GenerationRun."Run ID");
                        until GenerationRun.Next() = 0;
                    CurrPage.Update(false);
                end;
            }
        }
    }

    trigger OnOpenPage()
    var
        Policy: Codeunit "BCP Policy";
    begin
        Policy.RequireSandbox();
    end;

    trigger OnAfterGetRecord()
    var
        EndTime: DateTime;
    begin
        Elapsed := 0;
        RecordsPerSecond := 0;
        if Rec."Started At" = 0DT then
            exit;
        EndTime := Rec."Ended At";
        if EndTime = 0DT then
            EndTime := CurrentDateTime();
        Elapsed := EndTime - Rec."Started At";
        if Elapsed > 0 then
            RecordsPerSecond := Round(Rec.BusinessCount() * 1000.0 / Elapsed, 0.01);
    end;

    var
        Management: Codeunit "BCP Management";
        Cleanup: Codeunit "BCP Cleanup";
        Elapsed: Duration;
        RecordsPerSecond: Decimal;
        CreateQst: Label 'INTERNAL QA ONLY. Create synthetic data in this disposable sandbox company?';
        StartQst: Label 'Run %1 targets %2 business records. Start or resume sandbox generation?', Comment = '%1 = run id, %2 = target count';
        CleanupQst: Label 'Delete up to %1 tracked records in this sandbox company? Changed or referenced data will be refused. This cannot be undone.', Comment = '%1 = candidate count';
        PreviewMsg: Label '%1 tracked cleanup candidates including supporting records. This is a count preview, not proof of deletability. Each deletion rechecks identity, modification and references.', Comment = '%1 = candidate count';
}
