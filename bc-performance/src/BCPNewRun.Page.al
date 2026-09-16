page 53400 "BCP New Run"
{
    Caption = 'INTERNAL QA - New performance run';
    PageType = StandardDialog;
    SourceTable = "BCP Run";
    SourceTableTemporary = true;
    layout
    {
        area(Content)
        {
            group(Configuration)
            {
                Caption = 'Sandbox data generation';
                field(Profile; Rec.Profile)
                {
                    ApplicationArea = All;
                    ToolTip = 'Select the centrally defined dataset size, or Custom.';
                    trigger OnValidate()
                    begin
                        Policy.SetProfile(Rec);
                        CustomTargetsEditable := Rec.Profile = Rec.Profile::Custom;
                        CurrPage.Update(false);
                    end;
                }
                field(Seed; Rec.Seed) { ApplicationArea = All; ToolTip = 'Set the deterministic seed, from 0 to 1000000.'; }
                field(ErrorRate; Rec."Error Rate") { ApplicationArea = All; ToolTip = 'Choose 1, 5, 10 or 20 percent.'; }
                field(BatchSize; Rec."Batch Size") { ApplicationArea = All; ToolTip = 'Set 1 to 5000 business records per committed batch.'; }
                field(CustomerTarget; Rec."Customer Target") { ApplicationArea = All; Editable = CustomTargetsEditable; ToolTip = 'Set the customer count for Custom runs.'; }
                field(VendorTarget; Rec."Vendor Target") { ApplicationArea = All; Editable = CustomTargetsEditable; ToolTip = 'Set the vendor count for Custom runs.'; }
                field(ItemTarget; Rec."Item Target") { ApplicationArea = All; Editable = CustomTargetsEditable; ToolTip = 'Set the item count for Custom runs.'; }
                field(CustomerTemplate; CustomerNo) { ApplicationArea = All; Caption = 'Customer configuration source'; TableRelation = Customer; ToolTip = 'Select a configured QA customer. Only setup codes are copied, with no personal data.'; }
                field(VendorTemplate; VendorNo) { ApplicationArea = All; Caption = 'Vendor configuration source'; TableRelation = Vendor; ToolTip = 'Select a configured QA vendor. Only setup codes are copied.'; }
                field(ItemTemplate; ItemNo) { ApplicationArea = All; Caption = 'Item configuration source'; TableRelation = Item; ToolTip = 'Select an item with posting groups, category and base unit of measure.'; }
            }
        }
    }

    trigger OnOpenPage()
    begin
        Policy.RequireSandbox();
        Policy.InitializeTemporaryRequest(Rec);
        CustomTargetsEditable := Rec.Profile = Rec.Profile::Custom;
    end;

    procedure Create(): Integer
    var
        GenerationRun: Record "BCP Run";
        Management: Codeunit "BCP Management";
    begin
        GenerationRun := Rec;
        // The dialog row is configuration only; persistent run identity is allocated later.
        GenerationRun."Run ID" := 0;
        Management.CreateRun(GenerationRun, CustomerNo, VendorNo, ItemNo);
        exit(GenerationRun."Run ID");
    end;

    var
        Policy: Codeunit "BCP Policy";
        CustomTargetsEditable: Boolean;
        CustomerNo: Code[20];
        VendorNo: Code[20];
        ItemNo: Code[20];
}
