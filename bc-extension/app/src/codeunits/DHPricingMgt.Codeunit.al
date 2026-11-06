codeunit 53190 "DH Pricing Mgt."
{
    procedure GetPriceQuote(ProductCode: Text; AnalyzedRecordCount: Integer; var TierCode: Text; var PriceEUR: Decimal; var CustomQuote: Boolean)
    var
        Setup: Record "DH Setup";
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        JsonResponse: JsonObject;
        Token: JsonToken;
        Url: Text;
    begin
        if not Setup.Get() then
            Error('BCSentinel Setup is not configured.');
        if Setup."API Base URL" = '' then
            Error('BCSentinel API Base URL is not configured.');
        if AnalyzedRecordCount < 0 then
            AnalyzedRecordCount := 0;

        Url := BuildQuoteUrl(Setup."API Base URL", ProductCode, AnalyzedRecordCount);
        if not Client.Get(Url, Response) then
            Error('BCSentinel pricing request could not be sent.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('BCSentinel pricing request failed with status %1.', Response.HttpStatusCode());
        if not JsonResponse.ReadFrom(ResponseText) then
            Error('BCSentinel pricing response is invalid.');

        TierCode := '';
        PriceEUR := 0;
        CustomQuote := false;

        if JsonResponse.Get('tier_code', Token) then
            if not IsJsonNull(Token) then
                TierCode := Token.AsValue().AsText();
        if JsonResponse.Get('custom_quote', Token) then
            if not IsJsonNull(Token) then
                CustomQuote := Token.AsValue().AsBoolean();
        if not CustomQuote then
            if JsonResponse.Get('price_eur', Token) then
                if not IsJsonNull(Token) then
                    PriceEUR := Token.AsValue().AsDecimal();
    end;

    procedure GetAssessmentQuote(AnalyzedRecordCount: Integer; var TierCode: Text; var PriceEUR: Decimal; var CustomQuote: Boolean)
    begin
        GetPriceQuote('assessment', AnalyzedRecordCount, TierCode, PriceEUR, CustomQuote);
    end;

    procedure GetValidationQuote(AnalyzedRecordCount: Integer; var TierCode: Text; var PriceEUR: Decimal; var CustomQuote: Boolean)
    begin
        GetPriceQuote('validation_check', AnalyzedRecordCount, TierCode, PriceEUR, CustomQuote);
    end;

    procedure GetMonitoringMonthlyQuote(AnalyzedRecordCount: Integer; var TierCode: Text; var PriceEUR: Decimal; var CustomQuote: Boolean)
    begin
        GetPriceQuote('monitoring_monthly', AnalyzedRecordCount, TierCode, PriceEUR, CustomQuote);
    end;

    procedure GetMonitoringAnnualQuote(AnalyzedRecordCount: Integer; var TierCode: Text; var PriceEUR: Decimal; var CustomQuote: Boolean)
    begin
        GetPriceQuote('monitoring_annual', AnalyzedRecordCount, TierCode, PriceEUR, CustomQuote);
    end;

    local procedure BuildQuoteUrl(BaseUrl: Text; ProductCode: Text; AnalyzedRecordCount: Integer): Text
    var
        NormalizedBaseUrl: Text;
    begin
        NormalizedBaseUrl := BaseUrl;
        while (StrLen(NormalizedBaseUrl) > 0) and (CopyStr(NormalizedBaseUrl, StrLen(NormalizedBaseUrl), 1) = '/') do
            NormalizedBaseUrl := CopyStr(NormalizedBaseUrl, 1, StrLen(NormalizedBaseUrl) - 1);

        exit(StrSubstNo('%1/pricing/quote?product_key=%2&record_count=%3', NormalizedBaseUrl, ProductCode, AnalyzedRecordCount));
    end;

    local procedure IsJsonNull(Token: JsonToken): Boolean
    begin
        if not Token.IsValue() then
            exit(false);
        exit(Token.AsValue().IsNull());
    end;
}
