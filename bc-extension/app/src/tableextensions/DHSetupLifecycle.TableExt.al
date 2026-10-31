tableextension 53201 "DH Setup Lifecycle Ext" extends "DH Setup"
{
    fields
    {
        field(53136; "Report Notification Email"; Text[250])
        {
            Caption = 'Report & Notification Email';
            DataClassification = CustomerContent;
            ExtendedDatatype = EMail;

            trigger OnValidate()
            begin
                if ("Report Notification Email" <> '') and (StrPos("Report Notification Email", '@') <= 1) then
                    Error('Please enter a valid report and notification email address.');
            end;
        }
        field(53137; "Preferred Report Language"; Code[2])
        {
            Caption = 'Preferred Report Language';
            DataClassification = CustomerContent;
            InitValue = 'EN';

            trigger OnValidate()
            begin
                "Preferred Report Language" := UpperCase("Preferred Report Language");
                if not ("Preferred Report Language" in ['DE', 'EN']) then
                    Error('Preferred Report Language must be DE or EN.');
            end;
        }
    }
}
