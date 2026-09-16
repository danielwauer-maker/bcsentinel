pageextension 53198 "DH Setup Copy Recovery" extends "DH Setup"
{
    layout
    {
        addlast(AdvancedInformation)
        {
            field(CopiedCompanyIdentityState; RecoveryMgt.GetIdentityStateDisplay(Rec))
            {
                ApplicationArea = All;
                Caption = 'Registration Identity';
                Editable = false;
                ToolTip = 'Shows whether the stored BCSentinel identity snapshot matches the current Business Central company. A mismatch can occur after a company is copied.';
            }
        }
    }

    actions
    {
        addlast(Processing)
        {
            action(ResetCopiedCompanyRegistration)
            {
                ApplicationArea = All;
                Caption = 'Reset Copied Company Registration';
                ToolTip = 'Removes only the copied local BCSentinel binding and BCSentinel history from this company so it can be registered separately. Business Central business data and the source company are not changed.';
                Image = ResetStatus;
                Visible = RecoveryVisible;
                AccessByPermission = codeunit "DH Copied Company Recovery" = X;

                trigger OnAction()
                begin
                    if not RecoveryMgt.RecoverCopiedCompany(Rec) then
                        exit;

                    RecoveryVisible := RecoveryMgt.CanOfferRecovery(Rec);
                    CurrPage.Update(false);
                    Message(RecoveryCompletedMsg);
                end;
            }
        }
    }

    trigger OnOpenPage()
    begin
        RecoveryVisible := RecoveryMgt.CanOfferRecovery(Rec);
    end;

    trigger OnAfterGetCurrRecord()
    begin
        RecoveryVisible := RecoveryMgt.CanOfferRecovery(Rec);
    end;

    var
        RecoveryMgt: Codeunit "DH Copied Company Recovery";
        RecoveryVisible: Boolean;
        RecoveryCompletedMsg: Label 'The copied local BCSentinel registration was reset. Business Central business data and the source company were not changed. You can now register this company separately with BCSentinel.';
}
