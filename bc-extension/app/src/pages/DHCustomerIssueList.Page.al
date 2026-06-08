page 53156 "DH Customer Issue List"
{
    PageType = List;
    SourceTable = Customer;
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Customer Issue List';
    Editable = false;

    layout
    {
        area(Content)
        {
            repeater(General)
            {
                field("No."; Rec."No.") { ApplicationArea = All; ToolTip = 'Specifies No.'; }
                field(Name; Rec.Name) { ApplicationArea = All; ToolTip = 'Specifies Name.'; }
                field(Address; Rec.Address) { ApplicationArea = All; ToolTip = 'Specifies Address.'; }
                field(City; Rec.City) { ApplicationArea = All; ToolTip = 'Specifies City.'; }
                field("Post Code"; Rec."Post Code") { ApplicationArea = All; ToolTip = 'Specifies Post Code.'; }
                field("Country/Region Code"; Rec."Country/Region Code") { ApplicationArea = All; ToolTip = 'Specifies Country/Region Code.'; }
                field("E-Mail"; Rec."E-Mail") { ApplicationArea = All; ToolTip = 'Specifies E-Mail.'; }
                field("Phone No."; Rec."Phone No.") { ApplicationArea = All; ToolTip = 'Specifies Phone No.'; }
                field("Payment Terms Code"; Rec."Payment Terms Code") { ApplicationArea = All; ToolTip = 'Specifies Payment Terms Code.'; }
                field("Payment Method Code"; Rec."Payment Method Code") { ApplicationArea = All; ToolTip = 'Specifies Payment Method Code.'; }
                field("Salesperson Code"; Rec."Salesperson Code") { ApplicationArea = All; ToolTip = 'Specifies Salesperson Code.'; }
                field("Customer Price Group"; Rec."Customer Price Group") { ApplicationArea = All; ToolTip = 'Specifies Customer Price Group.'; }
                field("Customer Disc. Group"; Rec."Customer Disc. Group") { ApplicationArea = All; ToolTip = 'Specifies Customer Disc. Group.'; }
                field("Reminder Terms Code"; Rec."Reminder Terms Code") { ApplicationArea = All; ToolTip = 'Specifies Reminder Terms Code.'; }
                field("Fin. Charge Terms Code"; Rec."Fin. Charge Terms Code") { ApplicationArea = All; ToolTip = 'Specifies Fin. Charge Terms Code.'; }
                field(Contact; Rec.Contact) { ApplicationArea = All; ToolTip = 'Specifies Contact.'; }
                field("Home Page"; Rec."Home Page") { ApplicationArea = All; ToolTip = 'Specifies Home Page.'; }
                field("VAT Registration No."; Rec."VAT Registration No.") { ApplicationArea = All; ToolTip = 'Specifies VAT Registration No.'; }
                field("Credit Limit (LCY)"; Rec."Credit Limit (LCY)") { ApplicationArea = All; ToolTip = 'Specifies Credit Limit (LCY).'; }
                field(Blocked; Rec.Blocked) { ApplicationArea = All; ToolTip = 'Specifies Blocked.'; }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(OpenCustomerCard)
            {
                Caption = 'Correct Data';
                ToolTip = 'Runs Correct Data.';
                ApplicationArea = All;
                Image = EditLines;
                trigger OnAction()
                begin
                    Page.Run(Page::"Customer Card", Rec);
                end;
            }
            action(ExcludeFromIssue)
            {
                Caption = 'Exclude from Analysis';
                ToolTip = 'Runs Exclude from Analysis.';
                ApplicationArea = All;
                Image = Cancel;
                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    if CurrentIssueCode = '' then
                        exit;
                    ExceptionMgt.AddCustomerException(Rec, CurrentIssueCode, StrSubstNo('Manually excluded from %1.', CurrentIssueCode));
                    CurrPage.Update(false);
                end;
            }
            action(MarkCorrected)
            {
                Caption = 'Mark as Corrected';
                ToolTip = 'Runs Mark as Corrected.';
                ApplicationArea = All;
                Image = EditLines;
                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    if CurrentIssueCode = '' then
                        exit;
                    ExceptionMgt.MarkCustomerCorrected(Rec, CurrentIssueCode, 'Datensatz manuell als korrigiert markiert.');
                    CurrPage.Update(false);
                end;
            }
        }
    }

    var
        CurrentIssueCode: Code[50];

    trigger OnOpenPage()
    begin
        if CurrentIssueCode = '' then
            CurrentIssueCode := InferIssueCodeFromFilters();
        ApplyIssueFilter();
    end;

    procedure SetIssueCode(IssueCode: Code[50])
    begin
        CurrentIssueCode := IssueCode;
    end;

    local procedure ApplyIssueFilter()
    begin
        case CurrentIssueCode of
            'CUSTOMERS_MISSING_NAME':
                Rec.SetRange(Name, '');
            'CUSTOMERS_MISSING_SEARCH_NAME':
                Rec.SetRange("Search Name", '');
            'CUSTOMERS_MISSING_ADDRESS':
                Rec.SetRange(Address, '');
            'CUSTOMERS_MISSING_CITY':
                Rec.SetRange(City, '');
            'CUSTOMERS_MISSING_POST_CODE':
                Rec.SetRange("Post Code", '');
            'CUSTOMERS_MISSING_COUNTRY':
                Rec.SetRange("Country/Region Code", '');
            'CUSTOMERS_MISSING_EMAIL':
                Rec.SetRange("E-Mail", '');
            'CUSTOMERS_MISSING_PHONE':
                Rec.SetRange("Phone No.", '');
            'CUSTOMERS_MISSING_PAYMENT_TERMS':
                Rec.SetRange("Payment Terms Code", '');
            'CUSTOMERS_MISSING_PAYMENT_METHOD':
                Rec.SetRange("Payment Method Code", '');
            'CUSTOMERS_MISSING_POSTING_GROUP':
                Rec.SetRange("Customer Posting Group", '');
            'CUSTOMERS_MISSING_GEN_BUS_POSTING',
            'SYSTEM_CUSTOMERS_MISSING_GEN_BUS_POSTING':
                Rec.SetRange("Gen. Bus. Posting Group", '');
            'CUSTOMERS_MISSING_VAT_BUS_POSTING',
            'SYSTEM_CUSTOMERS_MISSING_VAT_BUS_POSTING':
                Rec.SetRange("VAT Bus. Posting Group", '');
            'CUSTOMERS_MISSING_CREDIT_LIMIT':
                Rec.SetRange("Credit Limit (LCY)", 0);
            'CUSTOMERS_MISSING_VAT_REG_NO':
                Rec.SetRange("VAT Registration No.", '');
            'CUSTOMERS_MISSING_SALESPERSON':
                Rec.SetRange("Salesperson Code", '');
            'CUSTOMERS_MISSING_PRICE_GROUP':
                Rec.SetRange("Customer Price Group", '');
            'CUSTOMERS_MISSING_DISC_GROUP':
                Rec.SetRange("Customer Disc. Group", '');
            'CUSTOMERS_MISSING_REMINDER_TERMS':
                Rec.SetRange("Reminder Terms Code", '');
            'CUSTOMERS_MISSING_FIN_CHARGE_TERMS':
                Rec.SetRange("Fin. Charge Terms Code", '');
            'CUSTOMERS_MISSING_CONTACT':
                Rec.SetRange(Contact, '');
            'CUSTOMERS_MISSING_HOME_PAGE':
                Rec.SetRange("Home Page", '');
        end;
    end;

    local procedure InferIssueCodeFromFilters(): Code[50]
    begin
        if Rec.GetFilter(Name) <> '' then
            exit('CUSTOMERS_MISSING_NAME');
        if Rec.GetFilter("Search Name") <> '' then
            exit('CUSTOMERS_MISSING_SEARCH_NAME');
        if Rec.GetFilter(Address) <> '' then
            exit('CUSTOMERS_MISSING_ADDRESS');
        if Rec.GetFilter(City) <> '' then
            exit('CUSTOMERS_MISSING_CITY');
        if Rec.GetFilter("Post Code") <> '' then
            exit('CUSTOMERS_MISSING_POST_CODE');
        if Rec.GetFilter("Country/Region Code") <> '' then
            exit('CUSTOMERS_MISSING_COUNTRY');
        if Rec.GetFilter("E-Mail") <> '' then
            exit('CUSTOMERS_MISSING_EMAIL');
        if Rec.GetFilter("Phone No.") <> '' then
            exit('CUSTOMERS_MISSING_PHONE');
        if Rec.GetFilter("Payment Terms Code") <> '' then
            exit('CUSTOMERS_MISSING_PAYMENT_TERMS');
        if Rec.GetFilter("Payment Method Code") <> '' then
            exit('CUSTOMERS_MISSING_PAYMENT_METHOD');
        if Rec.GetFilter("Customer Posting Group") <> '' then
            exit('CUSTOMERS_MISSING_POSTING_GROUP');
        if Rec.GetFilter("Gen. Bus. Posting Group") <> '' then
            exit('CUSTOMERS_MISSING_GEN_BUS_POSTING');
        if Rec.GetFilter("VAT Bus. Posting Group") <> '' then
            exit('CUSTOMERS_MISSING_VAT_BUS_POSTING');
        if Rec.GetFilter("VAT Registration No.") <> '' then
            exit('CUSTOMERS_MISSING_VAT_REG_NO');
        if Rec.GetFilter("Salesperson Code") <> '' then
            exit('CUSTOMERS_MISSING_SALESPERSON');
        if Rec.GetFilter("Customer Price Group") <> '' then
            exit('CUSTOMERS_MISSING_PRICE_GROUP');
        if Rec.GetFilter("Customer Disc. Group") <> '' then
            exit('CUSTOMERS_MISSING_DISC_GROUP');
        if Rec.GetFilter("Reminder Terms Code") <> '' then
            exit('CUSTOMERS_MISSING_REMINDER_TERMS');
        if Rec.GetFilter("Fin. Charge Terms Code") <> '' then
            exit('CUSTOMERS_MISSING_FIN_CHARGE_TERMS');
        if Rec.GetFilter(Contact) <> '' then
            exit('CUSTOMERS_MISSING_CONTACT');
        if Rec.GetFilter("Home Page") <> '' then
            exit('CUSTOMERS_MISSING_HOME_PAGE');
        if Rec.GetFilter("Credit Limit (LCY)") <> '' then
            exit('CUSTOMERS_MISSING_CREDIT_LIMIT');

        exit('');
    end;
}

