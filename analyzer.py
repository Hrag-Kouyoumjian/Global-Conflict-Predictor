import os
import json
import anthropic
from models import Headline, ConflictAssessment

client = anthropic.Anthropic(api_key=os.environ.get("Put your Anthropic API Key HERE"))

# historical base rates — rough priors based on known conflict history
# these are starting points before headlines move them
BASE_RATES = {
    ("United States", "China"): 0.25,
    ("United States", "Russia"): 0.30,
    ("India", "Pakistan"): 0.45,
    ("Israel", "Iran"): 0.50,
    ("Armenia", "Azerbaijan"): 0.40,
    ("North Korea", "South Korea"): 0.35,
    ("China", "Taiwan"): 0.40,
}

DEFAULT_BASE_RATE = 0.15  # for pairs with no historical data


def get_base_rate(primary: str, target: str) -> float:
    # check both orderings since user could enter either way
    key1 = (primary, target)
    key2 = (target, primary)
    return BASE_RATES.get(key1) or BASE_RATES.get(key2) or DEFAULT_BASE_RATE


def bayesian_update(prior: float, headlines: list[Headline]) -> float:
    if not headlines:
        return prior

    # average signal across all headlines — ranges from -1 to +1
    avg_signal = sum(h.signal for h in headlines) / len(headlines)

    # scale the signal — strong signal moves prior by up to 20 points
    # weak signal barely moves it
    adjustment = avg_signal * 0.20

    updated = prior + adjustment

    # clamp between 1% and 99% — never say never, never say certain
    return max(0.01, min(0.99, updated))


def to_icd203(probability: float) -> str:
    p = probability * 100
    if p <= 5:   return "Remote"
    if p <= 20:  return "Highly Unlikely"
    if p <= 45:  return "Unlikely"
    if p <= 55:  return "Roughly Even Chance"
    if p <= 80:  return "Likely"
    if p <= 95:  return "Highly Likely"
    return "Almost Certain"


async def analyze(primary: str, target: str, scenario: str, headlines: list[Headline]) -> ConflictAssessment:

    prior = get_base_rate(primary, target)
    updated_probability = bayesian_update(prior, headlines)

    # build headline context for Claude
    headline_context = "\n".join(
        [f"- {h.title} (signal: {h.signal:+.2f})" for h in headlines]
    ) if headlines else "No recent headlines found."

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a Senior Geopolitical Intelligence Director operating under ICD 203 analytic standards.

Primary Actor: {primary}
Target/Adversary: {target}
Scenario: {scenario}

Computed conflict probability (Bayesian, based on {len(headlines)} headlines): {updated_probability * 100:.1f}%

Recent headlines and their escalatory signals:
{headline_context}

Using the DIME-FIL framework, assess:
- Military capabilities and posture
- Alliance structures
- Economic interdependencies  
- Nuclear posture if relevant
- Domestic political stability
- Historical conflict patterns

Escalation ladder:
0=Baseline Stability, 1=Rhetorical Escalation, 2=Diplomatic Deterioration,
3=Economic Coercion, 4=Military Signaling, 5=Gray Zone Operations,
6=Blockade/Quarantine, 7=Limited Kinetic Action, 8=Conventional Conflict,
9=Strategic Escalation

Return ONLY valid JSON, no markdown, no text outside the object:
{{
  "escalation_level": <0-9>,
  "volatility_index": <0.0-1.0>,
  "confidence_score": <0.0-1.0>,
  "key_factors": ["<5-7 factors prefixed with DIME-FIL category>"],
  "three_month_outlook": "<2-3 sentences>",
  "twelve_month_outlook": "<2-3 sentences>",
  "counter_arguments": ["<2-3 reasons this assessment could be wrong>"],
  "reasoning_steps": ["<6-8 steps showing analytical process>"]
}}"""
            }
        ]
    )

    raw = message.content[0].text.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(clean)

    return ConflictAssessment(
        probability=round(updated_probability * 100, 1),
        probability_language=to_icd203(updated_probability),
        base_rate=round(prior * 100, 1),
        bayesian_update=round((updated_probability - prior) * 100, 1),
        escalation_level=result["escalation_level"],
        volatility_index=result["volatility_index"],
        confidence_score=result["confidence_score"],
        headlines_analyzed=len(headlines),
        key_factors=result["key_factors"],
        three_month_outlook=result["three_month_outlook"],
        twelve_month_outlook=result["twelve_month_outlook"],
        counter_arguments=result["counter_arguments"],
        reasoning_steps=result["reasoning_steps"]
    )


#How Bayesian Math Works 

#prior = 0.25  (US/China historical base rate)

#headlines avg signal = +0.4  (moderately escalatory news)
#adjustment = 0.4 * 0.20 = +0.08

#updated = 0.25 + 0.08 = 0.33  (33% → "Unlikely" in ICD 203)