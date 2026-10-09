enum 53194 "DH Remediation Status"
{
    Extensible = false;
    value(0; Open) { Caption = 'Open'; }
    value(1; InProgress) { Caption = 'In Progress'; }
    value(2; Blocked) { Caption = 'Blocked'; }
    value(3; Completed) { Caption = 'Completed'; }
    value(4; Cancelled) { Caption = 'Cancelled'; }
}

enum 53195 "DH Remediation Priority"
{
    Extensible = false;
    value(0; Medium) { Caption = 'Medium'; }
    value(1; Critical) { Caption = 'Critical'; }
    value(2; High) { Caption = 'High'; }
    value(3; Low) { Caption = 'Low'; }
}

enum 53196 "DH Remediation Source"
{
    Extensible = false;
    value(0; Manual) { Caption = 'Manual'; }
    value(1; Recommendation) { Caption = 'Recommendation'; }
    value(2; Imported) { Caption = 'Imported'; }
}
