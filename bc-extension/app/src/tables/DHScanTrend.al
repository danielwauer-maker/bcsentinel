table 53104 "DH Scan Trend"
{
    Caption = 'DH Scan Trend';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Tenant ID"; Code[50])
        {
            Caption = 'Tenant ID';
            DataClassification = CustomerContent;
        }
        field(2; "Latest Scan ID"; Code[50])
        {
            Caption = 'Latest Scan ID';
            DataClassification = CustomerContent;
        }
        field(3; "Previous Scan ID"; Code[50])
        {
            Caption = 'Previous Scan ID';
            DataClassification = CustomerContent;
        }
        field(4; "Latest Score"; Integer)
        {
            Caption = 'Latest Score';
            DataClassification = CustomerContent;
        }
        field(5; "Previous Score"; Integer)
        {
            Caption = 'Previous Score';
            DataClassification = CustomerContent;
        }
        field(6; "Delta"; Integer)
        {
            Caption = 'Delta';
            DataClassification = CustomerContent;
        }
        field(7; "Trend"; Text[10])
        {
            Caption = 'Trend';
            DataClassification = CustomerContent;
        }
        field(8; "Last Updated At"; DateTime)
        {
            Caption = 'Last Updated At';
            DataClassification = CustomerContent;
        }
    }

    keys
    {
        key(PK; "Tenant ID")
        {
            Clustered = true;
        }
    }
}
