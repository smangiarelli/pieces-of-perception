"""Build the IEP Prep Companion PDF.

A parent-voiced document, structured to fit any state's IEP framework
(with RI-specific references). Populated entirely from the family's
questionnaire data — never templated, never reused.

What this IS:
  - The parent's voice and observations, organized to align with the
    sections of a school IEP
  - Suggested goal AREAS to discuss (not pre-written SMART goals)
  - Suggested accommodations to discuss (not prescriptive)
  - Questions to bring to the IEP meeting
  - A primer on the IEP process

What this is NOT:
  - A draft IEP
  - Legal advice
  - A diagnostic instrument
  - A substitute for the school district's IEP team process

Output:
  {first_name}_IEP_Prep_Companion.pdf
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True

# Template-mode swap (mirrors build_comprehensive.py pattern):
if "--template" in sys.argv:
    import jamie_data as _jd
    sys.modules["joey_data"] = _jd

from branding import (
    ACCENT, ACCENT_BG, ACCENT_DARK, WARM, WARM_BG, SAGE, SAGE_BG,
    SKY, SKY_BG, LAVENDER, LAV_BG, ROSE, ROSE_BG, DEEP, TEXT,
    TEXT_LIGHT, BG, BORDER_SOFT, WHITE,
    SERIF_BOLD, SERIF_ITALIC, SANS, SANS_BOLD, SANS_OBLIQUE,
    PAGE_W, PAGE_H, MARGIN_X, CONTENT_W,
    get_styles, page_decoration, cover_decoration,
    callout, section_label, card_grid, make_doc,
    disclaimers_page, parent_support_page,
)
import joey_data as J
from joey_data import (
    CHILD, PARENT, SHARED_QA, COMPREHENSIVE_QA,
    ANCHOR_TRUTHS, SENSORY_MAP, STRENGTHS_CARDS,
    COMM_SAY_DONT, COMM_RULES, TOOLKIT_TIERS,
    CRISIS_STEPS, TRIGGER_SWAPS,
    EXISTING_TEAM, HOME_ACCOMMODATIONS_RELIED_ON,
)
from reportlab.platypus import (Paragraph, Spacer, PageBreak, Table,
                                TableStyle, KeepTogether)
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor

S = get_styles()
TEMPLATE_MODE = False
OUT = os.path.join(HERE, CHILD["first_name"] + "_IEP_Prep_Companion.pdf")

# IEP report uses LAVENDER as primary accent (carries through the doc)
PRIMARY = LAVENDER
PRIMARY_BG = LAV_BG

# Helper: determine if this is a secondary-age student (transition planning)
def _is_secondary():
    try:
        age = int(str(CHILD.get("age", "")).split()[0])
    except (ValueError, IndexError):
        return False
    return age >= 14


# ── Cover ─────────────────────────────────────────────────────────────
def cover():
    items = []
    items.append(Spacer(1, 1.4 * inch))
    items.append(Paragraph(
        '<font color="#8E7FC4" size="10"><b>IEP PREP COMPANION · '
        'PARENT-VOICED · ANY-STATE ADAPTABLE</b></font>',
        ParagraphStyle("ce", fontName=SANS_BOLD, fontSize=10, leading=14,
                       textColor=PRIMARY, alignment=TA_CENTER,
                       spaceAfter=22)))
    items.append(Paragraph(
        f'Bringing {CHILD["first_name"]} {CHILD["last_initial"]}<br/>'
        f'to the IEP table',
        ParagraphStyle("ct", fontName=SERIF_BOLD, fontSize=34, leading=42,
                       textColor=DEEP, alignment=TA_CENTER, spaceAfter=20)))
    items.append(Paragraph(
        ("A parent-prep companion that organizes your child's profile into "
         "the language and sections of an Individualized Education Program. "
         "Walk into the meeting heard, prepared, and aligned with the team."),
        ParagraphStyle("cs", fontName=SANS, fontSize=12.5, leading=20,
                       textColor=TEXT, alignment=TA_CENTER, spaceAfter=22,
                       leftIndent=40, rightIndent=40)))

    # Meta strip
    age_grade = f'{CHILD["first_name"]} {CHILD["last_initial"]}, age {CHILD["age"]}'
    grade = CHILD.get("grade", "")
    meta = [[
        Paragraph(f'<font size="8"><b>PREPARED FOR</b></font><br/>'
                  f'<font size="11">{age_grade}</font>',
                  ParagraphStyle("m1", alignment=TA_CENTER, leading=14)),
        Paragraph(f'<font size="8"><b>PARENT VOICE</b></font><br/>'
                  f'<font size="11">{PARENT["name"]}</font>',
                  ParagraphStyle("m2", alignment=TA_CENTER, leading=14)),
        Paragraph(f'<font size="8"><b>REPORT DATE</b></font><br/>'
                  f'<font size="11">{CHILD.get("report_date", "")}</font>',
                  ParagraphStyle("m3", alignment=TA_CENTER, leading=14)),
    ]]
    mt = Table(meta, colWidths=[CONTENT_W/3]*3)
    mt.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER_SOFT),
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, BORDER_SOFT),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    items.append(mt)
    items.append(Spacer(1, 24))

    # Banner: "Bring to your meeting"
    chip = Table([[Paragraph(
        '<font color="#FFFFFF" size="9"><b>HOW TO USE</b></font><br/>'
        '<font color="#FFFFFF" size="12"><b>Share with the IEP team 1–2 '
        'weeks before the meeting · bring a printed copy to reference</b></font>',
        ParagraphStyle("nc", alignment=TA_CENTER, leading=18,
                       textColor=WHITE))]],
        colWidths=[CONTENT_W - 1.4 * inch])
    chip.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    items.append(chip)
    items.append(Spacer(1, 18))

    # Important disclaimer banner
    disc = Table([[Paragraph(
        ('<font color="#D95B72" size="10"><b>Important.</b></font>  '
         'This is a parent-prepared informational document. It is '
         '<b>not a draft IEP, not legal advice, and not a diagnostic '
         'evaluation.</b> Your school district’s IEP team produces '
         'the official IEP. Read the next two pages for full disclosures.'),
        ParagraphStyle("dc", fontName=SANS, fontSize=10, leading=15,
                       textColor=TEXT, alignment=TA_LEFT))]],
        colWidths=[CONTENT_W - 0.6 * inch])
    disc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ROSE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ROSE),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
    ]))
    items.append(disc)
    items.append(PageBreak())
    return items


# ── Disclosures (reuses comprehensive's disclaimers + IEP-specific) ──
def iep_disclosures():
    """Standard disclosures + IEP-specific framing."""
    items = []
    items.append(section_label("IMPORTANT DISCLOSURES", color=PRIMARY))
    items.append(Paragraph("Please read before using this Companion",
                           S["h1"]))
    items.append(Paragraph(
        ("By using this document you acknowledge that you have read, "
         "understood, and agree to the disclosures below. The full Privacy "
         "Policy, Terms of Service, and Disclaimer are available at "
         "piecesofperception.com."),
        S["lead"]))
    items.append(Spacer(1, 8))

    disclosures = [
        ("Not a Draft IEP",
         "This is a <b>parent-prepared companion document</b>. It is not "
         "an Individualized Education Program (IEP), does not create one, "
         "and does not substitute for the IEP team process required under "
         "IDEA (34 CFR §§ 300.320–300.324). Your school "
         "district’s IEP team—which by law includes the parent, "
         "general and special education teachers, a district representative, "
         "and an evaluation interpreter—produces the official IEP."),
        ("Not Legal Advice",
         "Nothing in this document constitutes legal advice or legal "
         "representation. If you anticipate disputes about eligibility, "
         "placement, services, or due process, consult a qualified special "
         "education attorney or advocate."),
        ("Not Medical or Diagnostic Advice",
         "Reports and content generated by Pieces of Perception are "
         "general informational resources only. They do not constitute "
         "medical advice, clinical guidance, psychological assessment, or "
         "any form of professional healthcare recommendation. Always "
         "consult licensed clinicians before implementing strategies in "
         "this report."),
        ("Not a Clinical Evaluation",
         "Pieces of Perception is not a diagnostic tool or standardized "
         "evaluation. This document is generated from a family-completed "
         "questionnaire and reflects parent observation, not a comprehensive "
         "psychoeducational or neuropsychological evaluation. Schools may "
         "require formal evaluations — conducted by qualified school "
         "personnel — to determine eligibility and to inform IEP goals."),
        ("AI-Generated Content — Limitations",
         "Reports are generated using artificial intelligence language "
         "models and may contain errors, inaccuracies, or omissions. "
         "Outputs are based solely on the information submitted through "
         "the questionnaire. Review all content critically and in "
         "consultation with your child's qualified care team."),
        ("IEP Goals & Recommendations — Family Input Only",
         "Any goal-area suggestions, accommodation suggestions, or "
         "questions in this report are <b>informational starting points "
         "for parent advocacy and family preparation.</b> They are not "
         "draft IEP goals, do not constitute special-education consulting "
         "services, and carry no legal or procedural standing under IDEA. "
         "The IEP team is responsible for developing measurable annual "
         "goals, present levels of performance, and specially designed "
         "instruction."),
        ("State Framework",
         "This document references the Rhode Island Department of "
         "Education IEP framework (see ride.ri.gov/students-families/"
         "special-education/iep-individual-education-program). Most "
         "sections are also broadly applicable to other state IEP "
         "processes and to federal IDEA requirements. Confirm specifics "
         "with your district."),
        ("Children's Privacy & COPPA",
         "Pieces of Perception is designed for use by parents and "
         "caregivers on behalf of their children — not directly by "
         "children. By completing the questionnaire, you represent that "
         "you are the parent or legal guardian. We do not knowingly "
         "collect personal information directly from children under 13 "
         "without verifiable parental consent, in accordance with COPPA."),
    ]

    for title, body in disclosures:
        items.append(Paragraph(f'<b>{title}</b>',
                               ParagraphStyle("dt", fontName=SANS_BOLD,
                                              fontSize=11, leading=15,
                                              textColor=DEEP,
                                              spaceAfter=4)))
        items.append(Paragraph(body,
                               ParagraphStyle("db", fontName=SANS,
                                              fontSize=10, leading=14.5,
                                              textColor=TEXT,
                                              spaceAfter=12)))
    items.append(Spacer(1, 6))
    items.append(Paragraph(
        "<i>Pieces of Perception LLC · hello@piecesofperception.com</i>",
        ParagraphStyle("dfooter", fontName=SANS_OBLIQUE, fontSize=9,
                       leading=13, textColor=TEXT_LIGHT,
                       alignment=TA_CENTER)))
    items.append(PageBreak())
    return items


# ── How to Use This Companion ────────────────────────────────────────
def how_to_use():
    items = []
    items.append(section_label("HOW TO USE THIS COMPANION",
                               color=PRIMARY))
    items.append(Paragraph(
        "Three ways to put this to work", S["h1"]))
    items.append(Paragraph(
        ("This is your voice as a parent, organized into the structure "
         "the school will use. Use it however supports your meeting best."),
        S["lead"]))
    items.append(Spacer(1, 10))

    ways = [
        ("Before the meeting",
         "Share a copy with the IEP team 1–2 weeks in advance. "
         "Email the chairperson and ask them to circulate it to the "
         "team. This gives teachers and related service providers time "
         "to read it, weave your observations into their planning, and "
         "come to the meeting already aligned with your priorities.",
         PRIMARY),
        ("During the meeting",
         "Bring a printed copy as your reference. Section numbers in "
         "this Companion map to standard IEP sections (Present Levels, "
         "Goals, Accommodations, Services). When the team gets to a "
         "section, you can flip to the matching page and bring your data "
         "to the conversation — calmly, confidently, with backup.",
         SAGE),
        ("After the meeting",
         "Use the Questions section (Section 11) to track what was "
         "answered, what was deferred, and what needs follow-up. This "
         "becomes your record of what the team committed to and what "
         "you still need to advocate for.",
         WARM),
    ]
    items.append(card_grid(
        [(f'<font color="{c.hexval()}">●</font>', t, b)
         for t, b, c in ways],
        cols=1, accent_color=PRIMARY, bg_color=WHITE,
        border_color=BORDER_SOFT))
    items.append(Spacer(1, 14))

    items.append(callout(
        "A note about parent voice in an IEP",
        ("Under IDEA §300.324, the IEP team is required to consider "
         "the concerns of the parents for enhancing the education of their "
         "child. That is a federal mandate, not a suggestion. The data in "
         "this Companion is parent-observed, specific, and behaviorally "
         "framed — exactly the form of input the team is required to "
         "consider."),
        accent=PRIMARY, bg=PRIMARY_BG))
    items.append(PageBreak())
    return items


# ── Section 1 — Student Information & IEP Team ──────────────────────
def section_student_info():
    items = []
    items.append(section_label("SECTION 01 · STUDENT INFORMATION",
                               color=PRIMARY))
    items.append(Paragraph(
        f"Who {CHILD['first_name']} is, on paper", S["h1"]))
    items.append(Paragraph(
        ("The facts the IEP team will reference — plus space to "
         "capture the team members who will be at the table."),
        S["lead"]))
    items.append(Spacer(1, 8))

    # Student facts table
    facts = [
        ("Full name (first + last initial)",
         f"{CHILD['first_name']} {CHILD['last_initial']}"),
        ("Age", str(CHILD.get("age", ""))),
        ("Pronouns", CHILD.get("pronouns", "")),
        ("Current grade / placement", CHILD.get("grade", "")),
        ("Primary diagnoses (parent-reported)",
         "; ".join(CHILD.get("diagnoses", []))),
        ("Report prepared",
         CHILD.get("report_date", "")),
    ]
    rows = []
    for label, val in facts:
        rows.append([
            Paragraph(f'<b>{label}</b>',
                      ParagraphStyle("ll", fontName=SANS_BOLD, fontSize=9,
                                     leading=12, textColor=PRIMARY)),
            Paragraph(val or "—",
                      ParagraphStyle("vv", fontName=SANS, fontSize=10,
                                     leading=13.5, textColor=DEEP)),
        ])
    tbl = Table(rows, colWidths=[2.0 * inch, CONTENT_W - 2.0 * inch])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER_SOFT),
        ("BACKGROUND", (0, 0), (0, -1), BG),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 12))

    # IEP team roster (blank slots for parent to fill in)
    items.append(Paragraph(
        '<font color="#8E7FC4" size="11"><b>The IEP team</b></font>  '
        '<font size="9" color="#6B6B80">(per IDEA §300.321)</font>',
        ParagraphStyle("th", leading=15, spaceAfter=6)))
    items.append(Paragraph(
        ("The federal IEP team minimally includes the people listed below. "
         "Fill in names ahead of the meeting so you walk in already "
         "knowing who you're talking with."),
        ParagraphStyle("h", fontName=SANS, fontSize=10, leading=14,
                       textColor=TEXT, spaceAfter=10)))

    team_roles = [
        ("Parent / Legal Guardian", PARENT.get("name", "________________")),
        ("Regular Education Teacher", "________________"),
        ("Special Education Teacher / Case Manager", "________________"),
        ("School District Representative", "________________"),
        ("Evaluation Interpreter (per IDEA)", "________________"),
        (f"Student ({CHILD['first_name']}) — invited at age 14+",
         "yes / no / partial — ________________"),
        ("Related Service Providers (OT/SLP/PT/BCBA/Counselor)",
         "________________"),
        ("Other invited team members", "________________"),
    ]
    trows = []
    for role, name in team_roles:
        trows.append([
            Paragraph(f'<b>{role}</b>',
                      ParagraphStyle("trl", fontName=SANS_BOLD, fontSize=9,
                                     leading=12, textColor=DEEP)),
            Paragraph(name,
                      ParagraphStyle("trv", fontName=SANS, fontSize=9.5,
                                     leading=12.5, textColor=TEXT_LIGHT)),
        ])
    ttbl = Table(trows, colWidths=[3.1 * inch, CONTENT_W - 3.1 * inch])
    ttbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER_SOFT),
    ]))
    items.append(ttbl)
    items.append(PageBreak())
    return items


# ── Section 2 — Parent Concerns & Priorities ────────────────────────
def section_parent_concerns():
    items = []
    items.append(section_label("SECTION 02 · PARENT CONCERNS & PRIORITIES",
                               color=PRIMARY))
    items.append(Paragraph(
        f"What you, as {CHILD['first_name']}’s parent, want this "
        f"IEP to address", S["h1"]))
    items.append(Paragraph(
        ("IDEA §300.324 requires the IEP team to consider the "
         "<b>concerns of the parents for enhancing the education of "
         "their child.</b> The text below is yours — already written, "
         "ready to read aloud or attach to the meeting record."),
        S["lead"]))
    items.append(Spacer(1, 10))

    # Pull biggest challenge
    biggest = ""
    for q, a in SHARED_QA:
        if "biggest challenge" in q.lower():
            biggest = a
            break

    items.append(Paragraph(
        '<font color="#8E7FC4" size="11"><b>Biggest concern right now</b></font>',
        ParagraphStyle("c1", leading=15, spaceAfter=6)))
    items.append(callout("", biggest or "(no answer recorded)",
                         accent=PRIMARY, bg=PRIMARY_BG))
    items.append(Spacer(1, 14))

    # Pull top 3 goals from comprehensive Q&A
    goals_text = ""
    for q, a in COMPREHENSIVE_QA:
        if "top 3" in q.lower() and "goal" in q.lower():
            goals_text = a
            break

    items.append(Paragraph(
        '<font color="#8E7FC4" size="11"><b>Top priorities for the next '
        '12 months</b></font>  <font size="9" color="#6B6B80">'
        '(parent’s view — not pre-written goals)</font>',
        ParagraphStyle("c2", leading=15, spaceAfter=6)))
    items.append(Paragraph(
        ("These are the AREAS the parent wants the team to focus on. The "
         "IEP team will translate these into measurable annual goals."),
        ParagraphStyle("h", fontName=SANS, fontSize=10, leading=14,
                       textColor=TEXT, spaceAfter=10)))
    items.append(callout("", goals_text or "(no answer recorded)",
                         accent=SAGE, bg=SAGE_BG))
    items.append(Spacer(1, 14))

    # What an ideal outcome looks like (anchor truths help frame this)
    items.append(Paragraph(
        '<font color="#8E7FC4" size="11"><b>The lens to bring to every '
        f'conversation about {CHILD["first_name"]}</b></font>',
        ParagraphStyle("c3", leading=15, spaceAfter=10)))
    if ANCHOR_TRUTHS:
        items.append(card_grid(
            [(f'<font color="{PRIMARY.hexval()}">●</font>',
              t[0], t[1])
             for t in ANCHOR_TRUTHS[:3]],
            cols=3, accent_color=PRIMARY, bg_color=WHITE,
            border_color=BORDER_SOFT))
    items.append(PageBreak())
    return items


# ── Section 3 — Present Levels of Functional Performance ────────────
def section_present_levels():
    items = []
    items.append(section_label(
        "SECTION 03 · PRESENT LEVELS OF FUNCTIONAL PERFORMANCE",
        color=PRIMARY))
    items.append(Paragraph("Functional baselines, from the home view",
                           S["h1"]))
    items.append(Paragraph(
        ("Under IDEA §300.320, the IEP must describe the student’s "
         "<b>academic achievement AND functional performance.</b> Functional "
         "performance is everyday life: communication, social-emotional, "
         "sensory, behavior, daily living. School evaluations will provide "
         "academic baselines (reading, writing, math). What follows is the "
         "<b>functional</b> data the parent observes — equally required "
         "by IDEA, and often the most under-documented section of the IEP."),
        S["lead"]))
    items.append(Spacer(1, 12))

    # 3a — Communication & Language
    items.append(Paragraph(
        '<font color="#8E7FC4" size="12"><b>3.1 Communication &amp; Language</b></font>',
        ParagraphStyle("p3a", leading=16, spaceAfter=8)))
    comm_style = ""
    for q, a in SHARED_QA:
        if "communication" in q.lower():
            comm_style = a
            break
    if comm_style:
        items.append(Paragraph(
            f"<b>Primary communication style (parent-reported):</b> {comm_style}",
            ParagraphStyle("p3aa", fontName=SANS, fontSize=10.5, leading=15,
                           textColor=TEXT, spaceAfter=10)))
    if COMM_RULES:
        items.append(Paragraph(
            f"<b>What works for {CHILD['first_name']} in communication:</b>",
            ParagraphStyle("p3ab", fontName=SANS_BOLD, fontSize=10.5,
                           leading=14, textColor=DEEP, spaceAfter=6)))
        for r in COMM_RULES[:6]:
            rule = r[0] if isinstance(r, tuple) and len(r) > 0 else (r if isinstance(r, str) else "")
            body = r[1] if isinstance(r, tuple) and len(r) > 1 else ""
            items.append(Paragraph(
                f'<font color="{PRIMARY.hexval()}"><b>{rule}</b></font>',
                ParagraphStyle("p3ac1", fontName=SANS_BOLD, fontSize=10.5,
                               leading=14, textColor=DEEP,
                               leftIndent=14, spaceAfter=2)))
            if body:
                items.append(Paragraph(
                    body,
                    ParagraphStyle("p3ac2", fontName=SANS, fontSize=10,
                                   leading=14, textColor=TEXT,
                                   leftIndent=28, spaceAfter=8)))
    items.append(Spacer(1, 14))

    # 3b — Sensory Profile
    items.append(Paragraph(
        '<font color="#8E7FC4" size="12"><b>3.2 Sensory Profile</b></font>',
        ParagraphStyle("p3b", leading=16, spaceAfter=8)))
    items.append(Paragraph(
        ("Sensory regulation directly affects access to instruction. "
         "Without sensory accommodations in place, the student is "
         "regulating instead of learning."),
        ParagraphStyle("p3bi", fontName=SANS_OBLIQUE, fontSize=10,
                       leading=14, textColor=TEXT_LIGHT, spaceAfter=10)))
    if SENSORY_MAP:
        # Use Paragraph objects so cells word-wrap correctly inside narrow columns.
        # 3-column layout: system / parent observation / accommodation discussed at IEP.
        header_style = ParagraphStyle("sh", fontName=SANS_BOLD, fontSize=8.5,
                                       leading=11, textColor=WHITE,
                                       alignment=TA_LEFT)
        sys_style = ParagraphStyle("ss", fontName=SANS_BOLD, fontSize=9,
                                    leading=12, textColor=PRIMARY)
        cell_style = ParagraphStyle("sc", fontName=SANS, fontSize=9,
                                     leading=12, textColor=TEXT)
        sens_rows = [[
            Paragraph("SYSTEM", header_style),
            Paragraph("PARENT-OBSERVED PATTERN", header_style),
            Paragraph("ACCOMMODATION TO DISCUSS", header_style),
        ]]
        for entry in SENSORY_MAP[:7]:
            system = entry[0] if len(entry) > 0 else ""
            obs = entry[3] if len(entry) > 3 else ""
            acc = entry[4] if len(entry) > 4 else ""
            sens_rows.append([
                Paragraph(system, sys_style),
                Paragraph(obs, cell_style),
                Paragraph(acc, cell_style),
            ])
        col1 = 1.4 * inch
        col3 = 2.3 * inch
        col2 = CONTENT_W - col1 - col3
        stbl = Table(sens_rows, colWidths=[col1, col2, col3], repeatRows=1)
        stbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DEEP),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, BG]),
        ]))
        items.append(stbl)
    items.append(PageBreak())

    # 3c — Self-Regulation & Coping
    items.append(Paragraph(
        '<font color="#8E7FC4" size="12"><b>3.3 Self-Regulation &amp; Coping</b></font>',
        ParagraphStyle("p3c", leading=16, spaceAfter=8)))
    if TOOLKIT_TIERS:
        items.append(Paragraph(
            f"<b>What helps {CHILD['first_name']} stay regulated:</b>",
            ParagraphStyle("p3ci", fontName=SANS_BOLD, fontSize=10.5,
                           leading=14, textColor=DEEP, spaceAfter=6)))
        for tier in TOOLKIT_TIERS[:4]:
            name = tier[1] if len(tier) > 1 else ""
            description = tier[2] if len(tier) > 2 else ""
            actions = tier[3] if len(tier) > 3 else ""
            if name:
                items.append(Paragraph(
                    f'<font color="{PRIMARY.hexval()}"><b>Tier {tier[0]} — {name}</b></font>',
                    ParagraphStyle("p3cn", fontName=SANS_BOLD, fontSize=10.5,
                                   leading=14, textColor=PRIMARY,
                                   spaceAfter=4, spaceBefore=8)))
            if description:
                items.append(Paragraph(
                    description,
                    ParagraphStyle("p3cd", fontName=SANS_OBLIQUE, fontSize=10,
                                   leading=14, textColor=TEXT_LIGHT,
                                   leftIndent=14, spaceAfter=3)))
            if actions:
                items.append(Paragraph(
                    f'▸  {actions}',
                    ParagraphStyle("p3cb", fontName=SANS, fontSize=10,
                                   leading=14.5, textColor=TEXT,
                                   leftIndent=14, spaceAfter=4)))
    # Force the Behavior + Crisis Steps subsection onto a fresh page block
    # so the 6 crisis steps don't orphan across pages.
    from reportlab.platypus import CondPageBreak
    items.append(CondPageBreak(5.5 * inch))

    # 3d — Behavior & Stressors
    items.append(Paragraph(
        '<font color="#8E7FC4" size="12"><b>3.4 Behavior, Stressors &amp; '
        'Recovery Patterns</b></font>',
        ParagraphStyle("p3d", leading=16, spaceAfter=8)))
    melt_freq = ""
    for q, a in SHARED_QA:
        if "meltdown" in q.lower() or "shutdown" in q.lower():
            melt_freq = a
            break
    if melt_freq:
        items.append(Paragraph(
            f"<b>Frequency of dysregulation events (parent-reported):</b> "
            f"{melt_freq}",
            ParagraphStyle("p3di", fontName=SANS, fontSize=10.5, leading=15,
                           textColor=TEXT, spaceAfter=10)))
    if CRISIS_STEPS:
        items.append(Paragraph(
            f"<b>What works during dysregulation, in order:</b>",
            ParagraphStyle("p3dh", fontName=SANS_BOLD, fontSize=10.5,
                           leading=14, textColor=DEEP, spaceAfter=6)))
        for i, step in enumerate(CRISIS_STEPS[:6], start=1):
            label = step[0] if len(step) > 0 else ""
            body = step[2] if len(step) > 2 else ""
            block = [
                Paragraph(
                    f'<font color="{PRIMARY.hexval()}"><b>{i}. {label}</b></font>',
                    ParagraphStyle("p3ds1", fontName=SANS_BOLD, fontSize=10,
                                   leading=14, textColor=DEEP,
                                   leftIndent=14, spaceAfter=2)),
                Paragraph(
                    body,
                    ParagraphStyle("p3ds2", fontName=SANS, fontSize=10,
                                   leading=14.5, textColor=TEXT,
                                   leftIndent=28, spaceAfter=6)),
            ]
            items.append(KeepTogether(block))
    items.append(PageBreak())
    return items


# ── Section 4 — Strengths Inventory ─────────────────────────────────
def section_strengths():
    items = []
    items.append(section_label("SECTION 04 · STRENGTHS INVENTORY",
                               color=PRIMARY))
    items.append(Paragraph(
        f"What {CHILD['first_name']} does beautifully", S["h1"]))
    items.append(Paragraph(
        ("Strengths-based IEPs are required practice under IDEA "
         "(§300.324(a)(1)(i)). The team must consider strengths of "
         "the student. These are the strengths to build the IEP on — "
         "not the consolation prize after the deficit list."),
        S["lead"]))
    items.append(Spacer(1, 10))

    if STRENGTHS_CARDS:
        cards_data = []
        for c in STRENGTHS_CARDS[:6]:
            title = c[1] if len(c) > 1 else ""
            body = c[2] if len(c) > 2 else ""
            cards_data.append(
                (f'<font color="{PRIMARY.hexval()}">★</font>',
                 title, body))
        items.append(card_grid(
            cards_data, cols=2, accent_color=PRIMARY,
            bg_color=WHITE, border_color=BORDER_SOFT))
    items.append(Spacer(1, 12))

    # Special interests + motivators
    interests = ""
    for q, a in COMPREHENSIVE_QA:
        if "special interest" in q.lower():
            interests = a
            break
    if interests:
        items.append(callout(
            f"{CHILD['first_name']}’s special interests "
            f"(use as engagement levers in instruction)",
            interests, accent=SAGE, bg=SAGE_BG))
    items.append(PageBreak())
    return items


# ── Section 5 — Areas to Discuss for Annual Goal Development ────────
def section_goal_areas():
    items = []
    items.append(section_label(
        "SECTION 05 · AREAS FOR THE TEAM TO DISCUSS",
        color=PRIMARY))
    items.append(Paragraph(
        "Goal areas the parent wants the IEP team to address", S["h1"]))
    items.append(Paragraph(
        ("These are not pre-written SMART goals. They are the AREAS the "
         "parent has identified, with baseline observations and growth "
         "directions, ready for the team to translate into measurable "
         "annual goals using whatever measurement framework the district "
         "uses."),
        S["lead"]))
    items.append(Spacer(1, 10))

    # Pull the top-3 goals text and try to split into 3 distinct areas
    goals_text = ""
    for q, a in COMPREHENSIVE_QA:
        if "top 3" in q.lower() and "goal" in q.lower():
            goals_text = a
            break

    # Naive parse — split on numbered list markers
    import re
    parts = re.split(r"\n\s*[123]\.\s+", "\n" + goals_text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        parts = [goals_text]

    colors_seq = [PRIMARY, SAGE, WARM]
    for i, area in enumerate(parts[:3]):
        c = colors_seq[i % 3]
        # First sentence becomes the area header; rest becomes body
        head, _, rest = area.partition(".")
        head = head.strip().rstrip(":") + "."
        rest = rest.strip()

        items.append(Paragraph(
            f'<font color="{c.hexval()}" size="11"><b>'
            f'Goal Area {i+1} — Parent’s framing</b></font>',
            ParagraphStyle("ga", leading=14, spaceAfter=4)))
        items.append(Paragraph(
            head,
            ParagraphStyle("gat", fontName=SERIF_BOLD, fontSize=14,
                           leading=18, textColor=DEEP, spaceAfter=6)))
        if rest:
            items.append(Paragraph(
                rest,
                ParagraphStyle("gab", fontName=SANS, fontSize=10.5,
                               leading=15, textColor=TEXT, spaceAfter=8)))

        # Suggested questions for the team
        items.append(Paragraph(
            '<font color="#6B6B80" size="9.5"><b>For team discussion:</b></font>',
            ParagraphStyle("gaq", leading=13, spaceAfter=4)))
        questions = [
            ("What baseline data would the school like to gather to "
             "measure progress in this area?"),
            ("Which staff member(s) will own the data collection?"),
            ("How will progress be communicated to the parent, and how "
             "often?"),
        ]
        for q in questions:
            items.append(Paragraph(
                f'▸  {q}',
                ParagraphStyle("gaqi", fontName=SANS, fontSize=9.5,
                               leading=13.5, textColor=TEXT_LIGHT,
                               leftIndent=14, spaceAfter=2)))
        items.append(Spacer(1, 14))

    items.append(PageBreak())
    return items


# ── Section 6 — Accommodations to Discuss ────────────────────────────
def section_accommodations():
    items = []
    items.append(section_label(
        "SECTION 06 · ACCOMMODATIONS TO DISCUSS",
        color=PRIMARY))
    items.append(Paragraph(
        f"What’s already working at home, for team consideration",
        S["h1"]))
    items.append(Paragraph(
        ("Under IDEA §300.320, the IEP must describe accommodations "
         "needed for the student to participate in instruction and "
         "assessment. The accommodations below have been observed by the "
         "parent to support functioning at home. The IEP team will "
         "consider, adapt, and add school-context accommodations."),
        S["lead"]))
    items.append(Spacer(1, 10))

    if HOME_ACCOMMODATIONS_RELIED_ON:
        for acc in HOME_ACCOMMODATIONS_RELIED_ON[:12]:
            t = acc if isinstance(acc, str) else (
                acc.get("text") or acc.get("title") or str(acc))
            items.append(Paragraph(
                f'<font color="{PRIMARY.hexval()}">▸</font>  {t}',
                ParagraphStyle("acc", fontName=SANS, fontSize=10.5,
                               leading=15, textColor=TEXT,
                               leftIndent=14, spaceAfter=5)))
    else:
        items.append(Paragraph(
            "(No specific home accommodations were captured in the "
            "questionnaire. Use the sensory profile in Section 3 and the "
            "regulation toolkit to inform the conversation.)",
            ParagraphStyle("none", fontName=SANS_OBLIQUE, fontSize=10,
                           leading=14, textColor=TEXT_LIGHT)))
    items.append(Spacer(1, 16))

    items.append(callout(
        "Accommodation vs. Modification — a quick distinction",
        ("<b>Accommodations</b> change HOW the student learns and "
         "demonstrates learning (extended time, sensory breaks, preferential "
         "seating). They do not change WHAT is being learned. "
         "<b>Modifications</b> change WHAT is being learned (different "
         "grade-level content, modified assessments). Most students need "
         "accommodations; modifications are considered only when the "
         "team determines the general curriculum is not accessible even "
         "with accommodations."),
        accent=PRIMARY, bg=PRIMARY_BG))
    items.append(PageBreak())
    return items


# ── Section 7 — Specially Designed Instruction (SDI) Considerations ─
def section_sdi():
    items = []
    items.append(section_label(
        "SECTION 07 · SPECIALLY DESIGNED INSTRUCTION",
        color=PRIMARY))
    items.append(Paragraph(
        "What SDI is, and what to ask about", S["h1"]))
    items.append(Paragraph(
        ("Specially Designed Instruction (SDI) is the heart of special "
         "education — the explicit, individualized teaching practices "
         "that address the student’s unique needs. Per IDEA "
         "§300.39, SDI is content, methodology, OR delivery of "
         "instruction that’s been adapted for the child."),
        S["lead"]))
    items.append(Spacer(1, 10))

    items.append(Paragraph(
        '<font color="#8E7FC4" size="11"><b>What the parent has observed '
        f'about how {CHILD["first_name"]} learns best</b></font>',
        ParagraphStyle("sdi1", leading=15, spaceAfter=6)))

    # Pull communication rules — they double as instructional rules
    if COMM_RULES:
        for r in COMM_RULES[:5]:
            rule = r[0] if isinstance(r, tuple) and len(r) > 0 else (r if isinstance(r, str) else "")
            items.append(Paragraph(
                f'<font color="{PRIMARY.hexval()}">▸</font>  {rule}',
                ParagraphStyle("sdi2", fontName=SANS, fontSize=10.5,
                               leading=14.5, textColor=TEXT,
                               leftIndent=14, spaceAfter=4)))
    items.append(Spacer(1, 14))

    items.append(Paragraph(
        '<font color="#8E7FC4" size="11"><b>Questions to ask about '
        'SDI in the IEP meeting</b></font>',
        ParagraphStyle("sdi3", leading=15, spaceAfter=6)))
    sdi_q = [
        ("What specifically designed instructional methods will be used "
         "to address {name}’s identified needs?"),
        ("Who is delivering the SDI — the special education teacher "
         "directly, a paraprofessional under supervision, or both? In "
         "what setting?"),
        ("What is the dosage — frequency, duration, and group size "
         "— for each SDI area?"),
        ("How will the IEP team know the SDI is working? What are the "
         "decision rules for changing approach if data shows lack of "
         "progress?"),
    ]
    for q in sdi_q:
        items.append(Paragraph(
            f'▸  {q.format(name=CHILD["first_name"])}',
            ParagraphStyle("sdiq", fontName=SANS, fontSize=10,
                           leading=14, textColor=TEXT,
                           leftIndent=14, spaceAfter=4)))
    items.append(PageBreak())
    return items


# ── Section 8 — Triggers & De-escalation (FBA prep) ─────────────────
def section_triggers():
    items = []
    items.append(section_label(
        "SECTION 08 · TRIGGERS, DE-ESCALATION & FBA NOTES",
        color=PRIMARY))
    items.append(Paragraph(
        "What sets dysregulation off — and what brings calm back",
        S["h1"]))
    items.append(Paragraph(
        ("If the school is considering a Functional Behavioral Assessment "
         "(FBA) or a Behavior Intervention Plan (BIP), this section is the "
         "parent’s observational input. It is not a substitute for an "
         "FBA — it is the data the team should consider alongside "
         "their own observations."),
        S["lead"]))
    items.append(Spacer(1, 10))

    # Trigger swaps
    if TRIGGER_SWAPS:
        items.append(Paragraph(
            '<font color="#8E7FC4" size="11"><b>Words / phrases to retire '
            '— with replacements that work</b></font>',
            ParagraphStyle("tr1", leading=15, spaceAfter=8)))
        sw_rows = [["RETIRE", "REPLACE WITH"]]
        for sw in TRIGGER_SWAPS[:8]:
            retire = sw[0] if len(sw) > 0 else ""
            replace = sw[1] if len(sw) > 1 else ""
            sw_rows.append([retire, replace])
        swt = Table(sw_rows, colWidths=[2.4 * inch, CONTENT_W - 2.4 * inch])
        swt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DEEP),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), SANS_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTNAME", (0, 1), (0, -1), SANS_BOLD),
            ("TEXTCOLOR", (0, 1), (0, -1), ROSE),
            ("FONTNAME", (1, 1), (1, -1), SANS),
            ("TEXTCOLOR", (1, 1), (1, -1), DEEP),
            ("FONTSIZE", (0, 1), (-1, -1), 9.5),
            ("LEADING", (0, 1), (-1, -1), 13),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, BG]),
        ]))
        items.append(swt)
    items.append(Spacer(1, 14))

    items.append(callout(
        "A question worth asking the IEP team",
        ("“Given the dysregulation patterns described in this "
         "section, would the team consider a Functional Behavioral "
         "Assessment (FBA), or a Behavior Intervention Plan (BIP), to "
         "ensure consistent response across school staff?”"),
        accent=PRIMARY, bg=PRIMARY_BG))
    items.append(PageBreak())
    return items


# ── Section 9 — Existing Team & Providers ───────────────────────────
def section_existing_team():
    items = []
    items.append(section_label(
        "SECTION 09 · EXISTING TEAM & OUTSIDE PROVIDERS",
        color=PRIMARY))
    items.append(Paragraph("The team already in place", S["h1"]))
    items.append(Paragraph(
        ("Coordination between school and outside providers makes the "
         "IEP work. This is the team already supporting "
         f"{CHILD['first_name']}."),
        S["lead"]))
    items.append(Spacer(1, 12))

    if EXISTING_TEAM:
        for member in EXISTING_TEAM[:10]:
            role = member[0] if len(member) > 0 else ""
            notes = member[2] if len(member) > 2 else ""
            items.append(Paragraph(
                f'<b>{role}</b>',
                ParagraphStyle("et", fontName=SANS_BOLD, fontSize=11,
                               leading=15, textColor=DEEP,
                               spaceAfter=2)))
            if notes:
                items.append(Paragraph(
                    notes,
                    ParagraphStyle("etn", fontName=SANS, fontSize=10,
                                   leading=14, textColor=TEXT_LIGHT,
                                   leftIndent=14, spaceAfter=8)))
            else:
                items.append(Spacer(1, 6))
    else:
        items.append(Paragraph(
            "(No outside providers were specified in the questionnaire.)",
            ParagraphStyle("none", fontName=SANS_OBLIQUE, fontSize=10,
                           leading=14, textColor=TEXT_LIGHT)))
    items.append(Spacer(1, 14))

    items.append(callout(
        "Releases of information",
        ("Ask the IEP team chairperson to send Release of Information "
         "forms so the school can communicate directly with the outside "
         "providers listed above. This is opt-in for the parent and "
         "dramatically improves continuity of care."),
        accent=SAGE, bg=SAGE_BG))

    # Footnote: explain why Section 10 may be absent
    if not _is_secondary():
        items.append(Spacer(1, 14))
        items.append(Paragraph(
            ("<i>Section 10 (Transition Planning) appears in the version "
             "of this Companion for students age 14 and older. RI requires "
             "transition planning to begin at age 14; the federal IDEA "
             "floor is age 16.</i>"),
            ParagraphStyle("s10n", fontName=SANS_OBLIQUE, fontSize=9.5,
                           leading=13.5, textColor=TEXT_LIGHT,
                           alignment=TA_CENTER)))
    items.append(PageBreak())
    return items


# ── Section 10 — Transition Planning (age 14+ only) ─────────────────
def section_transition():
    """IDEA requires transition planning to begin at age 14 in RI
       (16 federally; many states including RI use 14)."""
    items = []
    items.append(section_label(
        "SECTION 10 · TRANSITION PLANNING",
        color=PRIMARY))
    items.append(Paragraph(
        "Post-school goals and transition services", S["h1"]))
    items.append(Paragraph(
        ("Beginning at age 14 (per RI) and at minimum by age 16 (per "
         "IDEA §300.320), the IEP must include measurable "
         "post-school goals in three areas: <b>education / training</b>, "
         "<b>employment</b>, and — where appropriate — "
         "<b>independent living skills</b>. Transition services "
         "(§300.43) are the coordinated activities that get the "
         "student there."),
        S["lead"]))
    items.append(Spacer(1, 12))

    fields = [
        ("Post-school education / training goal",
         "What does the parent see as a realistic and aspirational "
         "next step after high school? (College? Certificate program? "
         "Supported post-secondary? Vocational training?)"),
        ("Post-school employment goal",
         "What kind of work or contribution does the student/family "
         "envision? What strengths and interests would support that?"),
        ("Independent living goal (if appropriate)",
         "What level of independence is the target? What daily living "
         "skills would the student need to build?"),
        ("Transition services to consider",
         "Instructional supports, community experiences, employment "
         "training, daily-living skill instruction, related agency "
         "linkages (e.g., RI BHDDH, ORS-VR, RIPIN). The IEP team must "
         "coordinate with any agency likely to provide transition services."),
        ("Student participation",
         "The student must be invited to the IEP meeting beginning at "
         "age 14. If they are not yet ready to attend the full meeting, "
         "the team can plan a partial visit with appropriate supports."),
    ]
    for label, prompt in fields:
        items.append(Paragraph(
            f'<font color="{PRIMARY.hexval()}" size="11"><b>{label}</b></font>',
            ParagraphStyle("trh", leading=15, spaceAfter=4)))
        items.append(Paragraph(
            prompt,
            ParagraphStyle("trp", fontName=SANS_OBLIQUE, fontSize=10,
                           leading=14, textColor=TEXT_LIGHT,
                           spaceAfter=10)))
        items.append(Paragraph(
            "Parent’s notes: ________________________________"
            "________________________________________",
            ParagraphStyle("trn", fontName=SANS, fontSize=10, leading=20,
                           textColor=TEXT, spaceAfter=14)))
    items.append(PageBreak())
    return items


# ── Section 11 — Questions for the IEP Meeting ──────────────────────
def section_questions():
    items = []
    items.append(section_label(
        "SECTION 11 · QUESTIONS FOR THE IEP MEETING",
        color=PRIMARY))
    items.append(Paragraph(
        "The list to bring with you", S["h1"]))
    items.append(Paragraph(
        ("Use this checklist during the meeting. Mark a question "
         "&#10003; when answered, &#8594; when deferred for follow-up, or "
         "leave blank to come back to."),
        S["lead"]))
    items.append(Spacer(1, 10))

    questions = [
        "What evaluations has the school completed, and when were they last updated?",
        "How will the IEP team translate the parent priorities (Section 2) into measurable annual goals?",
        "Who on the IEP team will be the parent’s primary point of contact between meetings?",
        "How often will the school report on progress toward goals, and through what format?",
        "What is the school’s plan for the sensory accommodations described in Section 3?",
        "Has an FBA been considered, given the dysregulation patterns described in Section 8?",
        "What is the school’s plan for coordinating with the outside providers in Section 9?",
        "How will the IEP team include the student’s strengths (Section 4) in the IEP language?",
        "What is the placement decision, and what was considered before reaching it?",
        "What is the plan if data shows insufficient progress on a goal at the 6–week mark?",
        "Will Extended School Year (ESY) services be considered? On what basis?",
        "When is the next scheduled IEP review? When can the parent request an interim review?",
    ]
    if _is_secondary():
        questions += [
            "How is the student being prepared for and supported through "
            "the transition planning process described in Section 10?",
            "Which agencies will be invited to participate in transition "
            "planning meetings (e.g., RI ORS-VR, BHDDH)?",
        ]

    for i, q in enumerate(questions, start=1):
        block = [
            Paragraph(
                f'<font color="{PRIMARY.hexval()}"><b>{i:02d}.</b></font>  {q}',
                ParagraphStyle("qq", fontName=SANS, fontSize=10.5,
                               leading=15, textColor=TEXT,
                               leftIndent=18, spaceAfter=4)),
            Paragraph(
                "<font color='#6B6B80'>Answer / next step: ___________________________"
                "________________________________________</font>",
                ParagraphStyle("qa", fontName=SANS, fontSize=9, leading=15,
                               textColor=TEXT_LIGHT, leftIndent=18,
                               spaceAfter=8)),
        ]
        items.append(KeepTogether(block))
    items.append(PageBreak())
    return items


# ── Section 12 — RI IEP Framework Quick Reference ───────────────────
def section_framework():
    items = []
    items.append(section_label(
        "SECTION 12 · RI IEP FRAMEWORK QUICK REFERENCE",
        color=PRIMARY))
    items.append(Paragraph(
        "What’s in an IEP — the elements every team must address",
        S["h1"]))
    items.append(Paragraph(
        ("A one-page primer. Per IDEA §300.320 and the Rhode Island "
         "Department of Education IEP framework, every IEP must include "
         "the elements below. Knowing these helps you recognize when a "
         "section is being skipped or compressed."),
        S["lead"]))
    items.append(Spacer(1, 8))

    # RI-specific resources callout placed UP HERE so the grid + closing
    # note land cleanly on the same page.
    items.append(callout(
        "RI-specific resources",
        ("Forms, guidebooks, and FAQs at <b>ride.ri.gov/students-families/"
         "special-education/iep-individual-education-program</b>. RI uses "
         "two IEP forms: <b>Age 3–13</b> and <b>Secondary</b> (14+). "
         "RI begins transition planning at age 14 (earlier than the "
         "federal age-16 floor). The 6-step process for aligning academic "
         "IEP goals to the Common Core State Standards is documented on "
         "the RIDE site."),
        accent=PRIMARY, bg=PRIMARY_BG))
    items.append(Spacer(1, 10))

    elements = [
        ("Present Levels of Performance (PLOP/PLAFP)",
         "Academic AND functional. Measurable baselines. Must describe "
         "how the disability affects involvement and progress in the "
         "general curriculum. → See Section 03 of this Companion."),
        ("Measurable Annual Goals",
         "What the student is expected to accomplish in 12 months. "
         "Stated in measurable terms with how progress is measured and "
         "reported. → See Section 05 for parent’s framing."),
        ("Specially Designed Instruction",
         "The adapted content, methodology, or delivery of instruction "
         "to meet the student’s unique needs. → See Section 07."),
        ("Accommodations & Modifications",
         "Changes that allow the student to access the curriculum, "
         "demonstrate learning, and participate in assessments. → "
         "See Section 06."),
        ("Services — Dates, Frequency, Location, Duration",
         "When services start, how often, where, and for how long. "
         "This is the binding part of the IEP."),
        ("Assessment Participation",
         "How the student will participate in state and district-wide "
         "assessments — with accommodations, without, or via the "
         "RI Alternate Assessment."),
        ("Extended School Year (ESY)",
         "Whether services must continue through summer to prevent "
         "regression of critical skills. Considered annually."),
        ("Transition Services (age 14+ in RI)",
         "Post-school goals + coordinated activities to reach them. "
         "→ See Section 10 if applicable."),
    ]
    cards_data = [
        (f'<font color="{PRIMARY.hexval()}">◆</font>', t, b)
        for t, b in elements
    ]
    items.append(card_grid(cards_data, cols=2, accent_color=PRIMARY,
                           bg_color=WHITE, border_color=BORDER_SOFT))
    items.append(Spacer(1, 10))
    items.append(Paragraph(
        ("Although this Companion uses the RI framework as its reference "
         "point, the section structure is broadly applicable to any "
         "state’s IEP process and to federal IDEA requirements. "
         "Confirm state-specific terminology with your district."),
        ParagraphStyle("ntl", fontName=SANS_OBLIQUE, fontSize=9.5,
                       leading=14, textColor=TEXT_LIGHT,
                       alignment=TA_CENTER)))
    # Note: no trailing PageBreak — parent_support_page handles its own break
    return items


# ── Build ────────────────────────────────────────────────────────────
def build():
    meta_title = (CHILD["first_name"] + " " + CHILD["last_initial"]
                  + " - IEP Prep Companion")
    if TEMPLATE_MODE:
        meta_title = "IEP Prep Companion TEMPLATE"
    meta_subtitle = ("IEP Prep Companion · "
                     + CHILD["first_name"] + " " + CHILD["last_initial"])
    doc = make_doc(OUT, meta_title, meta_subtitle)
    story = []
    story += cover()
    story += iep_disclosures()
    story += how_to_use()
    story += section_student_info()
    story += section_parent_concerns()
    story += section_present_levels()
    story += section_strengths()
    story += section_goal_areas()
    story += section_accommodations()
    story += section_sdi()
    story += section_triggers()
    story += section_existing_team()
    if _is_secondary():
        story += section_transition()
    story += section_questions()
    story += section_framework()
    story += parent_support_page(child_first_name=CHILD["first_name"])
    doc.build(story,
              onFirstPage=lambda c, d: cover_decoration(c, d),
              onLaterPages=lambda c, d: page_decoration(c, d))
    print(f"Built: {OUT}")


if __name__ == "__main__":
    import sys as _sys
    if "--template" in _sys.argv:
        globals()["TEMPLATE_MODE"] = True
        globals()["OUT"] = os.path.join(
            HERE, "7_IEP_Prep_Companion_TEMPLATE.pdf")
    build()
