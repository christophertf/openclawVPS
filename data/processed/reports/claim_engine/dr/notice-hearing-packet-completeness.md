# DR Stage 2 — Claim `notice-hearing-packet-completeness` (Case 23-009185)

## 1) Rule/Law candidates (citation placeholders + plain meaning)

> **Status note:** The record set here is mostly factual/CPRA artifacts; legal pin-cites below are candidate anchors and need jurisdiction-confirmed validation before filing.

1. **California constitutional due process** — **TODO exact citation format** (likely Cal. Const. art. I, § 7 + procedural due process case law).
   - Plain meaning: Before government can impose monetary burdens (special assessments/liens), notice and a meaningful chance to be heard must be reasonably calculated to reach affected parties.

2. **Mullane standard (U.S. due process)** — **TODO exact reporter citation**.
   - Plain meaning: Service method must be reasonably calculated to provide actual notice under the circumstances; repeated failed delivery can require additional reasonable steps.

3. **Jones v. Flowers line** — **TODO exact reporter citation**.
   - Plain meaning: If government learns mailed notice failed (returned/unclaimed), doing nothing further may be constitutionally insufficient where practical alternatives exist.

4. **California Government Code (CPRA production duty)** — **Gov. Code § 7922.530(a)** (formerly § 6253(a)); **TODO confirm formatting/version in final brief**.
   - Plain meaning: Public records must be produced unless exempt; if key hearing packet components are not produced, agency should identify withholding basis or nonexistence.

5. **Sacramento Code references shown in activity notes** — **SCC § 1.28.010(D)(3)(c)(2)(ii) (candidate; TODO verify exact codification text/date)**.
   - Plain meaning: Activity entries repeatedly cite this as authority for penalties/monitoring; if hearing/supporting packet proof is incomplete, use-of-authority chain can be attacked.

6. **State housing/code enforcement notice framework** — **Health & Safety Code § 17980.6 (candidate; TODO verify applicability to this hearing path)**.
   - Plain meaning: Enforcement escalation should be tied to documented conditions and compliant notice process.

---

## 2) Required action (what the City needed to do for this claim to fail)

For each HCAAB/DLHO cycle tied to an assessment/lien, the file should contain (and produce on request):
- Notice of hearing
- Full hearing packet (staff report + exhibits)
- Proof of service set (certified mailing proof, tracking, green card or equivalent, returned envelope scans)
- If mail failed: documented remedial notice steps (re-mail/posting/publication + diligence narrative)
- Hearing outcome/order and downstream council packet/resolution continuity

If these are complete and traceable per cycle, this claim weakens substantially.

---

## 3) What happened (dated fact timeline)

- **2023-06-28 onward:** repeated entries state owner was scheduled for HCAAB/DLHO hearings and that a “Notice of Hearing packet” would be sent by certified mail (many cycles through 2025-10-02).  
  Source: `/home/claw/CASE_FILES/gemini/7_removed_hcaab_hearing_packets.csv`

- **2023-07-06, 2023-08-22, 2023-10-05, 2023-12-19, 2024-02-01, 2024-03-14, 2024-03-15, 2024-08-07, 2025-01-14, 2025-01-24, 2025-09-12, 2025-09-16, 2025-10-15, etc.:** many “received signed certified green card” events, often noting **“Signature unknown”**.  
  Source: `/home/claw/CASE_FILES/timeline/events.json` (multiple event indexes)

- **2023-10-24, 2024-04-24, 2024-05-28, 2024-07-30, 2024-11-26, 2025-05-01, 2025-05-28, 2025-07-02, 2025-08-20, 2025-09-23:** entries report “Due to lack of service… hearing notice is being published in the Sacramento Bulletin.”  
  Source: `/home/claw/CASE_FILES/timeline/events.json`

- **2024-05-17, 2025-06-26 and other dates:** explicit “return mail” logs for hearing packets.  
  Source: `/home/claw/CASE_FILES/timeline/events.json`

- **2025-11-26 addendum and targeted CPRA requests:** requester enumerates missing HCAAB/DLHO packet components (notice, staff report, exhibits, certified proof, minutes/decision, council packet/resolution).  
  Source: `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`, `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md`

---

## 4) Mismatch analysis

### Expected
A complete, cycle-by-cycle hearing packet/service chain that can be produced and audited from notice issuance through hearing outcome and council follow-up.

### Observed
- Activity log repeatedly claims hearing packets were sent.
- Service reliability appears unstable (unknown signatures, returned mail, publication due to lack of service).
- CPRA follow-up artifacts repeatedly seek missing hearing packet/support documents, implying production incompleteness at least from requester perspective.

### Gap significance
- **Strong point for claim:** Pattern-level service irregularity + repeated requests for missing packet components.
- **Weak point / uncertainty:** Current evidence set does **not** yet include definitive agency admission “records do not exist” for each packet element; some proofs may exist in unreviewed document tabs.

---

## 5) Proof table (file path, date, quote/excerpt, reliability)

| File path | Date | Quote / excerpt | Reliability |
|---|---|---|---|
| `/home/claw/CASE_FILES/gemini/7_removed_hcaab_hearing_packets.csv` | 2023-06-28 | “A Notice of Hearing packet will be sent by certified mail on 6/28/23…” (HCAAB) | **Medium** (structured extract; derivative) |
| `/home/claw/CASE_FILES/gemini/7_removed_hcaab_hearing_packets.csv` | 2024-02-16 | “A Notice of Hearing packet has been sent certified… DLHO hearing…” | **Medium** |
| `/home/claw/CASE_FILES/timeline/events.json` | 2023-07-06 | “Received signed certified green card for the 08/09/23 HCAAB hearing packet. **Signature unknown**…” | **High** (primary timeline extract) |
| `/home/claw/CASE_FILES/timeline/events.json` | 2023-10-24 | “Due to lack of service, the 11/15/23 DLHO… Notice is being published in the Sacramento Bulletin…” | **High** |
| `/home/claw/CASE_FILES/timeline/events.json` | 2024-05-17 | “Received return mail for the 05/08/24 HCAAB hearing packet… ‘NOT DELIVERABLE AS ADDRESSED’…” | **High** |
| `/home/claw/CASE_FILES/timeline/events.json` | 2025-06-26 | “Received return mail for the HCAAB 06/11/2025 hearing packet… ‘UNCLAIMED’…” | **High** |
| `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md` | 2025-11-26 | Requests full hearing packets: notice, staff report, exhibits, certified proof, minutes/decision, council packet/resolution for many dates | **Medium** (advocacy request, not agency admission) |
| `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md` | undated (post-review draft) | States hearing packet components “remain missing” and requests production/nonexistence declarations | **Medium** |
| `/home/claw/CASE_FILES/case_codex/paperwork_followup.md` | undated | “Sampling shows none supplied; need complete billing/hearing trail.” | **Low-Med** (analyst summary) |

---

## 6) Counter-evidence / likely defense

Likely City defenses:
1. **Records exist but were not in the subset reviewed** (e.g., Accela document tab/council systems not fully pulled).
2. **Substantial compliance:** certified mail attempts + publication when service failed satisfy notice standards.
3. **Actual notice argument:** signatures (even if “unknown”) and some signed cards prove delivery attempts reasonably calculated to notify.
4. **Administrative regularity presumption:** hearing and council actions imply packets existed even if current CPRA production is incomplete.

---

## 7) Confidence

**Medium.**  
The pattern strongly supports a **completeness-risk** claim, but current dataset lacks final dispositive proof (e.g., agency declaration of nonexistence for each missing hearing packet element, or full packet index showing exact absences).

---

## 8) What would confirm vs what would kill the claim

### Would confirm the claim
- Agency written admission that some hearing packet components (staff reports/exhibits/proofs/minutes/resolutions) cannot be located.
- Production log showing repeated hearing events with only bare notice stubs and no full packet/outcome continuity.
- Evidence that liens/assessments proceeded after known failed service without documented additional reasonable steps.

### Would kill (or severely weaken) the claim
- Complete per-hearing packet production for all contested cycles, including service proofs and outcomes.
- Clear chain linking each HCAAB/DLHO hearing to council agenda/resolution and recorded service remediation.
- Verified delivery evidence (not ambiguous) for key cycles where due-process challenge is strongest.

---

## 9) Next document pulls

1. **Accela Document Tab full export** for case 23-009185 (with document type, upload date, user, filename, linked activity row).
2. **Per-hearing packet index** (HCAAB and DLHO) mapped to every hearing date listed in `cpra_missing_records_addendum.md`.
3. **USPS artifact bundle** for each hearing cycle: certified receipt stub, tracking history printout, green card front/back, returned envelope scans.
4. **Sacramento Bulletin proofs of publication + affidavits** for every “lack of service” publication event.
5. **Hearing outcomes**: minutes/orders and **City Council packet/resolution** for each scheduled council follow-up.
6. **Custodian declaration** identifying systems searched and explicit nonexistence statements for anything not produced.
7. **Local code packet**: exact SCC hearing-notice/service requirements in force on each hearing date (versioned code history).

---

### Bottom line
The evidence currently supports a credible **packet completeness and service-chain vulnerability** theory, but at this stage it is best framed as a **documented risk pattern** rather than a fully proven procedural invalidity. Final determination depends on whether the City can produce complete per-cycle hearing packets and service/audit trails.