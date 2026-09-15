enum 53401 "BCP Status"
{
    Extensible = false;
    value(0; Pending) { Caption = 'Pending'; }
    value(1; Running) { Caption = 'Running'; }
    value(2; Completed) { Caption = 'Completed'; }
    value(3; Failed) { Caption = 'Failed'; }
    value(4; Cancelled) { Caption = 'Cancelled'; }
    value(5; Cleaning) { Caption = 'Cleaning'; }
    value(6; Cleaned) { Caption = 'Cleaned'; }
}
