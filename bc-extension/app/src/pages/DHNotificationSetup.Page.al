page 53170 "DH Notification Setup"
{
    PageType = Card;
    SourceTable = "DH Notification Setup";
    ApplicationArea = All;
    UsageCategory = Administration;
    Caption = 'BCSentinel Notification Setup';
    InsertAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            group(General)
            {
                field(Enabled; Rec.Enabled) { ApplicationArea = All; ToolTip = 'Specifies whether tenant-wide BCSentinel product notifications are enabled.'; }
                field("Preferred Language"; Rec."Preferred Language") { ApplicationArea = All; ToolTip = 'Specifies the tenant fallback language for notification templates.'; }
                field("Delivery Evidence Retention Days"; Rec."Delivery Evidence Retention Days") { ApplicationArea = All; ToolTip = 'Specifies the minimum retention horizon for delivery evidence.'; }
                field("Last Processing At UTC"; Rec."Last Processing At UTC") { ApplicationArea = All; Editable = false; }
                field("Tenant ID"; Rec."Tenant ID") { ApplicationArea = All; Editable = false; }
                field("Company ID"; Rec."Company ID") { ApplicationArea = All; Editable = false; }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(Recipients)
            {
                ApplicationArea = All; Caption = 'Recipients'; Image = Users;
                RunObject = page "DH Notification Recipients";
            }
            action(Rules)
            {
                ApplicationArea = All; Caption = 'Event Rules'; Image = Setup;
                RunObject = page "DH Notification Rules";
            }
            action(Templates)
            {
                ApplicationArea = All; Caption = 'Templates'; Image = Email;
                RunObject = page "DH Notification Templates";
            }
            action(Events)
            {
                ApplicationArea = All; Caption = 'Event Log'; Image = Log;
                RunObject = page "DH Notification Events";
            }
            action(Deliveries)
            {
                ApplicationArea = All; Caption = 'Delivery Log'; Image = SendTo;
                RunObject = page "DH Notification Deliveries";
            }
            action(Audit)
            {
                ApplicationArea = All; Caption = 'Configuration Audit'; Image = History;
                RunObject = page "DH Notification Audit";
            }
            action(EnsureDefaults)
            {
                ApplicationArea = All; Caption = 'Ensure Default Rules'; Image = Refresh;
                trigger OnAction()
                var NotificationMgt: Codeunit "DH Notification Mgt.";
                begin
                    NotificationMgt.EnsureSetupAndDefaults();
                    CurrPage.Update(false);
                end;
            }
            action(ProcessQueue)
            {
                ApplicationArea = All; Caption = 'Process Delivery Queue'; Image = SendMail;
                trigger OnAction()
                var NotificationMgt: Codeunit "DH Notification Mgt.";
                begin
                    NotificationMgt.ProcessQueuedDeliveries(50);
                end;
            }
        }
    }

    trigger OnOpenPage()
    var NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        NotificationMgt.EnsureSetupAndDefaults();
        if not Rec.Get() then begin
            Rec.Init();
            Rec.Insert(true);
        end;
    end;
}
