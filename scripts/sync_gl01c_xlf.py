"""Merge and translate GL-01C generated XLIFF units into de-DE."""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bc-extension" / "Translations" / "BCSentinel.g.xlf"
TARGET = ROOT / "bc-extension" / "Translations" / "BCSentinel.de-DE.xlf"

TRANSLATIONS = {
    "Applied Exception Count": "Anzahl angewandter Ausnahmen",
    "An active DH exception already exists for record %1 and issue %2.": "Für Datensatz %1 und Problem %2 ist bereits eine aktive DH-Ausnahme vorhanden.",
    "A reason is required for a DH exception.": "Für eine DH-Ausnahme ist ein Grund erforderlich.",
    "Runs Run Scan.": "Führt Scan ausführen aus.",
    "Run Scan": "Scan ausführen",
    "Create DH Exception": "DH-Ausnahme erstellen",
    "An issue code is required.": "Ein Problemcode ist erforderlich.",
    "This record will be excluded from this check and from the effective score, penalty, and financial impact calculation until the exception is manually deactivated.": "Dieser Datensatz wird aus dieser Prüfung sowie aus der wirksamen Score-, Penalty- und Finanzwirkung-Berechnung ausgeschlossen, bis die Ausnahme manuell deaktiviert wird.",
    "Exception Details": "Ausnahmedetails",
    "Specifies the check from which the record will be excluded.": "Gibt die Prüfung an, aus der der Datensatz ausgeschlossen wird.",
    "Issue Code": "Problemcode",
    "Specifies the required business reason for the exception.": "Gibt den erforderlichen fachlichen Grund für die Ausnahme an.",
    "Reason": "Grund",
    "Specifies the affected record caption.": "Gibt die Bezeichnung des betroffenen Datensatzes an.",
    "Record Caption": "Datensatzbezeichnung",
    "Specifies the affected record.": "Gibt den betroffenen Datensatz an.",
    "Record No.": "Datensatznr.",
    "Explains how the exception affects the next scan.": "Erläutert, wie sich die Ausnahme auf den nächsten Scan auswirkt.",
    "Score Effect": "Scorewirkung",
    "DH Exception History": "DH-Ausnahmehistorie",
    "Specifies when the action occurred.": "Gibt an, wann die Aktion ausgeführt wurde.",
    "Specifies EXCLUDED for activation, INCLUDED for deactivation, or CORRECTED for a separately documented correction.": "Gibt EXCLUDED für die Aktivierung, INCLUDED für die Deaktivierung oder CORRECTED für eine getrennt dokumentierte Korrektur an.",
    "Specifies who performed the action.": "Gibt an, wer die Aktion ausgeführt hat.",
    "Specifies the reason or comment recorded for the action.": "Gibt den für die Aktion protokollierten Grund oder Kommentar an.",
    "Specifies the affected check.": "Gibt die betroffene Prüfung an.",
    "Customer": "Debitor",
    "Deactivate the DH exception for record %1 and issue %2? The record will be included in the next score calculation.": "DH-Ausnahme für Datensatz %1 und Problem %2 deaktivieren? Der Datensatz wird in die nächste Scoreberechnung einbezogen.",
    "Item": "Artikel",
    "The affected record no longer exists or cannot be opened.": "Der betroffene Datensatz ist nicht mehr vorhanden oder kann nicht geöffnet werden.",
    "Table %1": "Tabelle %1",
    "Exceptions can only be created here for customers, vendors, and items.": "Ausnahmen können hier nur für Debitoren, Kreditoren und Artikel erstellt werden.",
    "Vendor": "Kreditor",
    "Specifies the caption of the affected record.": "Gibt die Bezeichnung des betroffenen Datensatzes an.",
    "Specifies the number of the affected record.": "Gibt die Nummer des betroffenen Datensatzes an.",
    "Specifies whether the exception belongs to a customer, vendor, or item.": "Gibt an, ob die Ausnahme zu einem Debitor, Kreditor oder Artikel gehört.",
    "Record Type": "Datensatzart",
    "Views": "Ansichten",
    "Active": "Aktiv",
    "All": "Alle",
    "Customers": "Debitoren",
    "Inactive": "Inaktiv",
    "Items": "Artikel",
    "Vendors": "Kreditoren",
    "Reactivates the selected exception and excludes the record from the next score calculation.": "Reaktiviert die ausgewählte Ausnahme und schließt den Datensatz aus der nächsten Scoreberechnung aus.",
    "Activate": "Aktivieren",
    "Creates an exception for the current customer, vendor, or item and check.": "Erstellt eine Ausnahme für den aktuellen Debitor, Kreditor oder Artikel und die Prüfung.",
    "Create Exception": "Ausnahme erstellen",
    "Opens the affected Business Central record.": "Öffnet den betroffenen Business Central-Datensatz.",
    "Open Record": "Datensatz öffnen",
    "Shows the activation, reactivation, deactivation, and correction history for the selected record and check.": "Zeigt die Aktivierungs-, Reaktivierungs-, Deaktivierungs- und Korrekturhistorie für den ausgewählten Datensatz und die Prüfung.",
    "Show History": "Historie anzeigen",
    "Opens the central list of active and inactive Data Health exceptions.": "Öffnet die zentrale Liste der aktiven und inaktiven Data Health-Ausnahmen.",
    "DH Exceptions": "DH-Ausnahmen",
}


def main() -> None:
    source_text = SOURCE.read_text(encoding="utf-8")
    target_text = TARGET.read_text(encoding="utf-8")
    target_ids = set(re.findall(r'<trans-unit id="([^"]+)"', target_text))
    missing_blocks: list[str] = []

    for match in re.finditer(r"        <trans-unit id=\"([^\"]+)\".*?</trans-unit>\r?\n", source_text, re.S):
        unit_id, block = match.group(1), match.group(0)
        if unit_id in target_ids:
            continue
        source_match = re.search(r"<source>(.*?)</source>", block, re.S)
        if source_match is None:
            raise RuntimeError(f"Missing source for {unit_id}")
        source_value = html.unescape(source_match.group(1))
        if source_value not in TRANSLATIONS:
            raise RuntimeError(f"Missing German translation: {source_value!r}")
        target_value = html.escape(TRANSLATIONS[source_value], quote=False)
        block = block.replace(
            source_match.group(0),
            source_match.group(0) + f'<target state="translated">{target_value}</target>',
            1,
        )
        missing_blocks.append(block)

    if missing_blocks:
        body_end = "    </body>"
        if body_end not in target_text:
            raise RuntimeError("Target XLIFF body end not found")
        target_text = target_text.replace(body_end, "".join(missing_blocks) + body_end, 1)
        TARGET.write_text(target_text, encoding="utf-8", newline="")
    print(f"Merged translated XLIFF units: {len(missing_blocks)}")


if __name__ == "__main__":
    main()
