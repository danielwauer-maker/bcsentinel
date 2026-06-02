enum 53102 "DH License Status"
{
    Extensible = false;
    Caption = 'DH License Status';

    value(0; Trial)
    {
        Caption = 'Compatibility Pending';
    }

    value(1; Active)
    {
        Caption = 'Active';
    }

    value(2; Expired)
    {
        Caption = 'Expired';
    }

    value(3; Blocked)
    {
        Caption = 'Blocked';
    }
}
