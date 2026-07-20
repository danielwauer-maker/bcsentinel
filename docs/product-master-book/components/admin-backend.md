# Admin-Backend

## Zusammenfassung
Jinja-Adminoberfläche mit HTTP-Basic-Authentifizierung und umfangreichen Formularrouten.

## Erkannte Verantwortlichkeiten
Tenants, Lizenzen/Produkte/Credits, Preise/Kosten, Übersetzungen, E-Mail-Templates, Seitenvisibility, Partner/Provisionen und Audit.

## Erkannte Unterbereiche
Tenantliste/-detail, Konfigurationsansichten, Partner-/Payout-Ansichten und CSV-Exporte.

## Vorhandene Features
ADM-TEN-001, ADM-LIC-001, ADM-CONF-001, ADM-PART-001, ADM-AUDIT-001.

## Teilweise vorhandene Features
ADM-MAIL-001: Testversand hängt von SMTP ab.

## Stubs oder statische Inhalte
Keine komplette Adminroute als Stub nachgewiesen.

## APIs und Schnittstellen
Alle `/admin/*`-Routen, Basic Auth, Form-/CSRF-Prüfung, SMTP.

## Datenmodelle
Tenant-, Lizenz-/Billing-, Partner-, Pricing-, Translation-/Template- und Auditmodelle.

## Tests
`test_admin.py`, `test_pricing.py`, `test_landingpage_visibility.py`, Lokalisierungstests.

## Dokumentation
Architektur- und Pricingdokumente; keine eigenständige vollständige Admin-Bedienungsanleitung gefunden.

## Technische Auffälligkeiten
Mehrere GET-Routen besitzen Slash-Aliase; Mutationen werden im Admin Audit protokolliert.

## Manuell zu prüfen
Rollenmodell über die einzelne Basic-Adminidentität hinaus und reale Bedienabläufe.

## Belegverzeichnis
`backend/app/routers/admin.py`; `admin_tenants.html`; `admin_tenant_detail.html`.
