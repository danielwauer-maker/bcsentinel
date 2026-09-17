permissionset 53462 "BCS FINDING QA"
{
    Assignable = true;
    Caption = 'Finding QA evidence';
    Permissions = page "BCS Finding QA Export" = X,
                  codeunit "BCS Finding Identity Tests" = X,
                  tabledata "DH Deep Scan Run" = R,
                  tabledata "DH Deep Scan Finding" = R;
}
