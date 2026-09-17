permissionset 53452 "BCR EVIDENCE"
{
    Assignable = true;
    Caption = 'BC runtime evidence export';
    Permissions = codeunit "BCR Evidence Export" = X,
                  page "BCR Runtime Evidence" = X,
                  tabledata "DH Deep Scan Run" = R,
                  tabledata "DH Deep Scan Finding" = R,
                  tabledata "DH Setup" = R,
                  tabledata "DH Issue Exception" = R,
                  tabledata "BCP Run" = R,
                  tabledata "BCP Owned Record" = R,
                  tabledata Customer = R,
                  tabledata Vendor = R,
                  tabledata Item = R;
}
