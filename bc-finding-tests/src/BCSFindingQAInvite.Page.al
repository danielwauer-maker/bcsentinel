page 53463 "BCS Finding QA Invite"
{
    // QA-only dialog; write operations are guarded by the calling evidence page.
    PageType = StandardDialog;
    ApplicationArea = All;
    Caption = 'BCSentinel Finding QA Invite';

    layout
    {
        area(Content)
        {
            field(InviteCode; InviteCode)
            {
                ApplicationArea = All;
                Caption = 'Registration Invite Code';
                ExtendedDatatype = Masked;
                ToolTip = 'Specifies the temporary registration invite code for the isolated Finding QA runtime test.';
            }
        }
    }

    procedure GetInviteCode(): Text[100]
    begin
        exit(InviteCode);
    end;

    var
        InviteCode: Text[100];
}
