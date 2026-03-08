# Stage 1 Claim Discovery (Pass 1)

**Case context:** 4880 T St / Accela case 23-009185 (City housing/code enforcement)  
**Scope:** Claim hypothesis discovery only (no legal conclusions; no Stage 2 validation)  
**Compiled from:** CASE_FILES timeline/events, case_codex gap analyses, CPRA missing-records summaries, homeowner briefing artifacts, and prior claims notes.

---

## Initiation authority

### 1) 
- claim_id: `init-complaint-foundation-gap`
- claim_title: Missing complaint foundation for case initiation
- claim_hypothesis: If the City cannot produce the original complaint intake narrative and routing records, initial enforcement initiation may lack documented factual basis and auditable trigger authority.
- why_plausible_from_data: `missing_paperwork_index.csv` and CPRA missing-records summaries flag row-1/row-2 intake materials as absent.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv`
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_summary.md`
  - `/home/claw/CASE_FILES/timeline/events.json` (entries around 2023-03-20)
- confidence_prevalidation: high

### 2)
- claim_id: `init-buster-prelim-authority`
- claim_title: Dangerous-building track escalation authority gap
- claim_hypothesis: If the “HSG - BUSTER PRELIM” escalation has no supporting referral memo/checklist, the transition into heightened enforcement may have occurred without complete recorded authorization.
- why_plausible_from_data: Gap files identify missing narrative/attachment for 2023-03-21 BUSTER PRELIM.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv`
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md`
  - `/home/claw/CASE_FILES/timeline/events.json` (2023-03-21)
- confidence_prevalidation: high

### 3)
- claim_id: `init-title-cloud-prereq-gap`
- claim_title: Title/cloud actions without full prerequisite records
- claim_hypothesis: If cloud/title-report actions were taken without complete underlying title report and decision records, authority for downstream notice targeting and beneficiary service may be contestable.
- why_plausible_from_data: Early title/cloud records are repeatedly listed as missing in CPRA follow-up docs.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv`
  - `/home/claw/CASE_FILES/timeline/events.json` (2023-04-11 title/cloud entries)
- confidence_prevalidation: medium

---

## Entry / inspection legality

### 4)
- claim_id: `entry-2025-consent-chain-ambiguity`
- claim_title: Ambiguous consent chain during 2025 backyard/garage entry
- claim_hypothesis: The 2025 entry sequence may raise consent-scope issues if caretaker refusal, warrant threat, later third-party phone consent, and subsequent access were not documented with clear authority and scope boundaries.
- why_plausible_from_data: 2025-08-21 narrative states caretaker wanted cancellation, inspector referenced warrant, then later rep call enabled entry.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (event index around 445)
  - `/home/claw/CASE_FILES/case_codex/pdf_sections/section_01d_activities/section_01d_activities.csv`
  - Any call logs / authorization notes in case management attachments
- confidence_prevalidation: high

### 5)
- claim_id: `entry-garage-access-scope`
- claim_title: Potential overbreadth of inspection scope (garage/interior-related areas)
- claim_hypothesis: If inspection authorization was limited to backyard conditions, entry into detached garage and additional areas may exceed documented scope unless explicit consent/warrant scope is recorded.
- why_plausible_from_data: Narrative references backyard purpose, then detached garage/service panel observations.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (2025-08-21 narrative)
  - Any written consent scope docs or warrant application drafts
  - Inspector worksheet for 2025-08-21
- confidence_prevalidation: medium

### 6)
- claim_id: `entry-warrant-threat-procedure`
- claim_title: Warrant-procedure trigger and documentation gap
- claim_hypothesis: Mentioned move toward inspection warrant suggests procedural prerequisites; absence of warrant prep records (if no actual warrant sought) may expose process irregularity questions.
- why_plausible_from_data: Narrative includes “we would move forward with an inspection warrant,” but current reviewed materials do not show linked warrant packet.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (2025-08-21)
  - Warrant request templates / legal review trail in case file
  - Email trails around 2025-08-21
- confidence_prevalidation: medium

### 7)
- claim_id: `inspection-worksheet-missing-series`
- claim_title: Repeated inspection worksheet/documentation gaps
- claim_hypothesis: If numerous “RE-INSPECTION” events relied on formulaic text without corresponding worksheets/field evidence, inspection legality and factual basis for continued enforcement may be vulnerable.
- why_plausible_from_data: Missing paperwork index repeatedly marks inspection worksheet gaps for cyclical re-inspection entries.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv`
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_summary.md`
  - `/home/claw/CASE_FILES/timeline/events.json`
- confidence_prevalidation: high

---

## Notice / due process

### 8)
- claim_id: `notice-returned-mail-escalation`
- claim_title: Escalation despite repeated returned/undeliverable mail
- claim_hypothesis: If the City escalated penalties/liens while certified notices were repeatedly returned and remedial service steps were weak or undocumented, due-process notice sufficiency may be challenged.
- why_plausible_from_data: Multiple returned-mail entries (2024-02-01; 2025-03-07; 2025-06-19; 2025-08-07; 2025-09-26) plus ongoing escalation flow.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv` (returned mail rows)
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - `/home/claw/CASE_FILES/timeline/events.json` (returned-mail clusters)
- confidence_prevalidation: high

### 9)
- claim_id: `notice-unknown-signature-green-card`
- claim_title: Service reliability issue from unknown-signature green card
- claim_hypothesis: Where hearing packet receipt is logged with “signature unknown,” actual notice to legally responsible parties may be factually uncertain without corroborating service records.
- why_plausible_from_data: Event notes include unknown signature for DLHO hearing packet.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (event around 443)
  - Green-card scan and USPS chain docs in production
  - Beneficiary/address service matrix
- confidence_prevalidation: medium

### 10)
- claim_id: `notice-publication-after-service-failure`
- claim_title: Publication service adequacy after failed direct service
- claim_hypothesis: Resort to publication due to lack of service may be vulnerable if statutory prerequisites, diligence declarations, and timeline sequencing are incomplete.
- why_plausible_from_data: Event logs mention publication in Sacramento Bulletin due to lack of service.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (event around 444)
  - Publication affidavits/proof of publication
  - Diligent search declarations and address-verification records
- confidence_prevalidation: medium

### 11)
- claim_id: `notice-reissue-reset-ambiguity`
- claim_title: Re-issued N&O may imply prior notice defects or reset questions
- claim_hypothesis: A 2025 re-issue of Notice & Order may support a hypothesis that earlier notice chain was defective or stale, potentially affecting continuity of prior penalties.
- why_plausible_from_data: 2025-09-02 “HSG - RE- ISSUE N AND O” with post/re-inspection entries.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (2025-09-02 entries)
  - Re-issue packet and stated rationale
  - Any internal memo explaining need to re-issue
- confidence_prevalidation: high

### 12)
- claim_id: `notice-hearing-packet-completeness`
- claim_title: Hearing packet and proof-of-service completeness gaps
- claim_hypothesis: If hearing notices, exhibits, and proof-of-service packets are incomplete across HCAAB/DLHO cycles, procedural due-process compliance for liens may be contestable.
- why_plausible_from_data: CPRA targeted requests enumerate many hearing packet components still missing.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md`
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - Relevant hearing notice PDFs in produced set
- confidence_prevalidation: high

---

## Evidence integrity

### 13)
- claim_id: `evid-photo-chain-custody`
- claim_title: Photo-to-event chain-of-custody and attribution gaps
- claim_hypothesis: If photos cited in activities are not consistently linked to source files/metadata/declarations per event, evidentiary reliability for condition findings may be disputed.
- why_plausible_from_data: Many photo references; separate photo indexes indicate extensive mapping work and potential linkage gaps to each event.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/case_photos_with_pages.csv`
  - `/home/claw/CASE_FILES/case_codex/photo_evidence_gap_report.md`
  - `/home/claw/CASE_FILES/timeline/events.json`
- confidence_prevalidation: medium

### 14)
- claim_id: `evid-activity-template-reuse`
- claim_title: Boilerplate/template reuse undermining individualized findings
- claim_hypothesis: Repeated templated “send nth admin penalty/monitoring fee” entries may indicate automated progression absent contemporaneous individualized evidence.
- why_plausible_from_data: Activity briefing and gap docs identify large proportion of repetitive boilerplate cycles.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/activity_briefing.md`
  - `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv`
  - `/home/claw/CASE_FILES/timeline/events.json`
- confidence_prevalidation: high

### 15)
- claim_id: `evid-meaningful-entry-scarcity`
- claim_title: Sparse substantive narrative relative to penalty volume
- claim_hypothesis: A record where substantive field narratives are rare compared to penalty actions can support a claim hypothesis that enforcement decisions may outpace documented factual development.
- why_plausible_from_data: Homeowner briefing flags only ~10 meaningful rows out of 200 and just 1% field narrative.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/activity_briefing.md`
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/data/meaningful_entries.csv`
- confidence_prevalidation: high

### 16)
- claim_id: `evid-invoice-support-gap`
- claim_title: Invoice-level support records missing for fee cycles
- claim_hypothesis: If invoices and ledger/approval trails are incomplete for repeated penalties/monitoring fees, financial enforcement evidence integrity may be vulnerable.
- why_plausible_from_data: CPRA addendum explicitly requests billing authorizations, invoices, ledgers by date cycle.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/data/hearing_invoice_refs.csv`
  - Finance/ECAP invoice exports tied to CDDCHA/CDDCHC numbers
- confidence_prevalidation: high

---

## Selective enforcement

### 17)
- claim_id: `selective-complaint-driven-neighbor-pressure`
- claim_title: Potential complaint-pressure/selective focus pattern
- claim_hypothesis: If enforcement trajectory relied heavily on complaint/neighbor narrative while maintaining prolonged penalty cadence despite limited new field findings, selective-emphasis concerns may arise.
- why_plausible_from_data: Early notes mention complaints/neighbors; long penalty cycle with minimal substantive updates.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (initial complaint + early narrative)
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/activity_briefing.md`
  - Comparative enforcement data for nearby similarly situated properties (if obtainable)
- confidence_prevalidation: low

### 18)
- claim_id: `selective-prolonged-cycle-despite-contact`
- claim_title: Continued escalation despite owner-representative engagement
- claim_hypothesis: If owner/representative communications occurred but penalties continued in largely automated fashion without documented individualized reassessment, selective or mechanical enforcement concerns may be arguable.
- why_plausible_from_data: Timeline includes owner friend/rep contact and later access cooperation while cycle continues.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (owner rep calls/emails, 2025-08-21 and 2025-08-25)
  - Email attachments/logged responses
  - Internal decision logs after communications
- confidence_prevalidation: medium

---

## Escalation procedure

### 19)
- claim_id: `escalation-level-c-progression-validity`
- claim_title: Validity of repeated “Level C” escalation progression
- claim_hypothesis: Repeated nth-level penalty escalation may be challengeable if required stepwise findings, approval checkpoints, or recalibration triggers were not documented each cycle.
- why_plausible_from_data: Events repeatedly reference nth admin penalty/monitoring cycles and level language.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json`
  - `/home/claw/CASE_FILES/case_codex/others/penalty_monitoring_row_indices.txt`
  - Department penalty escalation policy SOP
- confidence_prevalidation: medium

### 20)
- claim_id: `escalation-fee-rate-shift-docs`
- claim_title: Fee-rate and surcharge transition documentation gap
- claim_hypothesis: If monitoring fee amounts and collection surcharges changed over time (e.g., $305 to $380; +$20 vs +20%) without clear authorizing records, amount calculations and lien totals may be vulnerable.
- why_plausible_from_data: Cost summaries and hearing references show mixed amount structures.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/cost_summary.md`
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/data/hearing_invoice_refs.csv`
  - Ordinance/rate schedule history and effective dates
- confidence_prevalidation: high

### 21)
- claim_id: `escalation-reissue-fresh-start-theory`
- claim_title: Reissue date supports fresh-start liability segmentation theory
- claim_hypothesis: If 2025 re-issue functionally reset enforcement notice posture, pre-reissue penalty stack could be treated as procedurally distinct from post-reissue claims.
- why_plausible_from_data: Briefing documents explicitly model legacy vs post-2025-09-02 scenarios and rationale.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/one_page_summary.md`
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/cost_summary.md`
  - Re-issue memo and hearing officer rationale
- confidence_prevalidation: medium

### 22)
- claim_id: `escalation-hearing-to-council-link-gap`
- claim_title: Hearing-to-council continuity documentation gap
- claim_hypothesis: If hearing outcomes, appeal rights, and council placement materials are inconsistently linked across cycles, escalation continuity to lien imposition may be procedurally challengeable.
- why_plausible_from_data: CPRA requests specifically seek missing hearing minutes/orders/council packets for many hearing dates.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - Hearing-specific packet PDFs and council agenda/resolution docs
- confidence_prevalidation: high

---

## Recordkeeping / administrative-law

### 23)
- claim_id: `admin-record-retention-nonproduction`
- claim_title: Potential record-retention / nonproduction irregularities
- claim_hypothesis: Persistent inability to produce core intake, worksheet, billing, and service records may indicate retention/search deficiencies affecting administrative reliability.
- why_plausible_from_data: Multiple CPRA rounds remain focused on foundational records not yet produced.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_summary.md`
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - CPRA closure/reopen correspondence in case pipeline inventory
- confidence_prevalidation: high

### 24)
- claim_id: `admin-custodian-search-adequacy`
- claim_title: Custodian search adequacy and system-query sufficiency
- claim_hypothesis: If agency responses do not identify custodians/systems/search methods for missing records, administrative-law challenges to adequacy of search and disclosure process may be plausible.
- why_plausible_from_data: CPRA drafts repeatedly request custodian/system/search-term declarations when records are absent.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md`
  - Final agency response letters (request IDs 25-3549, 25-4711, 26-39, 26-71)
- confidence_prevalidation: medium

### 25)
- claim_id: `admin-activity-log-vs-attachment-parity`
- claim_title: Accela activity log and attachment repository parity gap
- claim_hypothesis: If activity notes reference documents/photos/actions that do not exist in retrievable attachment repositories, the administrative record may be internally inconsistent.
- why_plausible_from_data: Multiple references to declarations/attachments with corresponding “none located” findings in gap index.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/missing_paperwork_index.csv`
  - `/home/claw/CASE_FILES/case_codex/pdf_sections/section_01d_activities/section_01d_activities.csv`
  - Accela document tab export vs produced PDF pagination map
- confidence_prevalidation: high

---

## Remedies-oriented claim hypotheses

### 26)
- claim_id: `remedy-fee-reduction-to-documented-period`
- claim_title: Fee reduction/remittitur to fully documented enforcement period
- claim_hypothesis: If only a subset of penalty cycles is supported by compliant notice and documentary evidence, equitable/statutory reduction to that subset may be a plausible remedy theory.
- why_plausible_from_data: Cost scenario analysis distinguishes full-cycle amount from post-reissue subset and highlights documentation gaps.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/cost_summary.md`
  - `/home/claw/CASE_FILES/case_codex/homeowner_briefing/data/fee_scenarios.csv`
  - Hearing officer orders detailing recoverable amounts
- confidence_prevalidation: medium

### 27)
- claim_id: `remedy-lien-vacatur-for-service-defect`
- claim_title: Lien reversal/vacatur theory tied to service defects
- claim_hypothesis: If service of hearing/penalty notices is not provable for key cycles, lien outcomes derived from those cycles may be vulnerable to reversal or rehearing relief.
- why_plausible_from_data: Repeated returned-mail patterns plus missing remedial-service proof requests.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_addendum.md`
  - `/home/claw/CASE_FILES/timeline/events.json` (returned mail events)
  - Council resolutions and lien recording documents by invoice/date
- confidence_prevalidation: high

### 28)
- claim_id: `remedy-remand-for-complete-record`
- claim_title: Remand/reopening for completion of administrative record
- claim_hypothesis: Where foundational evidence is absent, a remedy theory may seek remand/reopening to compel complete record production before further enforcement collection.
- why_plausible_from_data: Core foundational and cyclical support documents are repeatedly identified as missing.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_missing_records_summary.md`
  - `/home/claw/CASE_FILES/case_codex/cpra_requests/cpra_targeted_missing_records.md`
  - Any adjudicative rules governing reopening/continuance
- confidence_prevalidation: medium

### 29)
- claim_id: `remedy-fee-waiver-humanitarian-discretion`
- claim_title: Discretionary waiver/modification based on owner condition and corrective cooperation
- claim_hypothesis: Narrative references to owner condition and cooperation with contractor engagement may support discretionary mitigation/waiver arguments, especially if safety corrections were pursued.
- why_plausible_from_data: 2025-08-21 narrative notes power shutoff was withheld due to owner condition and contractor-directed correction path.
- key_artifacts_to_check_next:
  - `/home/claw/CASE_FILES/timeline/events.json` (2025-08-21, 2025-08-25 entries)
  - Contractor permit/inspection follow-up records
  - Agency hardship/mitigation policy
- confidence_prevalidation: low

---

## Top 10 priority claims for immediate deep research

1. `notice-returned-mail-escalation`  
2. `init-complaint-foundation-gap`  
3. `init-buster-prelim-authority`  
4. `inspection-worksheet-missing-series`  
5. `notice-hearing-packet-completeness`  
6. `entry-2025-consent-chain-ambiguity`  
7. `admin-activity-log-vs-attachment-parity`  
8. `evid-invoice-support-gap`  
9. `escalation-fee-rate-shift-docs`  
10. `remedy-lien-vacatur-for-service-defect`

---

## Notes for Stage 2 handoff
- These are **hypotheses only**, not legal conclusions.
- Stage 2 should validate each hypothesis against governing municipal code, California due-process/admin-law standards, hearing rules, and produced/withheld documentary record.
- Immediate document pull priority: intake records, inspection worksheets, complete service proofs, invoice ledgers/approvals, hearing packet + council packet continuity docs.
