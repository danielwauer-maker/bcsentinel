# LP-GL-01 – Positioning and Information Architecture

Status: Implemented as the canonical content and structure contract for the landing-page redesign.

## 1. Objective

BCSentinel must be positioned as a focused enterprise SaaS product for Microsoft Dynamics 365 Business Central that turns data-quality findings into measurable business decisions.

The landing page must explain within seconds:

1. what BCSentinel analyzes,
2. why the result matters commercially,
3. what the customer receives,
4. how Assessment, Validation and Monitoring relate to each other,
5. how Estimated Loss is calculated,
6. why the product can be trusted with business-critical ERP data.

## 2. Canonical product language

### Commercial products

- Assessment
- Validation
- Monitoring

### Experience modes

- free
- assessment
- validation
- monitoring
- locked

### Mandatory terminology rules

- `Assessment` is the visible product name for the initial paid deep scan.
- `Validation` is the visible product name for the follow-up confirmation step.
- `Monitoring` is the visible product name for continuous recurring control.
- `Premium` must not appear as a visible product name.
- `Full Analysis` may only be used descriptively, never as the canonical product name.
- The technical code `full_analysis` remains untouched where required for compatibility.
- `Validation Check` may be used in technical or transitional contexts, but customer-facing copy should prefer `Validation`.
- `Estimated Loss` is always described as a modelled estimate, not as a guaranteed financial loss.
- `Potential Saving` is always described as a realistic improvement potential, not as a guaranteed saving.

## 3. Positioning statement

### English

BCSentinel is a data-health-management and executive-assessment solution for Microsoft Dynamics 365 Business Central. It detects data-quality risks, evaluates their operational and financial relevance, and shows teams what to address first.

### German

BCSentinel ist eine Data-Health-Management- und Executive-Assessment-Lösung für Microsoft Dynamics 365 Business Central. Sie erkennt Datenqualitätsrisiken, bewertet deren operative und finanzielle Relevanz und zeigt Teams, welche Maßnahmen zuerst umgesetzt werden sollten.

## 4. Core promise

### English

Turn Business Central data quality into measurable business decisions.

BCSentinel detects data-quality risks, estimates their operational and financial impact, and shows your teams what to fix first.

### German

Machen Sie die Datenqualität in Business Central messbar und steuerbar.

BCSentinel erkennt Datenqualitätsrisiken, schätzt ihre operativen und finanziellen Auswirkungen und zeigt Ihren Teams, was zuerst behoben werden sollte.

## 5. Audience-specific value propositions

### Management and CFO

- Understand the business impact of poor ERP data.
- Prioritize improvement initiatives using financial relevance.
- Receive an executive-ready report instead of technical raw data.
- Track whether corrective actions create measurable improvement.

### IT leaders and ERP owners

- Identify hidden data-quality risks across Business Central modules.
- Standardize issue evaluation and remediation priorities.
- Document exceptions and improvement progress.
- Establish continuous data-health governance.

### Business Central partners and consultants

- Run repeatable customer assessments.
- Create management-ready deliverables from technical findings.
- Validate remediation work.
- Extend advisory and managed-service offerings.

### Managed service providers

- Support repeatable data-health processes across customers.
- Detect critical changes early.
- Provide standardized monitoring and reporting.
- Build recurring data-governance services.

## 6. Primary conversion paths

### Main customer path

1. Understand the value proposition.
2. View a realistic product and report preview.
3. Understand how Estimated Loss is calculated.
4. Review Assessment, Validation and Monitoring.
5. Review security and data-processing information.
6. Start an Assessment or request onboarding.

### Executive path

Hero → Business impact → Estimated Loss example → Executive Report → Assessment CTA

### IT and ERP path

Hero → How it works → Findings → Security → FAQ → Assessment CTA

### Partner path

Hero → Partner value → Product lifecycle → Findings and report → Partner contact or registration

## 7. CTA hierarchy

### Primary CTA

English: `Start Assessment`

German: `Assessment starten`

During a controlled pilot or when self-service checkout is not generally available, use:

English: `Request an Assessment`

German: `Assessment anfragen`

### Secondary CTA

English: `View sample report`

German: `Beispielreport ansehen`

### Estimated Loss CTA

English: `See how Estimated Loss is calculated`

German: `So wird der Estimated Loss berechnet`

### Supporting CTAs

- View Findings
- Explore Security
- Talk to us
- Partner with BCSentinel
- Open Dashboard

The hero must not use `See products` as its primary action.

## 8. Canonical homepage information architecture

### 1. Header

- Product
- How it works
- Findings
- Report
- Security
- Pricing
- Resources
- DE / EN
- Sign in
- Primary Assessment CTA

### 2. Hero

Purpose: explain the product and create immediate trust.

Required elements:

- Business Central-specific category label
- core promise
- concise explanation
- primary Assessment CTA
- sample-report CTA
- real product composition using Dashboard, Findings and Executive Report
- concise trust signals

### 3. Trust strip

Use only verifiable product capabilities. Do not use invented customer logos or unsupported certifications.

Recommended topics:

- Built for Microsoft Dynamics 365 Business Central
- Executive PDF reporting
- Prioritized remediation guidance
- Tenant-aware processing
- Assessment, Validation and Monitoring

### 4. Problem and business impact

Explain that poor ERP data usually creates gradual operational cost rather than one visible incident.

Cover:

- manual rework
- process delays
- unreliable reporting
- margin leakage
- recurring corrections
- governance gaps

### 5. Estimated Loss transparency preview

This section is mandatory and appears early on the homepage.

It must include:

- one complete calculation example,
- clear separation between measured scan data and model assumptions,
- a disclaimer that the value is an estimate,
- a prominent link to `loss-examples`.

Example structure:

- 43 affected records
- 3 relevant events per year
- 15 minutes correction effort
- EUR 42 process cost per hour
- Estimated annual loss: EUR 1,354.50

### 6. How BCSentinel works

Management-level flow:

Connect → Assess → Improve → Monitor

Detailed technical flow:

Connect → Scan → Evaluate → Prioritize → Improve → Validate → Monitor

### 7. Product lifecycle

Assessment → Validation → Monitoring

#### Assessment

Understand the current data-health position.

#### Validation

Confirm that corrective actions worked.

#### Monitoring

Keep data health under continuous control.

Assessment is always marked as the recommended starting point.

### 8. Findings

Findings are the central product proof.

Show:

- severity,
- title,
- affected records,
- business impact,
- recommendation,
- module,
- status,
- exception state,
- priority.

### 9. Executive Report

Position the report as the bridge between technical analysis and management decisions.

Show:

- Data Health Score,
- key KPIs,
- severity distribution,
- Estimated Loss,
- Potential Saving,
- prioritized next steps,
- report metadata.

Primary CTA: download or view a sample report.

### 10. Dashboard

Show realistic views for:

- Overview
- Findings
- Monitoring

Marketing visuals must stay close to the real application.

### 11. Audience benefits

Use a tabbed or segmented presentation for:

- Management and CFO
- IT and ERP owners
- BC partners and consultants
- Managed service providers

### 12. Security and trust

Only verified claims may be used.

Structure:

- Access
- Processing
- Governance

Cover where technically correct:

- HTTPS communication
- tenant and company identification
- role-based access
- controlled access lifecycle
- execution tokens and leases
- auditable scan lifecycle
- data-retention controls
- no uncontrolled direct database access

### 13. Pricing

Present:

- Assessment as one-time entry product
- Validation as one-time confirmation product
- Monitoring monthly and annual

Pricing must state:

- B2B context
- net or gross pricing
- access duration
- included capabilities
- subscription term and cancellation rules where applicable

### 14. FAQ

Minimum topics:

- Does BCSentinel change data?
- Which BC versions are supported?
- How long does an Assessment take?
- What data is transferred?
- How is Estimated Loss calculated?
- What is the difference between Assessment and Validation?
- Can findings be documented as exceptions?
- What happens when access expires?
- Is Monitoring mandatory?
- Can partners run BCSentinel for customers?
- Where is the service hosted?

### 15. Final CTA

English headline:

Know the health of your Business Central data before it becomes a business problem.

German headline:

Erkennen Sie den Zustand Ihrer Business-Central-Daten, bevor daraus ein Geschäftsproblem wird.

Actions:

- Start or request Assessment
- View sample report

### 16. Footer

Required links:

- Product
- Estimated Loss methodology
- Sample Report
- Security
- Pricing
- Partners
- Contact
- Sign in
- Impressum
- Privacy
- Terms where applicable

## 9. `loss-examples` product role

The existing `landingpage/loss-examples.html` page is a P0 product asset and must remain available.

It is not a secondary blog article. It is the methodological trust layer behind the financial-impact promise.

### Required integrations

- homepage Estimated Loss section,
- KPI explanation links,
- Findings section,
- Executive Report section,
- FAQ,
- footer resources,
- future dashboard calculation breakdown.

### Required content principles

Each example must distinguish:

- what BCSentinel directly measures,
- what BCSentinel derives,
- what BCSentinel assumes,
- the formula used,
- the time horizon,
- the resulting Estimated Loss,
- the operational interpretation,
- the recommended corrective action.

### Required disclaimer

English:

Estimated Loss is a modelled orientation value based on detected data conditions and documented assumptions. It is not a guarantee of costs already incurred or savings that will be achieved.

German:

Der Estimated Loss ist ein modellierter Orientierungswert auf Basis erkannter Datenzustände und dokumentierter Annahmen. Er ist keine Garantie für bereits entstandene Kosten oder tatsächlich erzielbare Einsparungen.

## 10. Messaging exclusions

Do not use:

- Premium as a product name
- Full Analysis as a product name
- guaranteed savings
- guaranteed loss prevention
- unsupported Microsoft partnership claims
- unsupported compliance badges
- invented testimonials
- invented customer logos
- artificial urgency
- vague AI claims
- claims that all customer data stays inside Business Central unless technically true

## 11. Visual communication principles

- Hybrid Enterprise design
- light primary surfaces
- controlled dark Navy report and trust sections
- Orange reserved for primary actions
- real product visuals instead of stock imagery
- fewer repetitive floating cards
- restrained shadows and blur
- clear typography and generous whitespace
- no generic AI illustrations
- no decorative claims without product evidence

## 12. Acceptance criteria for LP-GL-01

- Canonical product terminology is documented.
- The core DE and EN positioning is approved as implementation baseline.
- Primary and secondary CTA hierarchy is fixed.
- Audience-specific value propositions are defined.
- The homepage section order is fixed.
- `loss-examples` is defined as a P0 trust and conversion asset.
- Unsupported marketing claims are explicitly prohibited.
- Future design and implementation sprints can reference this file as their content contract.

## 13. Follow-up sprint dependency

LP-GL-02 must convert this contract into the BCSentinel marketing design system.

LP-GL-03 must use this information architecture for the final desktop and mobile mockups.

LP-GL-04 and later implementation sprints must not reintroduce legacy visible product terms.