# Conflicts Analyzer

A geopolitical conflict probability engine that scrapes live news headlines 
and applies a Bayesian framework to assess the likelihood of escalation 
between two state actors.

## Background

I spent time living in Armenia through Birthright Armenia, and being there 
made global conflict feel a lot less abstract. The region had just come out 
of the 2020 Nagorno-Karabakh war, and tensions with Azerbaijan were still 
very much alive.

But it wasn't just Armenia. I found myself constantly reading about 
conflicts everywhere: Ukraine, Taiwan, the South China Sea, the Middle East. 
Part of what pulled me in was following Live UA Map and Deep State Map during 
the Ukraine war. Something was compelling about how conflict was being 
documented in real time through unbiased digital representation, front lines 
shifting day by day, visualized without editorial spin.

That got me thinking about the gap between what is happening on the ground 
and how it gets communicated. News headlines are either alarmist or buried. 
I wanted something that could take live reporting and turn it into a structured 
probability, the kind of analytical framework intelligence analysts actually 
use, not just a gut feeling.


## How it works

1. Scrapes Google News for recent headlines mentioning both countries
2. Claude scores each headline for escalatory signal (-1.0 to +1.0)
3. A Bayesian update adjusts a historical base rate based on the headline signals
4. Claude then runs a full DIME-FIL analysis on top of the computed probability
5. Returns a structured assessment with escalation level, outlooks, and counter-arguments

The probability is live — run it today vs during an active crisis and you 
get different numbers because it's pulling real headlines each time.

## Probability Framework

Uses ICD 203 analytic standards — the same confidence language used by 
US intelligence community analysts:

| Range | Language |
|---|---|
| 1-5% | Remote |
| 5-20% | Highly Unlikely |
| 20-45% | Unlikely |
| 45-55% | Roughly Even Chance |
| 55-80% | Likely |
| 80-95% | Highly Likely |
| 95-99% | Almost Certain |

## Stack

- FastAPI
- Anthropic Claude API (headline scoring + DIME-FIL analysis)
- BeautifulSoup (Google News RSS scraping)
- Bayesian base rate updating

## Run

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn main:app --reload
```

## Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "primary": "Armenia",
    "target": "Azerbaijan",
    "scenario": "military escalation along border"
  }'
```

## Example Response

```json
{
  "probability": 38.5,
  "probability_language": "Unlikely",
  "base_rate": 40.0,
  "bayesian_update": -1.5,
  "escalation_level": 3,
  "volatility_index": 0.7,
  "confidence_score": 0.65,
  "headlines_analyzed": 12,
  "key_factors": [
    "MILITARY: Armenia has signed defense agreements with France and India",
    "DIPLOMATIC: Ongoing peace talks mediated by EU",
    "ECONOMIC: Both countries remain dependent on regional trade corridors"
  ],
  "three_month_outlook": "...",
  "twelve_month_outlook": "...",
  "counter_arguments": ["..."],
  "reasoning_steps": ["..."]
}
```
