# DR Stage 2 — Claim `init-buster-prelim-authority` (Case 23-009185)

## Executive Summary
The record supports a **real documentation gap risk** around the 2023-03-21 `HSG - BUSTER PRELIM` escalation, but does **not yet conclusively prove** unauthorized escalation. Evidence shows a Buster escalation activity with blank notes and CPRA follow-up repeatedly demanding the referral/checklist/approval basis. At the same time, the produced document index lists a `HSG - Buster Prelim.htm` merge document dated 2023-03-20, which is potential counter-evidence that some escalation artifact exists. Current posture: **partially strengthened claim, not yet dispositive**. Confidence is **Medium** pending pull/review of the actual `HSG - Buster Prelim.htm` contents, metadata, and approval trail.

---

## 1) Rule/Law candidates (citation placeholders + plain meaning)

1. **Sacramento City Code Chapter 8.96** — `[TODO exact section: initiation/procedure for substandard buildings]`  
   Plain meaning: before dangerous/substandard-building enforcement actions, agency should document qualifying conditions and follow chapter procedures.

2. **Sacramento City Code Chapter 8.100** — `[TODO exact section: initiation/procedure for dangerous buildings]`  
   Plain meaning: dangerous-building pathway should be triggered by documented condition findings and formal process steps.

3. **Sacramento City Code § 1.28.010(D)(3)(c)(2)(ii)** (appears in case notes; formatting to confirm in codebook)  
   Plain meaning: Level C penalties/monitoring are tied to willful disregard of lawful orders/notices; implies validity of earlier order/escalation steps matters.

4. **California Health & Safety Code § 17980.6** `[TODO verify exact quoted text applicability to this municipal track]`  
   Plain meaning: cited in CPRA correspondence as requiring enforcement to be grounded in documented conditions and process.

5. **Procedural due process baseline** — `[TODO add controlling case/statute for local nuisance/dangerous-building administrative actions]`  
   Plain meaning: agency action affecting property rights should be supported by an administrative record sufficient to show basis and reviewability.

---

## 2) Required action
For this claim to fail (i.e., City authority shown), record should include:
- a contemporaneous referral/checklist/memo approving `HSG - BUSTER PRELIM`;
- underlying factual predicate (inspection findings/photos/complaint narrative);
- linkage from that predicate to dangerous-building track criteria;
- authorship/date metadata confirming it was created at decision time (not later reconstruction).

Absent those, escalation authority remains vulnerable.

---

## 3) What happened (dated fact timeline)

- **2023-03-20**: Activity log shows `INITIAL COMPLAINT` and `INITIAL INSPECTION` entries, both with no notes in the table extraction.  
- **2023-03-20 12:00**: Inspector note states site visit, no contact, blocked rear gate, and: “**A buster preliminary letter will be requested**.”  
- **2023-03-20**: Documents list includes merge document `HSG - Buster Prelim.htm` (description: `HSG - Buster Prelim - HSG - BUSTER PRELIM`, 36 KB).  
- **2023-03-21**: Activities table shows `HSG - BUSTER PRELIM` assigned to Monica Atkins with blank notes.  
- **2023-04-11**: Re-inspection note references “**see work Buster prelim sent out 2 weeks ago**,” then same-day movement toward `HSG - NOTICE ORD S/DB` and cloud/title actions.
- **CPRA follow-ups (2025-11 onward)**: repeated targeted requests seek the Buster referral checklist/approval memo and factual basis, indicating requester still treated it as missing from productions.

---

## 4) Mismatch analysis

### Claimed requirement vs documented record
- **Expected**: explicit authorization artifact for dangerous-building-track escalation.
- **Observed**: escalation event exists, but core activity note is blank; CPRA trackers flag missing referral memo/checklist.

### Tension / ambiguity
- **Gap evidence**: `missing_paperwork_index.csv` tags 2023-03-21 BUSTER entry as blank/no narrative and requests referral support.
- **Counterpoint**: documents inventory shows `HSG - Buster Prelim.htm` exists (dated 2023-03-20), which may itself be the escalation artifact.
- **Net**: authority gap is plausible but not proven until the actual content of `HSG - Buster Prelim.htm` is reviewed.

---

## 5) Proof table (file path, date, quote/excerpt, reliability)

| File path | Date | Quote / excerpt | Reliability |
|---|---|---|---|
| `/home/claw/CASE_FILES/case_codex/pdf_sections/section_01d_activities/section_01d_activities_table.md` | 2023-03-21 | `| 03/21/2023 | HSG - BUSTER PRELIM | Monica Atkins | — |` | **High** (structured extract from source PDF activity table) |
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | 2023-03-21 row | `HSG - BUSTER PRELIM... Gap_Category: Blank... Log_Notes: No narrative provided... Existing_Evidence: - Buster Prelim.htm (03/20/2023)` | **High** (curated gap index derived from production set) |
| `/home/claw/CASE_FILES/case_codex/pdf_sections/section_04_notes.md` | 2023-03-20 | `A buster preliminary letter will be requested.` | **High** (raw notes extract) |
| `/home/claw/CASE_FILES/case_codex/pdf_sections/section_03_documents.md` | 2023-03-20 | `Merge document   HSG - Buster Prelim.htm ... 03/20/2023 ... 36 KB` | **High** (documents inventory extract) |
| `/home/claw/CASE_FILES/timeline/events.csv` | 2023-04-11 | `...see work Buster prelim sent out 2 weeks ago...` | **High** (timeline extract from source file) |
| `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md` | 2025-10-28 | `HSG – BUSTER PRELIM ... referral checklist or approval memo documenting the factual basis...` | **Medium-High** (advocacy/request doc, not agency admission) |
| `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_initial_intake.md` | 2025-11-26 | requests `Referral memo, checklist, or approval...` for 2023-03-21 BUSTER | **Medium-High** (same reason: requester characterization) |

---

## 6) Counter-evidence / likely defense

1. **City can argue the escalation record exists**: `HSG - Buster Prelim.htm` is listed in produced document inventory, so no true “authority gap.”
2. **Workflow defense**: Buster prelim may be an administrative trigger letter, not requiring separate memo/checklist beyond inspector note + merge doc.
3. **Timing coherence defense**: 3/20 note says prelim letter will be requested; 3/20 merge doc exists; 3/21 activity entry logs completion.
4. **Subsequent confirmation defense**: 4/11 note references Buster prelim sent two weeks earlier, indicating operational follow-through.

---

## 7) Confidence
**Medium**.

Reason: Strong evidence of **missing explicit narrative/approval in activity table** and repeated CPRA demand for referral basis; but equally important, there is documented existence of a `HSG - Buster Prelim.htm` artifact that could satisfy authority if content is substantive.

---

## 8) What would confirm vs what would kill the claim

### Would confirm claim (authority gap)
- `HSG - Buster Prelim.htm` is only a template shell / form letter with no factual findings, approval, or criteria check.
- No separate referral/approval metadata or workflow logs exist for dangerous-building track transition.
- Custodian declaration confirms no checklist/memo/approval found in Accela, email, shared drives, or inspector files.

### Would kill claim (authority established)
- Produced `HSG - Buster Prelim.htm` (or linked record) contains case-specific findings, legal basis, and authorization trail.
- Accela audit/workflow history shows who approved escalation and when, with supporting attachments.
- Inspector or supervisor contemporaneous memo/checklist ties 3/20 findings to Chapter 8 dangerous-building trigger criteria.

---

## 9) Next document pulls

1. **Native file pull**: `HSG - Buster Prelim.htm` (full body + headers + metadata + linked resources).
2. **Accela audit trail export** for case 23-009185 around 2023-03-20 to 2023-03-22 (status changes, workflow actions, user IDs, attachment IDs).
3. **Email discovery pull** (Lovato, Atkins, supervisors) with terms: `buster`, `prelim`, `23-009185`, `dangerous building`, `N&O` for 2023-03-15..2023-04-01.
4. **Inspector worksheet/field log pull** for 2023-03-20 and 2023-03-21.
5. **Policy/SOP pull** for when `HSG - BUSTER PRELIM` can be used and required approvals/checklists.
6. **Custodian declaration** detailing systems searched and nonexistence rationale if no referral memo/checklist exists.

---

## Bottom line
The claim is **not falsified** and remains viable, but currently rests on an **incomplete record**: blank activity narrative + missing-request pattern versus existence of a likely key document (`HSG - Buster Prelim.htm`) not yet content-validated.