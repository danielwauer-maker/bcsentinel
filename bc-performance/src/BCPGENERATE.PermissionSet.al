permissionset 53400 "BCP GENERATE"
{
    Assignable = true;
    Caption = 'BCSentinel QA generation';
    Permissions = table "BCP Run" = X,
                  table "BCP Owned Record" = X,
                  tabledata "BCP Run" = Rim,
                  tabledata "BCP Owned Record" = Ri,
                  tabledata Customer = Ri,
                  tabledata Vendor = Ri,
                  tabledata Item = Rim,
                  tabledata "Item Unit of Measure" = Ri,
                  tabledata "Customer Posting Group" = R,
                  tabledata "Vendor Posting Group" = R,
                  tabledata "Gen. Business Posting Group" = R,
                  tabledata "VAT Business Posting Group" = R,
                  tabledata "Gen. Product Posting Group" = R,
                  tabledata "VAT Product Posting Group" = R,
                  tabledata "Inventory Posting Group" = R,
                  tabledata "Item Category" = R,
                  tabledata "Item Attribute Value Mapping" = R,
                  tabledata "Unit of Measure" = R,
                  tabledata "Payment Terms" = R,
                  tabledata "Payment Method" = R,
                  tabledata "Country/Region" = R,
                  page "BCP Runs" = X,
                  page "BCP New Run" = X,
                  codeunit "BCP Policy" = X,
                  codeunit "BCP Config" = X,
                  codeunit "BCP Management" = X,
                  codeunit "BCP Batch" = X;
}
