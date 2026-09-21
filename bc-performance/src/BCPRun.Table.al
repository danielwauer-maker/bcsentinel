table 53400 "BCP Run"
{
    Caption = 'QA generation run';
    DataClassification = SystemMetadata;
    fields
    {
        field(1; "Run ID"; Integer) { AutoIncrement = true; Caption = 'Run ID'; }
        field(2; Profile; Enum "BCP Profile") { Caption = 'Profile'; }
        field(3; Seed; Integer) { Caption = 'Seed'; }
        field(4; "Error Rate"; Integer) { Caption = 'Error rate (%)'; }
        field(5; "Batch Size"; Integer) { Caption = 'Batch size'; }
        field(6; Status; Enum "BCP Status") { Caption = 'Status'; }
        field(7; "Customer Target"; Integer) { Caption = 'Customer target'; }
        field(8; "Vendor Target"; Integer) { Caption = 'Vendor target'; }
        field(9; "Item Target"; Integer) { Caption = 'Item target'; }
        field(10; Customers; Integer) { Caption = 'Customers'; }
        field(11; Vendors; Integer) { Caption = 'Vendors'; }
        field(12; Items; Integer) { Caption = 'Items'; }
        field(13; "Started At"; DateTime) { Caption = 'Started at'; }
        field(14; "Ended At"; DateTime) { Caption = 'Ended at'; }
        field(15; "Failed Batches"; Integer) { Caption = 'Failed batches'; }
        field(16; "Error Text"; Text[2048]) { Caption = 'Error text'; }
        field(17; "Schema Version"; Integer) { Caption = 'Schema version'; }
        field(18; "Customer Config"; Text[2048]) { Caption = 'Customer configuration snapshot'; }
        field(19; "Vendor Config"; Text[2048]) { Caption = 'Vendor configuration snapshot'; }
        field(20; "Item Config"; Text[2048]) { Caption = 'Item configuration snapshot'; }
        field(21; "Current Batch"; Integer) { Caption = 'Current batch'; }
        field(22; "Expected Scenarios"; Integer) { Caption = 'Injected scenarios'; }
        field(23; "Cleanup Count"; Integer) { Caption = 'Deleted records including support'; }
        field(24; "Last Batch At"; DateTime) { Caption = 'Last batch at'; }
        field(25; "Current Phase"; Text[30]) { Caption = 'Current phase'; }
    }
    keys { key(PK; "Run ID") { Clustered = true; } }

    procedure BusinessCount(): Integer
    begin
        exit(Customers + Vendors + Items);
    end;

    procedure TargetCount(): Integer
    begin
        exit("Customer Target" + "Vendor Target" + "Item Target");
    end;

    procedure Progress(): Decimal
    begin
        if TargetCount() = 0 then
            exit(0);
        exit(Round(100.0 * BusinessCount() / TargetCount(), 0.01));
    end;
}
