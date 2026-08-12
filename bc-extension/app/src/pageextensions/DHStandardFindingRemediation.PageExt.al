pageextension 53180 "DH Sales Order Remediation" extends "Sales Order List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::"Sales Header", Rec.SystemId, Rec."No.", Rec."Sell-to Customer Name"); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::"Sales Header", Rec.SystemId, Rec."No.", Rec."Sell-to Customer Name"); end;
            }
        }
    }
}

pageextension 53181 "DH Purchase Order Remediation" extends "Purchase Order List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::"Purchase Header", Rec.SystemId, Rec."No.", Rec."Buy-from Vendor Name"); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::"Purchase Header", Rec.SystemId, Rec."No.", Rec."Buy-from Vendor Name"); end;
            }
        }
    }
}

pageextension 53182 "DH Cust Ledger Remediation" extends "Customer Ledger Entries"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::"Cust. Ledger Entry", Rec.SystemId, Format(Rec."Entry No."), Rec.Description); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::"Cust. Ledger Entry", Rec.SystemId, Format(Rec."Entry No."), Rec.Description); end;
            }
        }
    }
}

pageextension 53183 "DH Vendor Ledger Remediation" extends "Vendor Ledger Entries"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::"Vendor Ledger Entry", Rec.SystemId, Format(Rec."Entry No."), Rec.Description); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::"Vendor Ledger Entry", Rec.SystemId, Format(Rec."Entry No."), Rec.Description); end;
            }
        }
    }
}

pageextension 53184 "DH GL Entry Remediation" extends "General Ledger Entries"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::"G/L Entry", Rec.SystemId, Format(Rec."Entry No."), Rec.Description); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::"G/L Entry", Rec.SystemId, Format(Rec."Entry No."), Rec.Description); end;
            }
        }
    }
}

pageextension 53185 "DH GL Account Remediation" extends "G/L Account List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::"G/L Account", Rec.SystemId, Rec."No.", Rec.Name); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::"G/L Account", Rec.SystemId, Rec."No.", Rec.Name); end;
            }
        }
    }
}

pageextension 53186 "DH Contact Remediation" extends "Contact List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::Contact, Rec.SystemId, Rec."No.", Rec.Name); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::Contact, Rec.SystemId, Rec."No.", Rec.Name); end;
            }
        }
    }
}

pageextension 53187 "DH Employee Remediation" extends "Employee List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::Employee, Rec.SystemId, Rec."No.", Rec.FullName()); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::Employee, Rec.SystemId, Rec."No.", Rec.FullName()); end;
            }
        }
    }
}

pageextension 53188 "DH Resource Remediation" extends "Resource List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::Resource, Rec.SystemId, Rec."No.", Rec.Name); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::Resource, Rec.SystemId, Rec."No.", Rec.Name); end;
            }
        }
    }
}

pageextension 53189 "DH Service Item Remediation" extends "Service Item List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::"Service Item", Rec.SystemId, Rec."No.", Rec.Description); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::"Service Item", Rec.SystemId, Rec."No.", Rec.Description); end;
            }
        }
    }
}

pageextension 53190 "DH Job Remediation" extends "Job List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHExcludeFinding)
            {
                Caption = 'Exclude from Analysis'; ApplicationArea = All; Image = Cancel; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Excludes the selected record from the current BCSentinel finding without requiring a manual finding code.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.PromptExclude(Database::Job, Rec.SystemId, Rec."No.", Rec.Description); end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected'; ApplicationArea = All; Image = Approve; Promoted = true; PromotedCategory = Process;
                ToolTip = 'Documents the selected record as corrected. Future scans still re-evaluate the actual data.';
                trigger OnAction()
                var Mgt: Codeunit "DH Generic Remediation";
                begin Mgt.MarkCorrected(Database::Job, Rec.SystemId, Rec."No.", Rec.Description); end;
            }
        }
    }
}
