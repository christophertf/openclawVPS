# DR Stage 2 — Claim `inspection-worksheet-missing-series` (Case 23-009185)

## 1) Rule/Law candidates (citation placeholders + plain meaning)

1. **[TODO: Sacramento City Code chapter/section governing code-enforcement inspections, re-inspections, and basis for notices/penalties]**  
   - Plain meaning: Before escalating enforcement (penalties/monitoring/lien flow), the agency should have a factual inspection basis for each escalation step.

2. **[TODO: Sacramento City Code chapter/section governing administrative penalties + hearing record support]**  
   - Plain meaning: Administrative penalty actions generally require a defensible record showing violations persisted and that required procedures were followed.

3. **[TODO: California Gov. Code § 53069.4 or other controlling admin-penalty statute as applied by local ordinance]**  
   - Plain meaning: Local agencies can impose administrative penalties, but process must include adequate factual basis and review/hearing protections.

4. **[TODO: U.S. Const. amend. XIV + Cal. Const. due-process anchors (as applied to municipal enforcement)]**  
   - Plain meaning: Property-impacting penalties/liens need reliable factual basis and fair process; weak record support can undermine defensibility.

5. **[TODO: CPRA non-production standards under current California Public Records Act codification (Gov. Code Title 1.81)]**  
   - Plain meaning: If records do not exist, agency should clearly say so; if they exist, they should be produced unless exempt.

---

## 2) Required action

To sustain this claim, the record should show either:
- (A) actual inspection worksheets/field packets for each monthly “Send n-th admin penalty / monitoring fee” re-inspection, **or**
- (B) a formal declaration that no such worksheets exist and an alternative legally sufficient evidentiary basis was used for each escalation.

Absent A or B, the series of penalty escalations appears record-thin and vulnerable.

---

## 3) What happened (dated fact timeline)

- **2023-04-11**: First recurring template appears: “Any contact from owner? … Send 1st admin penalty / Monitoring fee.”  
- **2023-05-19 through 2025-10-16**: Repeated `RE- INSPECTION` entries by Paul Lovato with near-identical “Any contact… Send n-th admin penalty / monitoring fee” wording, increasing from 1st through 23rd.  
- **Across these entries**: `missing_paperwork_index.csv` marks gap category as **Inspection Worksheet** and states **“None located in current production.”**  
- **2025-08-21**: Separate re-inspection note (“Backyard inspection at 1:00pm”) indicates at least one non-template field-action entry exists in the activity log universe.  
- **CPRA checklist** explicitly identifies missing “inspection worksheet / field notes” rows for the monthly send-nth sequence (rows 13, 19, 25, …, 195).

---

## 4) Mismatch analysis

**Claim theory:** repeated enforcement escalations may lack underlying inspection documentation.  
**Observed mismatch:**
1. Activity log shows long-run escalation triggers (“Send n-th admin penalty / monitoring fee”).
2. Missing-paperwork index repeatedly tags those same events as “Inspection Worksheet” gaps.
3. Existing evidence column repeatedly says no supporting worksheet in current production.
4. CPRA missing-records summary independently flags the same row set as missing worksheet/field notes.

This is a coherent cross-source mismatch: escalation language is present; corresponding worksheet support is not present in produced set.

---

## 5) Proof table

| File path | Date | Quote / excerpt | Reliability |
|---|---|---|---|
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | 2023-04-11 | `RE- INSPECTION ... Gap_Category: Inspection Worksheet ... Existing_Evidence: None located in current production` | **High** (structured index) |
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | 2023-05-19 | `Any contact from owner? Permits acquired? Send 1st admin penalty / Monitoring fee.` + `None located in current production` | **High** |
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | 2024-11-13 | `Send 15th admin penalty / Monitoring fee.` + `Gap_Category: Inspection Worksheet` + `None located in current production` | **High** |
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | 2025-07-21 | `Send 22nd admin penalty / Monitoring fee.` + `Gap_Category: Inspection Worksheet` + `None located in current production` | **High** |
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | 2025-10-16 | `Send 23rd admin penalty / Monitoring fee.` + `Gap_Category: Inspection Worksheet` + `None located in current production` | **High** |
| `/home/claw/CASE_FILES/case_codex/pdf_sections/section_01d_activities/section_01d_activities.csv` | 2023-04-11 | `Any contact from owner? Re-visit site...` (template-style re-inspection) | **High** (direct activity export) |
| `/home/claw/CASE_FILES/case_codex/pdf_sections/section_01d_activities/section_01d_activities.csv` | 2025-08-21 | `RE- INSPECTION ... Backyard inspection at 1:00pm` | **High** (counter-pattern instance) |
| `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_summary.md` | (undated file; references row set) | `Inspection worksheet / field notes for every “Send n-th admin penalty / monitoring fee” re-inspection — rows 13, 19, 25, ... 195` | **Medium-High** (derived checklist, not original source docs) |
| `/home/claw/CASE_FILES/gemini/2_removed_inspection_worksheet.csv` | 2023-04-11 | includes the same template re-inspection text; supports recurring pattern extraction | **Medium** (processing artifact, but consistent with activity log) |

---

## 6) Counter-evidence / likely defense

1. **“Missing in production” ≠ “never existed.”** Agency may claim worksheets exist in another system, were withheld, or not yet located.
2. **Re-inspection may be visual/drive-by + posting actions.** Agency may argue formal worksheet not legally required for every re-check if violation persistence was already established.
3. **Some non-template inspection evidence exists** (e.g., 2025-08-21 backyard inspection note), which weakens an absolute “no field evidence at all” framing.
4. **Internal index is secondary analysis.** Defense may challenge `missing_paperwork_index.csv` as analyst-created rather than official agency certification.

---

## 7) Confidence

**Medium-High** that the claim is supportable as a **production-gap / record-support weakness**.  
**Medium** for any stronger claim that inspections definitively did not occur.

---

## 8) What would confirm vs what would kill the claim

### Would confirm
- Official response/declaration: no worksheets/field notes exist for listed re-inspection rows.
- Hearing packet(s) rely on monthly escalation cycle without attached inspection backup.
- Internal policy requiring worksheets for such re-inspections, coupled with missing records across the sequence.

### Would kill (or sharply weaken) the claim
- Production of complete worksheets/field notes/photos for the cited re-inspection dates (especially the 25-row send-nth sequence).
- Audit log showing each monthly re-inspection has contemporaneous field evidence in another repository.
- Legal authority/policy explicitly allowing penalty progression without new worksheet-level documentation per cycle.

---

## 9) Next document pulls

1. **Primary:** Official worksheet/field packet pull for these dates: 2023-04-11, 2023-05-19, 2023-06-28, …, 2025-10-16 (all 26 “Inspection Worksheet” gaps in index).  
2. **System metadata:** Accela attachments table/export (file IDs, upload timestamps, who uploaded, deleted/superseded flags).  
3. **Hearing binders:** HCAAB + DLHO packet exhibits for cycles linked to “Send n-th…” entries; verify whether inspection evidence was attached.  
4. **Records custodian declaration:** explicit statement of existence/nonexistence and search locations for inspection worksheets.  
5. **Policy docs:** departmental SOP on re-inspection documentation requirements and minimum evidentiary standard before issuing recurring admin penalties/monitoring fees.

