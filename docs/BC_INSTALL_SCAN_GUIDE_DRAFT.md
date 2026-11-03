# BCSentinel — Install & Run Your First Scan

Status: **text/content ready; final screenshots required after BC Online 1.0.2.30 acceptance**  
Audience: Fiverr Quick Assessment / Full Assessment customers  
Target: Microsoft Dynamics 365 Business Central Online

> This guide intentionally contains screenshot placeholders. Do not publish the final customer PDF until the accepted 1.0.2.30 Extension has been installed in a real BC Online tenant and every screenshot/caption has been verified against the runtime UI.

## Before you start

You need:

- Microsoft Dynamics 365 Business Central **Online**;
- an authorized Business Central administrator who can install the BCSentinel `.app` Extension;
- the BCSentinel Extension file supplied for the controlled pilot;
- the BCSentinel pilot Registration Invite Code supplied through the approved onboarding process;
- permission to approve the BCSentinel Data Processing Consent;
- a report/notification email address and preferred language for lifecycle/report communication.

### Security

Never send Business Central passwords, API tokens, Microsoft credentials or other secrets through Fiverr. BCSentinel registration creates/stores its own technical token securely; the token is not displayed to the customer and must not be copied into Fiverr.

---

## Step 1 — Install the BCSentinel Extension

1. Sign in to the Business Central Online environment that should be assessed.
2. Open **Extension Management**.
3. Upload/install the supplied BCSentinel `.app` file.
4. Wait until Business Central confirms that **BCSentinel** is installed.

**Expected result:** BCSentinel is listed as installed and its pages/actions are available.

**Screenshot S1:** Extension Management showing the installed BCSentinel Extension.

---

## Step 2 — Assign the pilot permission set

For the controlled pilot, assign the combined **BCSENTINEL PILOT** permission set to the pilot user. It combines the Setup, Scan and Viewer permissions needed for the intended customer journey without granting SUPER.

Do not add SUPER merely to make a failing step work. A permission failure must be captured as acceptance evidence and fixed before release.

**Expected result:** The pilot user can perform the approved BCSentinel flow using `BCSENTINEL PILOT` without SUPER.

**Screenshot S2:** User permission assignment showing BCSENTINEL PILOT and no SUPER.

---

## Step 3 — Open BCSentinel Setup

1. Use Business Central search (**Tell Me**) and open **BCSentinel Setup**.
2. Confirm that the API Base URL points to the approved BCSentinel environment. Production default is `https://api.bcsentinel.com`.
3. Do not enter or request an API token manually.

The internal Tenant ID is intentionally not a customer requirement and may be hidden in the UI.

**Screenshot S3:** BCSentinel Setup — General section.

---

## Step 4 — Review consent and onboarding settings

1. Review the **Data Processing Notice**.
2. Enable **Data Processing Consent** only if you are authorized to approve the described processing.
3. Enter the supplied **Registration Invite Code** when the controlled pilot requires it.
4. Configure the report/notification email and preferred language in the BCSentinel onboarding/lifecycle settings exposed by the accepted Extension flow.

The report/notification email is used for technical lifecycle/report delivery. It is not a request to move Fiverr commercial communication or payment off-platform.

**Screenshot S4:** Data Processing Consent + onboarding/invite fields.  
**Screenshot S5:** Report/notification email + language settings, using the exact accepted runtime page.

---

## Step 5 — Register the tenant

1. In **BCSentinel Setup**, select **Register Tenant**.
2. Registration is enabled only when the required setup conditions are met, including Data Processing Consent and an API Base URL.
3. Wait for the confirmation that BCSentinel tenant registration completed.
4. If shown, verify **Registered = Yes** / registration status.

If registration is incomplete, do not repeatedly reset or reinstall the Extension. Capture the displayed error and contact the BCSentinel seller through Fiverr.

**Expected result:** Tenant registration completes and BCSentinel product access can be refreshed.

**Screenshot S6:** Registered state after successful registration.

---

## Step 6 — Test the BCSentinel connection

1. Select **Test BCSentinel Connection**.
2. Confirm that the connection completes without an error.
3. If necessary, select **Refresh Product Access** after the seller has confirmed the Fiverr order/entitlement.

**Expected result:** The Extension can communicate with BCSentinel and current product access is visible.

**Screenshot S7:** Successful connection / Product Access section.

---

## Step 7 — Review scan scope

BCSentinel supports the standard scan modules shown in Setup. For the controlled pilot, the normal complete scan scope uses the enabled standard modules, including:

- System / Setup
- Finance
- Sales
- Purchasing
- Inventory
- CRM / Contacts
- Manufacturing
- Service
- Jobs / Projects
- HR / Resources

The standard initial Data Health Scan is technically the same full scan for Free, Quick and Full. The purchased Fiverr product controls which result layer is unlocked; it does not create a separate reduced scan engine.

Do not disable modules merely to reduce the Fiverr record-volume class unless this has been explicitly agreed as the intended assessment scope.

**Screenshot S8:** Enabled Scan Modules section.

---

## Step 8 — Start the Data Health Scan

1. In **BCSentinel Setup**, open the **Scan** action group.
2. Select **Start Scan**.
3. Read the performance notice.
4. Confirm only when the scan should start.

BCSentinel warns that performance may be affected during live operations. Running the scan outside busy business hours is recommended for larger environments.

**Important:** A fresh tenant receives one initial Free Entry scan credit. Quick Assessment and Full Assessment reuse this same qualifying initial scan and do **not** require a second scan. A new scan is created later only for Validation after remediation.

**Screenshot S9:** Start Scan action + confirmation dialog.

---

## Step 9 — Monitor scan progress

1. Open **Scan History** / **DH Deep Scan Runs**.
2. Locate the newly started scan.
3. Wait until the run reaches its successful completed state.
4. Do not start another scan while the initial scan is still running.

For the accepted full standard scope, the runtime QA target is all enabled standard modules/checks. The current product contract contains up to 10 standard business areas and 199 automated checks; the exact executed scope must be confirmed from the completed run rather than assumed from this guide.

**Screenshot S10:** Scan History while running.  
**Screenshot S11:** Completed scan showing final status/scope.

---

## Step 10 — Open the BCSentinel report

After the scan completes:

1. Select the completed scan/run.
2. Use the primary **Open BCSentinel Report** action.
3. Use **Open BCSentinel PDF** when a PDF version is required.

The Extension asks the backend for the highest valid report variant for that concrete scan:

**Validation → Full Assessment → Quick Assessment → Free Health**

This means customers should normally use the primary report action instead of manually choosing a report tier.

### Fiverr Quick Assessment

Quick unlocks the Top 5 prioritized findings and concise next steps from the same initial scan. It creates no new scan and remains available until explicitly revoked.

### Fiverr Full Assessment

Full unlocks the complete paid assessment boundary for the same qualifying initial scan for the defined detail window. No rescan is required when upgrading Quick → Full.

### Validation

Validation is a separate follow-up after remediation and requires a prior paid Full Assessment baseline. Validation grants exactly one new scan credit; that new scan is compared with the paid baseline.

**Screenshot S12:** Completed scan report actions.  
**Screenshot S13:** Correct report opened from BC.

---

## Troubleshooting checklist

Before contacting support, verify:

- Business Central is Online, not an unsupported on-premises launch scenario;
- the correct company/environment is open;
- BCSentinel 1.0.2.30 is installed;
- the user has **BCSENTINEL PILOT** and does not rely on SUPER;
- Data Processing Consent is enabled;
- the pilot Registration Invite Code is correct when required;
- tenant registration completed;
- **Test BCSentinel Connection** succeeds;
- the scan is not already running;
- the Fiverr order/product has been confirmed before expecting paid Quick/Full/Validation detail;
- no passwords, API tokens or secrets are sent in the support message.

When reporting an issue through Fiverr, include only non-secret diagnostic context such as company/environment name, the visible BCSentinel status/error text, scan/run identifier if available and a screenshot with sensitive unrelated data removed.

---

## Final screenshot acceptance checklist

Before this guide becomes customer-final:

- [ ] S1 Extension Management
- [ ] S2 BCSENTINEL PILOT permission assignment without SUPER
- [ ] S3 BCSentinel Setup / API Base URL
- [ ] S4 Consent + invite onboarding
- [ ] S5 report/notification email + language exact runtime UI
- [ ] S6 Registered state
- [ ] S7 Connection/Product Access
- [ ] S8 enabled modules
- [ ] S9 Start Scan confirmation
- [ ] S10 running scan
- [ ] S11 completed scan
- [ ] S12 report actions
- [ ] S13 opened report
- [ ] all labels match Extension 1.0.2.30 runtime exactly
- [ ] screenshots contain no tenant secrets, tokens or unrelated customer data
- [ ] DE and EN guide wording checked against the accepted Extension localization
