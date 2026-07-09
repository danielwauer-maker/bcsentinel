codeunit 53197 "DH Currency Mgt."
{
    procedure GetLocalCurrencyCode(): Code[10]
    var
        GeneralLedgerSetup: Record "General Ledger Setup";
    begin
        if GeneralLedgerSetup.Get() then
            exit(GeneralLedgerSetup."LCY Code");

        exit('');
    end;

    procedure FormatLocalAmount(Amount: Decimal): Text[50]
    var
        CurrencyCode: Code[10];
        AmountTxt: Text[30];
    begin
        AmountTxt := CopyStr(Format(Round(Amount, 0.01), 0, '<Precision,2:2><Standard Format,0>'), 1, 30);
        CurrencyCode := GetLocalCurrencyCode();

        if CurrencyCode = '' then
            exit(CopyStr(AmountTxt, 1, 50));

        exit(CopyStr(AmountTxt + ' ' + CurrencyCode, 1, 50));
    end;
}
