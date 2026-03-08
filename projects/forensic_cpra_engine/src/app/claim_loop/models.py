from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List


@dataclass
class EvidenceRef:
    path: str
    quote: str
    timestamp: str = ""
    page_or_line: str = ""
    sha256: str = ""


@dataclass
class ClaimRecord:
    claim_id: str
    claim_text: str
    claim_type: str
    status: str  # supported|unproven|contradicted
    confidence: float
    evidence: List[EvidenceRef]
    counter_evidence: List[EvidenceRef]
    law_refs: List[str]
    next_action: str
    limitations: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = [asdict(e) for e in self.evidence]
        d["counter_evidence"] = [asdict(e) for e in self.counter_evidence]
        return d
