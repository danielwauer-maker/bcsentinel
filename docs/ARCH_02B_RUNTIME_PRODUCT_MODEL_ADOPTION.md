# ARCH-02B – Runtime Product Model Adoption

Status: In Progress

## Ziel

Das in ARCH-02A eingeführte kanonische Produktmodell wird schrittweise in die tatsächlichen Runtime-Entscheidungen übernommen, ohne bestehende Kundenrechte zu erweitern, gespeicherte Produktcodes zu ändern oder eine Datenmigration auszulösen.

## Adoptionsstrategie

ARCH-02B verwendet eine doppelte Sicherheitsgrenze:

1. Das kanonische Product Model muss das erforderliche Offer beziehungsweise Entitlement liefern.
2. Die bestehende Legacy-Entscheidung muss den Zugriff weiterhin erlauben.

Eine bezahlte Capability wird nur gewährt, wenn beide Bedingungen erfüllt sind. Damit kann die Migration keine zusätzlichen Rechte erzeugen. Inkonsistente Zustände werden fail-closed behandelt.

## Umgesetzt

- zentraler `RuntimeProductPolicy` unter `backend/app/core/runtime_product_policy.py`
- kanonische Auflösung aktiver Offers, Experience Mode, Entitlements und Access State
- explizite Kennzeichnung `canonical_with_legacy_guard` im Access Snapshot
- Snapshot-Version `p0d-v3-runtime-product-model`
- kanonische Runtime-Prüfung für:
  - Product Access
  - Findings Full Access
  - Executive Report Access
  - Monitoring Access
  - Subscription State
  - Paid Deep Scan Access
- Free Score Scan bleibt über den bestehenden Free-Access-Pfad kompatibel
- bestehende Legacy-Flags bleiben während ARCH-02B als Guard aktiv
- keine Datenmigration
- keine Änderung an Checkout-, Stripe- oder Storage-Codes

## Fail-closed Regeln

- Legacy-Flag ohne kanonisches Offer/Entitlement gewährt keinen bezahlten Zugriff.
- Kanonisches Offer/Entitlement ohne Legacy-Freigabe gewährt keinen Zugriff.
- Free Scan bleibt unabhängig von bezahlten Entitlements verfügbar, sofern der bestehende Free-Access-Pfad ihn freigibt.

## Noch zu verifizieren

- fokussierte Product-Model- und Access-Snapshot-Tests
- vollständige Backend-Regression
- BC-AL-Compile und Cop-Gate
- finale Diff- und Kompatibilitätsprüfung

## Nicht Bestandteil dieses Sprints

- Entfernung der Legacy-Felder
- Datenmigration bestehender Lizenzen
- Änderung gespeicherter Produktcodes
- Änderung bestehender Kundenrechte
- Änderung an Stripe oder Checkout
- Produktiv-Merge ohne ausdrückliche Freigabe
