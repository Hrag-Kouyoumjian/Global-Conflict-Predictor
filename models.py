from pydantic import BaseModel
from typing import List

# what comes in from the frontend
class ScenarioRequest(BaseModel):
    primary: str    # e.g. "United States"
    target: str     # e.g. "China"
    scenario: str   # e.g. "naval blockade of Taiwan"

# a single headline pulled from the web
class Headline(BaseModel):
    title: str
    source: str
    signal: float   # -1.0 = de-escalatory, +1.0 = escalatory, 0 = neutral

# everything we send back
class ConflictAssessment(BaseModel):
    probability: float
    probability_language: str          # ICD 203 term e.g. "Likely"
    base_rate: float                   # prior before any headlines
    bayesian_update: float             # how much the headlines moved it
    escalation_level: int              # 0-9
    volatility_index: float
    confidence_score: float
    headlines_analyzed: int
    key_factors: List[str]             # each prefixed with DIME-FIL category
    three_month_outlook: str
    twelve_month_outlook: str
    counter_arguments: List[str]
    reasoning_steps: List[str]