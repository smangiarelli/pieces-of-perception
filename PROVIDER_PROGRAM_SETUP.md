# Provider Partner Program — Deploy Checklist (B2B-3 / B2B-5 / B2B-8)

Staged 2026-07-15. Everything is built and syntax-checked; nothing is live
until you do the steps below.

**⚠ SEQUENCING: wait for the attorney's OK on the consent-to-share wording
before Step 2 (the questionnaire upload).** Step 1 (SQL) is safe to run any
time — the new tables sit dormant until a provider exists. The consent
checkbox only ever appears for families who claim a provider-tagged code, so
normal families are unaffected either way.

---

## Step 1 — Supabase SQL (5 min, safe any time)

1. Supabase → SQL Editor → + New query
2. Paste ALL of `supabase_provider_partners.sql` → Run
3. Success looks like: **"Success. No rows returned."**

Creates: `providers`, `provider_intakes`, `beta_invites.provider_id`,
`get_my_provider()` (questionnaire), `submit_provider_intake()` (intake form).
GRANTs included (service_role + function EXECUTEs — the 42501 gotcha is
handled).

## Step 2 — GitHub upload (after attorney OK) (5 min)

GitHub web UI → your site repo → **Add file → Upload files** →
drag these 2 from `piecesofperception-site/`:

- `questionnaire.html`  (adds the conditional 6th consent checkbox)
- `provider-intake.html`  (new page — unlisted, noindex, not linked anywhere)

Commit. Done — the checkbox stays invisible until a family uses a
provider-tagged code.

## Step 3 — End-to-end test (15 min, do once before partner #1)

1. SQL Editor — create a test provider (copy the `intake_key` it returns):
   ```sql
   INSERT INTO public.providers (name, code_prefix, contact_name, contact_email, service_type)
   VALUES ('Test Practice (DELETE ME)', 'TST', 'Test', 'you@example.com', 'OT')
   RETURNING id, intake_key;
   ```
2. Issue one test code:
   ```sql
   INSERT INTO public.beta_invites (code, family_label, provider_id)
   VALUES ('TST-001', 'test provider code',
           (SELECT id FROM public.providers WHERE code_prefix = 'TST'));
   ```
3. In an **incognito window**: beta-portal.html → sign up with a throwaway
   email + code TST-001 → open the questionnaire.
   **Success looks like: SIX checkboxes on the agreement screen — the sixth
   says "Sharing with your provider" and names Test Practice.** Continue is
   disabled until all six are checked.
4. Open `/provider-intake.html` → fill it using the intake_key from step 1 +
   family code TST-001 → Submit.
   **Success looks like: the green "Intake received" screen.**
   Then verify the row: `SELECT * FROM provider_intakes;`
5. Also confirm a NORMAL flow is untouched: log in as any non-provider test
   account → questionnaire shows the usual FIVE checkboxes.
6. Cleanup:
   ```sql
   DELETE FROM public.provider_intakes WHERE family_code = 'TST-001';
   DELETE FROM public.beta_invites   WHERE code = 'TST-001';
   DELETE FROM public.providers      WHERE code_prefix = 'TST';
   ```
   (If a throwaway auth user was created, remove it in Authentication → Users.)

---

## Per-partner onboarding (once signed) — the runbook

1. **Create the provider** (SQL snippet A in `supabase_provider_partners.sql`)
   → email them the `intake_key` + the link to `/provider-intake.html`.
2. **Issue their codes** (snippet B) — as many as the credit pack they bought.
3. **Ledger**: add the partner + purchase rows in
   `PoP_B2B_Credits_Ledger.xlsx` when the Stripe invoice is paid.
4. Partner gives a family a code → family completes questionnaire (consents
   to sharing via the 6th checkbox) → partner submits the intake form.
5. **Before rendering**: confirm the consent — either the
   `provider_share_consent` row in `policy_acknowledgments` for that user, or
   `ack_provider_share` inside the pulled answers.json. **No consent = no
   delivery to the provider.**
6. Render with the partner's branding (B2B-4 manual logo swap in
   `provider_demo/provider_branding.py`), **email the PDFs to the partner
   contact from hello@** (B2B-8 decision: email delivery at launch — no
   dashboard upload for provider-flow families), log 1 credit in Usage.

## How the consent shows up downstream

- `policy_acknowledgments`: row with `policy_type = 'provider_share_consent'`,
  `policy_version = 'v1.0 — [Provider Name]'`
- `answers.json`: field `ack_provider_share = "Yes — I consent to sharing my
  answers and reports with [Provider Name]."` (travels through the pipeline
  and the report Q&A appendix automatically)
