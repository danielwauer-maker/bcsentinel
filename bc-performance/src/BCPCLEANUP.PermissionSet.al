permissionset 53401 "BCP CLEANUP"
{
    Assignable = true;
    Caption = 'BCSentinel QA cleanup';
    Permissions = table "BCP Run" = X,
                  table "BCP Owned Record" = X,
                  tabledata "BCP Run" = Rm,
                  tabledata "BCP Owned Record" = Rd,
                  tabledata Customer = Rd,
                  tabledata Vendor = Rd,
                  tabledata Item = Rd,
                  tabledata "Item Unit of Measure" = Rd,
                  page "BCP Runs" = X,
                  codeunit "BCP Policy" = X,
                  codeunit "BCP Cleanup" = X,
                  codeunit "BCP Cleanup Batch" = X,
                  codeunit "BCP References" = X;
}
