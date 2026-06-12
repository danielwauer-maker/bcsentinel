page 53145 "DH Duplicate Worklist"
{
    PageType = List;
    SourceTable = "DH Duplicate Buffer";
    SourceTableTemporary = true;
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Duplicate Worklist';
    Editable = false;

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
                field(Reason; Rec.Reason)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Reason.';
                }
                field("Duplicate Count"; Rec."Duplicate Count")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Duplicate Count.';
                }
                field("Source No."; Rec."Source No.")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Source No..';
                }
                field(Name; Rec.Name)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Name.';
                }
                field("Post Code"; Rec."Post Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Post Code.';
                }
                field(City; Rec.City)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies City.';
                }
                field("E-Mail"; Rec."E-Mail")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies E-Mail.';
                }
                field("VAT Registration No."; Rec."VAT Registration No.")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies VAT Registration No.';
                }
                field("Group Key"; Rec."Group Key")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Group Key.';
                    Visible = false;
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(OpenMasterData)
            {
                Caption = 'Correct Data';
                ToolTip = 'Runs Correct Data.';
                ApplicationArea = All;
                Image = EditLines;

                trigger OnAction()
                var
                    Customer: Record Customer;
                    Vendor: Record Vendor;
                begin
                    case Rec."Source Type" of
                        Rec."Source Type"::Customer:
                            if Customer.Get(Rec."Source No.") then
                                Page.Run(Page::"Customer Card", Customer);
                        Rec."Source Type"::Vendor:
                            if Vendor.Get(Rec."Source No.") then
                                Page.Run(Page::"Vendor Card", Vendor);
                    end;
                end;
            }
        }
    }

    trigger OnOpenPage()
    var
        DuplicateWorklistMgt: Codeunit "DH Duplicate Worklist Mgt.";
    begin
        DuplicateWorklistMgt.BuildWorklist(Rec);
    end;
}

