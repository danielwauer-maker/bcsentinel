from __future__ import annotations

from dataclasses import dataclass

from app.services.localization_service import normalize_language


@dataclass(frozen=True)
class IssueText:
    title: str
    recommendation: str


ISSUE_TEXTS: dict[str, dict[str, IssueText]] = {
    "CUSTOMERS_MISSING_POSTCODE": {
        "en": IssueText("Customers without a post code", "Complete the address data for the affected customers."),
        "de": IssueText("Debitoren ohne Postleitzahl", "Adressdaten der betroffenen Debitoren vervollständigen."),
    },
    "CUSTOMERS_MISSING_PAYMENT_TERMS": {
        "en": IssueText("Customers without payment terms", "Maintain payment terms for the affected customers."),
        "de": IssueText("Debitoren ohne Zahlungsbedingungen", "Zahlungsbedingungen bei den betroffenen Debitoren pflegen."),
    },
    "CUSTOMERS_MISSING_COUNTRY_CODE": {
        "en": IssueText("Customers without a country/region code", "Maintain the country/region code for the affected customers."),
        "de": IssueText("Debitoren ohne Länder-/Regionscode", "Länder-/Regionscode für die betroffenen Debitoren pflegen."),
    },
    "CUSTOMERS_MISSING_VAT_REG_NO": {
        "en": IssueText("Customers without a VAT registration number", "Review and complete the VAT registration number for the affected customers."),
        "de": IssueText("Debitoren ohne USt-IdNr.", "USt-IdNr. der betroffenen Debitoren prüfen und ergänzen."),
    },
    "CUSTOMERS_MISSING_EMAIL": {
        "en": IssueText("Customers without an email address", "Add email addresses for the affected customers."),
        "de": IssueText("Debitoren ohne E-Mail-Adresse", "E-Mail-Adressen der betroffenen Debitoren ergänzen."),
    },
    "CUSTOMERS_MISSING_PHONE_NO": {
        "en": IssueText("Customers without a phone number", "Maintain phone numbers for the affected customers."),
        "de": IssueText("Debitoren ohne Telefonnummer", "Telefonnummern der betroffenen Debitoren pflegen."),
    },
    "CUSTOMERS_MISSING_CUSTOMER_POSTING_GROUP": {
        "en": IssueText("Customers without a customer posting group", "Maintain customer posting groups for the affected customers."),
        "de": IssueText("Debitoren ohne Debitorenbuchungsgruppe", "Debitorenbuchungsgruppen der betroffenen Debitoren pflegen."),
    },
    "CUSTOMERS_MISSING_GEN_BUS_POSTING_GROUP": {
        "en": IssueText("Customers without a general business posting group", "Maintain general business posting groups for the affected customers."),
        "de": IssueText("Debitoren ohne Geschäftsbuchungsgruppe", "Geschäftsbuchungsgruppen der betroffenen Debitoren pflegen."),
    },
    "VENDORS_MISSING_PAYMENT_TERMS": {
        "en": IssueText("Vendors without payment terms", "Maintain payment terms for the affected vendors."),
        "de": IssueText("Kreditoren ohne Zahlungsbedingungen", "Zahlungsbedingungen bei den betroffenen Kreditoren pflegen."),
    },
    "VENDORS_MISSING_COUNTRY_CODE": {
        "en": IssueText("Vendors without a country/region code", "Maintain the country/region code for the affected vendors."),
        "de": IssueText("Kreditoren ohne Länder-/Regionscode", "Länder-/Regionscode für die betroffenen Kreditoren pflegen."),
    },
    "VENDORS_MISSING_EMAIL": {
        "en": IssueText("Vendors without an email address", "Add email addresses for the affected vendors."),
        "de": IssueText("Kreditoren ohne E-Mail-Adresse", "E-Mail-Adressen der betroffenen Kreditoren ergänzen."),
    },
    "VENDORS_MISSING_PHONE_NO": {
        "en": IssueText("Vendors without a phone number", "Maintain phone numbers for the affected vendors."),
        "de": IssueText("Kreditoren ohne Telefonnummer", "Telefonnummern der betroffenen Kreditoren pflegen."),
    },
    "VENDORS_MISSING_VENDOR_POSTING_GROUP": {
        "en": IssueText("Vendors without a vendor posting group", "Maintain vendor posting groups for the affected vendors."),
        "de": IssueText("Kreditoren ohne Kreditorenbuchungsgruppe", "Kreditorenbuchungsgruppen der betroffenen Kreditoren pflegen."),
    },
    "VENDORS_MISSING_GEN_BUS_POSTING_GROUP": {
        "en": IssueText("Vendors without a general business posting group", "Maintain general business posting groups for the affected vendors."),
        "de": IssueText("Kreditoren ohne Geschäftsbuchungsgruppe", "Geschäftsbuchungsgruppen der betroffenen Kreditoren pflegen."),
    },
    "ITEMS_MISSING_CATEGORY": {
        "en": IssueText("Items without an item category", "Add item categories for the affected items."),
        "de": IssueText("Artikel ohne Artikelkategorie", "Artikelkategorien der betroffenen Artikel ergänzen."),
    },
    "ITEMS_MISSING_BASE_UNIT": {
        "en": IssueText("Items without a base unit of measure", "Add a base unit of measure for the affected items."),
        "de": IssueText("Artikel ohne Basiseinheit", "Basiseinheit der betroffenen Artikel ergänzen."),
    },
    "ITEMS_MISSING_GEN_PROD_POSTING_GROUP": {
        "en": IssueText("Items without a general product posting group", "Maintain general product posting groups for the affected items."),
        "de": IssueText("Artikel ohne Produktbuchungsgruppe", "Produktbuchungsgruppen der betroffenen Artikel pflegen."),
    },
    "ITEMS_MISSING_INVENTORY_POSTING_GROUP": {
        "en": IssueText("Items without an inventory posting group", "Maintain inventory posting groups for the affected items."),
        "de": IssueText("Artikel ohne Lagerbuchungsgruppe", "Lagerbuchungsgruppen der betroffenen Artikel pflegen."),
    },
    "ITEMS_MISSING_VAT_PROD_POSTING_GROUP": {
        "en": IssueText("Items without a VAT product posting group", "Maintain VAT product posting groups for the affected items."),
        "de": IssueText("Artikel ohne MwSt.-Produktbuchungsgruppe", "MwSt.-Produktbuchungsgruppen der betroffenen Artikel pflegen."),
    },
    "ITEMS_MISSING_VENDOR_NO": {
        "en": IssueText("Items without a default vendor", "Review and add the default vendor for the affected items."),
        "de": IssueText("Artikel ohne Standardkreditor", "Standardkreditor der betroffenen Artikel prüfen und ergänzen."),
    },
}


def issue_text(issue_code: str, language: object | None) -> IssueText:
    translations = ISSUE_TEXTS[issue_code]
    return translations.get(normalize_language(language), translations["en"])


def summary_headline(score: int, language: object | None) -> str:
    lang = normalize_language(language)
    if score >= 90:
        return "Gute Datenqualität mit einzelnen Lücken" if lang == "de" else "Good data quality with a few gaps"
    if score >= 75:
        return "Ordentliche Datenqualität mit erkennbarem Verbesserungspotenzial" if lang == "de" else "Sound data quality with clear room for improvement"
    return "Erhöhter Handlungsbedarf bei der Datenqualität" if lang == "de" else "Data quality requires increased attention"
