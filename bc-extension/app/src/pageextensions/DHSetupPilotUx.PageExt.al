pageextension 53198 "DH Setup Pilot UX" extends "DH Setup"
{
    actions
    {
        modify(OpenDashboard)
        {
            Visible = DashboardResultAvailable;
        }
    }

    trigger OnOpenPage()
    begin
        UpdateDashboardVisibility();
    end;

    trigger OnAfterGetRecord()
    begin
        UpdateDashboardVisibility();
    end;

    var
        DashboardResultAvailable: Boolean;

    local procedure UpdateDashboardVisibility()
    begin
        DashboardResultAvailable := Rec."Last Scan Date" <> 0DT;
    end;
}
