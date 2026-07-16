-- =====================================================================
-- Pieces of Perception — B2B Provider Partner Program (B2B-3 + B2B-5)
-- =====================================================================
-- DRAFT staged 2026-07-15. Run AFTER the attorney approves the consent
-- language (the questionnaire checkbox ships in the same deploy).
--
-- HOW TO RUN:  Supabase → SQL Editor → + New query → paste ALL → Run
-- Expect: "Success. No rows returned."
-- Idempotent: safe to re-run.
--
-- What this creates:
--   1. providers            — one row per signed partner
--   2. beta_invites.provider_id — tags provider-issued codes
--   3. provider_intakes     — the 5-question intake (web form posts here)
--   4. get_my_provider()    — questionnaire asks "did this family come
--                             through a provider code?" (consent checkbox)
--   5. submit_provider_intake() — validated insert used by
--                             provider-intake.html (no provider login)
-- =====================================================================

-- 1. Providers ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.providers (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL,                       -- practice display name (appears in consent checkbox)
  code_prefix   text NOT NULL UNIQUE,                -- e.g. 'RIV' → codes RIV-001, RIV-002...
  contact_name  text,
  contact_email text,
  service_type  text,                                -- ABA / OT / SLP / direct-support / ...
  intake_key    text NOT NULL DEFAULT encode(gen_random_bytes(12), 'hex'),  -- secret for the intake form
  active        boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.providers ENABLE ROW LEVEL SECURITY;
-- No policies: service role only. (Standing gotcha: new tables need GRANTs.)
GRANT ALL ON public.providers TO service_role;

-- 2. Tag provider-issued invite codes ---------------------------------
ALTER TABLE public.beta_invites
  ADD COLUMN IF NOT EXISTS provider_id uuid REFERENCES public.providers(id) ON DELETE SET NULL;

-- 3. Provider intakes (5 questions, client-level) ----------------------
CREATE TABLE IF NOT EXISTS public.provider_intakes (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id     uuid NOT NULL REFERENCES public.providers(id),
  family_code     text NOT NULL,                     -- the invite code the family used (e.g. RIV-001)
  service_type    text,
  session_format  text,
  session_length  text,
  cadence         text,
  setting         text,
  engagement_goal text NOT NULL,
  known_diagnoses text,                              -- optional 6th question
  created_at      timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.provider_intakes ENABLE ROW LEVEL SECURITY;
GRANT ALL ON public.provider_intakes TO service_role;

-- 4. get_my_provider() — called by questionnaire.html after login ------
--    Returns the provider name for the CURRENT user if (and only if)
--    they claimed a provider-tagged invite code. Empty result otherwise.
CREATE OR REPLACE FUNCTION public.get_my_provider()
RETURNS TABLE (provider_name text)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT p.name
  FROM public.beta_invites bi
  JOIN public.providers p ON p.id = bi.provider_id
  WHERE bi.used_by_user_id = auth.uid()
    AND p.active
  LIMIT 1;
$$;

REVOKE ALL ON FUNCTION public.get_my_provider() FROM public;
GRANT EXECUTE ON FUNCTION public.get_my_provider() TO authenticated;

-- 5. submit_provider_intake() — used by provider-intake.html -----------
--    Providers have no login; the secret intake_key (given at onboarding)
--    authenticates the practice. Validates the key + the family code
--    belongs to that provider, then inserts.
CREATE OR REPLACE FUNCTION public.submit_provider_intake(
  p_intake_key      text,
  p_family_code     text,
  p_service_type    text,
  p_session_format  text,
  p_session_length  text,
  p_cadence         text,
  p_setting         text,
  p_engagement_goal text,
  p_known_diagnoses text DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_provider public.providers%ROWTYPE;
  v_code     text;
BEGIN
  SELECT * INTO v_provider
  FROM public.providers
  WHERE intake_key = p_intake_key AND active;

  IF v_provider.id IS NULL THEN
    RETURN jsonb_build_object('ok', false, 'error',
      'Invalid intake key. Check the key from your onboarding email.');
  END IF;

  v_code := upper(trim(p_family_code));
  IF v_code = '' OR coalesce(trim(p_engagement_goal), '') = '' THEN
    RETURN jsonb_build_object('ok', false, 'error',
      'Family code and engagement goal are required.');
  END IF;

  -- The family code must be one of THIS provider's issued codes.
  IF NOT EXISTS (
    SELECT 1 FROM public.beta_invites
    WHERE code = v_code AND provider_id = v_provider.id
  ) THEN
    RETURN jsonb_build_object('ok', false, 'error',
      'That family code was not issued to your practice. Check the code and try again.');
  END IF;

  INSERT INTO public.provider_intakes
    (provider_id, family_code, service_type, session_format,
     session_length, cadence, setting, engagement_goal, known_diagnoses)
  VALUES
    (v_provider.id, v_code, p_service_type, p_session_format,
     p_session_length, p_cadence, p_setting, trim(p_engagement_goal),
     nullif(trim(coalesce(p_known_diagnoses, '')), ''));

  RETURN jsonb_build_object('ok', true, 'provider', v_provider.name);
END;
$$;

REVOKE ALL ON FUNCTION public.submit_provider_intake(text,text,text,text,text,text,text,text,text) FROM public;
GRANT EXECUTE ON FUNCTION public.submit_provider_intake(text,text,text,text,text,text,text,text,text) TO anon, authenticated;

-- =====================================================================
-- ADMIN SNIPPETS (run per partner at onboarding — keep for reference)
-- =====================================================================
-- A. Create a partner (returns id + the secret intake_key to email them):
-- INSERT INTO public.providers (name, code_prefix, contact_name, contact_email, service_type)
-- VALUES ('Riverside Direct Support', 'RIV', 'Dr. Lee', 'dlee@example.com', 'PASS / respite')
-- RETURNING id, intake_key;
--
-- B. Issue 5 family codes for that partner:
-- INSERT INTO public.beta_invites (code, family_label, provider_id)
-- SELECT 'RIV-' || lpad(n::text, 3, '0'),
--        'Riverside Direct Support — partner code',
--        (SELECT id FROM public.providers WHERE code_prefix = 'RIV')
-- FROM generate_series(1, 5) n
-- ON CONFLICT (code) DO NOTHING;
--
-- C. See a partner's intakes:
-- SELECT family_code, service_type, session_length, engagement_goal, created_at
-- FROM public.provider_intakes
-- WHERE provider_id = (SELECT id FROM public.providers WHERE code_prefix = 'RIV')
-- ORDER BY created_at DESC;
--
-- D. Rotate a compromised intake key:
-- UPDATE public.providers SET intake_key = encode(gen_random_bytes(12),'hex')
-- WHERE code_prefix = 'RIV' RETURNING intake_key;
