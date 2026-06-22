table 53194 "DH Scan Check Selection"
{
    Caption = 'Scan Check Selection';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Check Code"; Code[50])
        {
            Caption = 'Check Code';
            DataClassification = CustomerContent;
        }
        field(2; "Module"; Text[100])
        {
            Caption = 'Module';
            DataClassification = CustomerContent;
        }
        field(3; Name; Text[150])
        {
            Caption = 'Name';
            DataClassification = CustomerContent;
        }
        field(4; Description; Text[250])
        {
            Caption = 'Description';
            DataClassification = CustomerContent;
        }
        field(5; Enabled; Boolean)
        {
            Caption = 'Enabled';
            DataClassification = CustomerContent;
        }
        field(6; "Default Enabled"; Boolean)
        {
            Caption = 'Default Enabled';
            DataClassification = CustomerContent;
        }
        field(7; "Risk Level"; Code[20])
        {
            Caption = 'Risk Level';
            DataClassification = CustomerContent;
        }
        field(8; "Sort Order"; Integer)
        {
            Caption = 'Sort Order';
            DataClassification = CustomerContent;
        }
        field(9; "Last Modified At"; DateTime)
        {
            Caption = 'Last Modified At';
            DataClassification = CustomerContent;
            Editable = false;
        }
        field(10; "Last Run At"; DateTime)
        {
            Caption = 'Last Run At';
            DataClassification = CustomerContent;
            Editable = false;
        }
        field(11; "Last Finding Count"; Integer)
        {
            Caption = 'Last Finding Count';
            DataClassification = CustomerContent;
            Editable = false;
        }
    }

    keys
    {
        key(PK; "Check Code")
        {
            Clustered = true;
        }
        key(Sort; "Sort Order", "Module", "Check Code")
        {
        }
    }

    trigger OnInsert()
    begin
        if "Last Modified At" = 0DT then
            "Last Modified At" := CurrentDateTime();
    end;

    trigger OnModify()
    begin
        "Last Modified At" := CurrentDateTime();
    end;
}
