# DR Stage 2 — `init-complaint-foundation-gap` (Case 23-009185)

## 1) Rule/Law candidates (citation placeholders + plain meaning)

1. **Sacramento City Code Ch. 8.96 and/or Ch. 8.100** *(TODO: confirm exact sections governing dangerous-building initiation, required findings, and notice thresholds)*  
   - **Plain meaning:** City enforcement actions should be grounded in identified property conditions and documented process steps before escalation.

2. **California Health & Safety Code § 17980.6** *(TODO: confirm exact operative language used by City in this case context)*  
   - **Plain meaning:** Substandard/dangerous building enforcement typically requires documented conditions, notice, and correction pathway.

3. **California Public Records Act (Gov. Code § 7920 et seq.)** *(TODO: confirm specific sections for “records existence / no-record response adequacy”)*  
   - **Plain meaning:** If core enforcement-trigger records are requested, agency should either produce them or explicitly state nonexistence after adequate search.

4. **Procedural due process baseline (U.S. Const. 14th Amend.; Cal. Const. Art. I § 7)** *(TODO: pin to best state/local administrative-law authority for this forum)*  
   - **Plain meaning:** Government action affecting property interests should rest on an auditable factual basis and fair notice.

---

## 2) Required action (for this claim to hold)

To sustain `init-complaint-foundation-gap`, evidence should show:

- The City initiated case 23-009185 from a complaint/initial inspection pathway; **and**
- The foundational records for that initiation (intake form/caller narrative/routing + initial inspection worksheet/evidence) are absent from production; **and**
- No alternative equivalent record packet cures that gap.

---

## 3) What happened (dated fact timeline)

- **2023-03-20** — Events logged: `Pierson INITIAL COMPLAINT`, `INITIAL INSPECTION`, `Pierson INITIAL INSPECTION`, and `HSG - BUSTER PRELIM` (all shown in timeline/master source).  
- **2023-03-20 12:00** — Inspector narrative log says onsite check from front, card left, alley access blocked, and “buster preliminary letter will be requested.”  
- **2023-04-04** — Inspector email narrative restates complaint content (noise/work allegations) and says inspector had verified no permits and had previously visited/sent letter.  
- **Post-production gap analyses (compiled later)** — Missing-paperwork trackers flag the foundational intake/initial inspection records as not located in current production.

---

## 4) Mismatch analysis

### Claimed enforcement foundation
- Case appears to begin from complaint + initial inspection pathway.

### Produced evidentiary foundation (current corpus)
- Timeline has event labels and later narrative references to complaint content.
- But gap index states no standalone initial complaint intake packet and no standalone initial inspection worksheet found in current production.

### Why this matters
- If initiation records are missing, escalation authority can still be argued by City from later records, but the **original factual trigger chain** is less auditable and easier to challenge.
- This is a **record-foundation weakness claim**, not yet a definitive invalidation of the whole case.

---

## 5) Proof table

| File path | Date | Quote / excerpt | Reliability |
|---|---|---|---|
| `/home/claw/CASE_FILES/timeline/events.json` (EV-10000) | 2023-03-20 | `eventType: "Pierson INITIAL COMPLAINT"` | **High** (official timeline extract for event existence) |
| `/home/claw/CASE_FILES/timeline/events.json` (EV-10002) | 2023-03-20 | `eventType: "INITIAL INSPECTION"` | **High** |
| `/home/claw/CASE_FILES/timeline/events.json` (EV-10261) | 2023-03-20 | `I arrived onsite ... no work going on ... left my card ... gate ... buster preliminary letter will be requested.` | **High** (inspector narrative in official event log) |
| `/home/claw/CASE_FILES/timeline/events.json` (EV-10262) | 2023-04-04 | `The City of Sacramento received a complaint ... [detailed allegation text] ... I have verified there are no permits issued...` | **High** for existence of later narrative; **Medium** for proving original intake packet existence |
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | (compiled artifact) | `2023-03-20, INITIAL COMPLAINT ... No narrative provided ... None located in current production` | **Medium-High** (structured gap audit, not raw source packet) |
| `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` | (compiled artifact) | `2023-03-20, INITIAL INSPECTION ... No narrative provided ... None located in current production` | **Medium-High** |
| `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_summary.md` | (request artifact) | `Initial complaint intake + inspection worksheet — rows 1–2` listed as missing records request | **Medium** (advocacy/request document, corroborative not dispositive) |
| `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md` | (request artifact) | Requests 311 intake/hotline log, complaint narrative, forwarding memo, initial inspection worksheet/photos/notes | **Medium** |

---

## 6) Counter-evidence / defense likely

City-side defenses likely:

1. **Substantial evidence via activity log + inspector narrative:** even if original intake form is missing, timeline entries plus inspector notes may be argued sufficient for initiation.
2. **Records retention/production limits:** City may claim nonproduction does not equal nonexistence or invalid enforcement.
3. **Harmless error theory:** downstream inspections/notices/appeals may be argued to cure early documentation defects.
4. **Confidentiality/redaction:** if complainant identity protected, City may argue narrative substance was still effectively disclosed elsewhere.

---

## 7) Confidence

**Medium-High** that there is a **documented foundation gap** in currently produced records for initiation (intake + initial inspection packet level).  
**Medium** on ultimate legal effect (whether this alone defeats enforcement) until exact governing sections and adjudicator standard are confirmed.

---

## 8) What would confirm vs what would kill the claim

### Would confirm (strengthen)
- Written agency statement: no responsive 311 intake / initial inspection worksheet exists after custodian search.
- Absence of any equivalent intake packet in Accela attachments/email archives/case scan exports.
- Hearing/council reliance trace showing enforcement proceeded without those foundational documents.

### Would kill (falsify)
- Production of dated original intake package (311/hotline entry, routing memo, narrative) tied to 2023-03-20 initiation.
- Production of initial inspection worksheet/photos/field notes from same initiation window.
- Metadata proving those records were in system contemporaneously and referenced by decision-makers.

---

## 9) Next document pulls

1. **Accela document-tab export for case 23-009185** with created dates, doc types, uploader, and attachment IDs for Mar–Apr 2023.
2. **311/CRM source record pull** for the complaint routed to code (including routing history and timestamps).
3. **Inspector Lovato + Pierson emails** around 2023-03-20 to 2023-04-05, including forwarded complaint text and any attached photos/worksheet.
4. **Initial inspection worksheet repository query** (all naming variants; include scanned forms and mobile inspection app exports).
5. **Custodian declaration** specifying systems searched, terms used, date range, and whether records are destroyed/retained/redacted.
6. **Any “Buster prelim” referral support memo/checklist** tied to immediate escalation.

---

## Bottom line

Current record set supports a credible claim that **case initiation is evidenced by event labels and later narrative, but the primary initiation packet itself appears missing from production**. That is a meaningful evidentiary weakness; final legal impact remains contingent on exact municipal code language and whether City can later produce equivalent contemporaneous records.