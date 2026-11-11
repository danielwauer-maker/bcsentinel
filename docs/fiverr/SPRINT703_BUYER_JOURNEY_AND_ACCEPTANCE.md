# Sprint 7.03 — Buyer journey, exception playbook and acceptance matrix

**Evidence date:** 2026-11-11. **Scope:** documentation and operator/customer communication only. **TECHNICAL DOCUMENTATION CANDIDATE — NO PRODUCT CONTRACT APPROVAL / NO GO-LIVE.**

## Authority and version pinning

| Source | Reviewed position | Implication |
|---|---|---|
| Core main `release/current-product-state.json` (blob `924cc4993ba58ada9dc1133b08d8144f1826b4b7`) | permanent paid Quick, Full 7d, Validation 7d; older USD matrix | Existing deployed/legacy-facing snapshot; do not silently remove Quick or reduce grandfathered rights |
| Product System main `00-core/product-model.yaml` (`bcs-product-model-v2.1`, 2026-10-09) | approved Assessment, Validation, Monitoring; Free not a commercial offer; no canonical Quick/Renewal offer | Normative CURRENT contract, **not** approval of the new 14d Access-v2 variant |
| Core Draft PR #154, HEAD `ad7f570c21c37fbb6b0cce04e8c462a76c604947` | proposed Free/Full14/Renewal14/Renewal+Validation/Monitoring; paid v2 SKUs unpriced and disabled | Target-only copy. No claim of current activation or settled commercial price |
| Core Draft PR #162, HEAD `a8b870eb41d29913cc0837a558c30637be8c57f2` | incomplete per-check/record identity evidence and BC27 runtime gate | Never promise proof of all resolved/new records or validated savings |
| Product-contract audit PR #164 | PC-01..PC-08 unresolved | Contract/legacy compatibility signoff prerequisite |
| Uploaded DEV-first tracker dated 2026-11-11, Sprint-Tracker row 45 | 7.03 Buyer Requirements, FAQ, Delivery/Revision Templates; no passwords or tokens on Fiverr; depends on 7.01 | This file is supporting evidence only; source tracker status is not changed by this PR |

**Release rule:** this kit is target copy for three planned Fiverr Gigs (Full, Validation, Monitoring), **not evidence** that three Gigs are currently sellable. Main's legacy Quick offering still exists as a separate historical/current implementation claim. Do not delete a purchased Quick entitlement, promise v2 to existing purchasers, or relabel old 7-day customers automatically.

## Buyer journey: control points and fail-closed outcomes

| ID | Step | Required seller/operator evidence | Customer message / outcome if blocked | Status |
|---|---|---|---|---|
| BJ-01 | Inquiry and eligibility | BC Online, intended tenant/company/environment, nonsecret scope, estimated volume | Scope clarification; no password, MFA, API token, credit card or raw export requested | COPY PASS; actual qualification untested |
| BJ-02 | Fiverr order and payment | Confirmed Fiverr order identifier, approved price/package, channel and payment state; no off-platform payment | Hold fulfillment on missing/uncertain payment; use Fiverr resolution tools | TEMPLATE PASS; live order pending |
| BJ-03 | Installation and registration | Authorized BC administrator, consent, correct company binding; prevent duplicate initial Free credit | Setup instructions; issue escalation without secrets | TEMPLATE PASS; BC27 runtime pending |
| BJ-04 | Initial scan | Exactly one authorized original Free Deep Scan for first registration; completed/persisted original scan ID | On failure: no claim of successful scan; guide to retry/support without granting unauthorized credit | TEMPLATE PASS; E2E pending |
| BJ-05 | Free report | Aggregate-safe archived Free; do not disclose finding titles, exact EUR, issue codes or root causes | If Free link fails: verify scope, state, safe new link; no report content in Fiverr chat | COPY PASS; E2E pending |
| BJ-06 | Full unlock | Paid verified order → one auditable authorized operator grant; 14d target, no extra scan; same original scan, immutable scope and company | If missing baseline/scope/access: hold, no fabricated report/no second scan | TEMPLATE PASS; v2 approval/runtime pending |
| BJ-07 | Full report delivery | Entitlement current, link/reader securely scoped, reviewed DE/EN PDF/HTML matching actual scan; attach only approved sanitized delivery file | Expired or revoked access: do not bypass; secure reissue only if authorized | TEMPLATE PASS; actual delivery pending |
| BJ-08 | Renewal (not public Gig) | Explicit approved contract, price, paid order, +14d policy incl overlap; zero extra scan | Explain that extension is not automatic and depends on agreed offer | TEMPLATE PASS; policy pending |
| BJ-09 | Validation | Previous **paid Full** qualifying baseline, same permitted company/scope; exactly one authorized credit, new scan and check provenance | If evidence absent: say not comparable; never assert resolved/new/improved or realized savings | TEMPLATE PASS; comparator E2E blocked |
| BJ-10 | Monitoring | Approved subscription/cadence/termination, executed scan schedule, history, notifications, customer report | Do not sell or deliver until operational acceptance | PRELAUNCH ONLY |
| BJ-11 | Revision/support | Scoped to formatting/clarification of same approved report; audit relevant scan/grant/order references | Data fixes, new scans/company or larger volume require separate approved Fiverr order | TEMPLATE PASS |
| BJ-12 | Refund/dispute/cancel | Verified Fiverr resolution/payment event, consumed-vs-unconsumed status, grant state, audit and lawful report retention | No automatic refund promise; reconcile case on Fiverr and revoke only authorized remaining unused rights | TEMPLATE PASS; real refund E2E pending |
| BJ-13 | Final closure | Order ID, scope/version, approved deliverables, access dates, requested revisions and incident ledger | State non-comparable/undelivered elements plainly; never mark blocked service complete | TEMPLATE PASS |

**No secrets:** Do not request passwords, MFA, API keys, share tokens, session tokens, payment data, raw BC records, or client data exports by Fiverr. Redact logs and screenshots. Technical notification email and grants belong in authorized application surfaces, not off-platform sales messages.

## Exceptions and compensation rules (operator internal)

| Scenario | Handling | Forbidden action |
|---|---|---|
| Buyer selected wrong company/environment | Freeze fulfillment, confirm authorized tenant/company via secure app flow; arrange Fiverr scope resolution | Switch paid reports across tenants or reuse another company's scan |
| Registration exists / duplicate attempt | Inspect tenant and original credit history, refuse an unauthorized second Free credit | Re-register to farm scans |
| Initial scan failed, partial, skipped or timed out | Document terminal state, investigate retry path and permitted credit policy; only accept completed evidence | Represent partial run as Full-ready, invent findings |
| Full purchased before successful first scan | Verify order; keep paid grant flow pending until original authorized Free scan and scope pass preflight | Mint second scan or report without source scan |
| Volume exceeds paid tier | Confirm persisted Scan.total_records and tier semantics; propose approved Fiverr Custom Offer/change; stop premium unlock until paid scope resolved | Charge outside Fiverr or silently auto-upgrade |
| Report link expired while paid entitlement remains valid | Reauthenticate and use authorized secure link reissue according to backend policy | Share a permanent bearer token or bypass checks |
| Paid access expired / revoked | Retain permissible Free archive; if reactivation purchased, grant only under reviewed renewal rules | Treat a previously issued link as proof of current entitlement |
| Company, currency or source identity changed | Mark Validation scope non-comparable; request reviewed new baseline/scope decision | Label aggregate deltas as record-level resolved/new evidence |
| Comparison evidence absent | Deliver only an expressly agreed limited explanation, or use Fiverr resolution/extension; do not substitute a fabricated Validation report | Claim all 199 checks are individually traceable |
| Monitoring scan, alert, scheduler or subscription failed | Stop customer claims, document incident and use approved cancellation/remedy rules | Claim availability, SLA, scan cadence or alerts without proof |
| Refund / chargeback before grant | Validate Fiverr payment state and prevent any grant; log outcome | Grant access based on an unverified screenshot |
| Refund / chargeback after grant, **unused** right | Verify authoritative payment/refund event, eligibility and unused grant/credit; revoke or adjust future unused entitlement per approved contract, audit idempotently | Delete historical completed scans or revoke another order |
| Refund after **consumed scan** | Keep completed scan/evidence/audit trace under retention rules; calculate any refund via Fiverr policy and case review | Re-credit/rewrite consumed history by assumption or promise automatic reimbursement |
| Partial refund / disputed transaction / out-of-order event | Put case on hold for manual reconciliation, idempotent event replay and safe authorization decision; escalate to operator | Guess proportional entitlements or accept forged events |
| Buyer requests deletion | Use approved privacy/retention and identity-verification process; communicate through permitted channel | Promise immediate deletion of immutable evidence or backups without legal review |

### Customer-ready exception texts — English

**Failed scan:** “The Data Health Scan did not complete successfully, so no final report can be delivered from that run. We are checking the supported retry options and will agree any delivery adjustment through this Fiverr order. Please do not send credentials or business data.”

**Report access / expiry:** “The report link is unavailable or has expired. We will verify your authorized company and current access rights before issuing any supported replacement link. An expired Full access period cannot be bypassed; any renewal must be agreed through Fiverr.”

**Refund / cancellation request:** “Thank you for raising this. We will review the order, payment status, work already performed and any unused access or scan credits against the agreed terms. Refund or cancellation decisions and communication will be handled through Fiverr's resolution process. We cannot promise an automatic refund or erase an already completed scan.”

**Disputed / pending payment:** “Fulfillment is temporarily on hold while the Fiverr order/payment status is verified. No additional access or scan will be authorized until the case is resolved in the platform.”

**Scope / incompatible Validation:** “The follow-up scan cannot currently be compared reliably with the original assessment for the specified company or checks. We will clearly identify the limitation and discuss supported delivery or resolution options through Fiverr, rather than report unverified improvements.”

### Kundentexte — Deutsch

**Scan fehlgeschlagen:** „Der Data Health Scan wurde nicht erfolgreich abgeschlossen. Deshalb kann aus diesem Lauf kein abschließender Bericht geliefert werden. Wir prüfen zulässige Wiederholungsmöglichkeiten und stimmen eine gegebenenfalls nötige Lieferanpassung über diesen Fiverr-Auftrag ab. Bitte senden Sie keine Zugangsdaten oder Geschäftsdaten.“

**Berichtslink / Ablauf:** „Der Berichtslink ist nicht mehr verfügbar oder abgelaufen. Vor einem zulässigen neuen Link prüfen wir die berechtigte Gesellschaft und die aktuell gültigen Zugriffsrechte. Ein abgelaufener Full-Zugriff wird nicht umgangen; eine Verlängerung muss über Fiverr vereinbart werden.“

**Refund / Stornierung:** „Vielen Dank für Ihre Nachricht. Wir prüfen den Bestell- und Zahlungsstatus, bereits erbrachte Leistungen sowie noch ungenutzte Zugriffs- und Scanrechte anhand der vereinbarten Bedingungen. Eine Erstattung oder Stornierung wird ausschließlich über die Fiverr-Abwicklung geklärt. Eine automatische Erstattung oder Löschung abgeschlossener Scans können wir nicht zusagen.“

**Zahlung strittig:** „Die Bearbeitung ist vorübergehend ausgesetzt, bis der Status Ihrer Fiverr-Bestellung beziehungsweise Zahlung geklärt ist. Bis dahin werden keine weiteren Scans oder Freischaltungen veranlasst.“

**Vergleich nicht möglich:** „Der Folgescan lässt sich für den vereinbarten Umfang derzeit nicht zuverlässig mit dem Ausgangs-Assessment vergleichen. Wir benennen die Einschränkung ausdrücklich und stimmen mögliche Liefer- oder Klärungsoptionen über Fiverr ab, statt nicht belegte Verbesserungen zu behaupten.“

## Sprint 7.03 — Acceptance matrix

| Acceptance ID | Requirement | Evidence | Documentation state | External/product gate |
|---|---|---|---|---|
| AC-01 | Three offer descriptions in EN/DE, scope and exclusions | `SPRINT703_FIVERR_BUYER_KIT_EN.md`, `_DE.md` | PASS, candidate | Approved Gig scope/7.01 |
| AC-02 | Buyer questions, confidentiality and minimal information | EN section E / DE section 3; this document | PASS | Live Fiverr form review |
| AC-03 | FAQs, language parity and no guaranteed savings | EN B-D, DE 4 | PASS, wording candidate | Legal/commercial signoff |
| AC-04 | Delivery, revision and support templates | EN F-G / DE 5; exception texts here | PASS | Live order run |
| AC-05 | Free/initial scan/no second credit, current vs target model separate | This authority table, PR #154 and PR #164 | PASS as documented distinction | Product System v2 amendment |
| AC-06 | Quick legacy compatibility not concealed | This authority table, Core current release JSON | PASS | Actual migration/grandfathering |
| AC-07 | Full14 / Renewal14 / Validation-credit semantics qualified | EN A/B/C + this matrix | PASS as **proposal**, not live fact | PR #154 real runtime/BC27 |
| AC-08 | Validation fail-closed missing provenance | EN C/F, this exception playbook, PR #162 | PASS as safe wording | Real comparator E2E |
| AC-09 | Monitoring no false availability or cadence | EN D, DE 2, this journey | PASS as safe wording | Subscription and scheduled scans E2E |
| AC-10 | Refund/chargeback/unused vs consumed rights | This exception playbook and EN/DE texts | PASS as policy-safe draft | Approved Fiverr terms + real event tests |
| AC-11 | Character, category, tags, package, legal, gallery checks | Editorial QA document | PENDING live UI | Fiverr seller interface and assets |
| AC-12 | Actual purchase → operator → scan → report → delivery | Journey table | NOT EXECUTED | Sprint 7.04 and BC/runtime gates |
| AC-13 | No secret transmission, no unauthorized access | EN E/G, DE 3/5 and exception matrix | PASS at copy review | Runtime security / tenant-isolation acceptance |
| AC-14 | Final product and financial approvals | PR #164 PC-01..PC-08 | BLOCKED | Product-owner + Legal |
| AC-15 | PR draft remains no-deploy/no-merge | GitHub PR #165 | DOCUMENTED | Maintainer release review |

**Technical interpretation:** the **documentation deliverables** of tracker 7.03 can be completed independently; the actual wording is a **conditional, non-publishable candidate**. This is **not** a successful BC27 test, implemented 14-day entitlement, approved USD price, paid Fiverr dry run or live Monitoring proof. **Go-live acceptance = NO.**

## Handoff / tracker text

> Sprint 7.03: EN/DE Fiverr Buyer Kit, three scoped Gig drafts, FAQs, buyer requirements, order/delivery/revision/support texts, failed-scan/report-access/refund/chargeback playbook and acceptance matrix documented in Draft PR #165. Documentation technically complete, **not publication-ready**. Product-System/Access-v2 contract and prices, legacy Quick compatibility, Validation provenance, Monitoring runtime, BC27, Fiverr seller UI, legal review and buyer E2E remain external P0 gates. No deployment, merge, payment or Go-Live approval.
