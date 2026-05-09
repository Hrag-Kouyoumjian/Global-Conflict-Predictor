import requests
from bs4 import BeautifulSoup
from models import Headline
import anthropic
import os
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def fetch_headlines(primary: str, target: str) -> list[Headline]:
    
    query = f"{primary} {target} conflict military diplomatic".replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "xml")
    
    items = soup.find_all("item")[:15]  # cap at 15, more than enough signal
    
    raw_headlines = []
    for item in items:
        title = item.find("title")
        source = item.find("source")
        if title:
            raw_headlines.append({
                "title": title.text,
                "source": source.text if source else "unknown"
            })
    
    if not raw_headlines:
        return []
    
    return score_headlines(raw_headlines, primary, target)


def score_headlines(raw: list[dict], primary: str, target: str) -> list[Headline]:
    
    # ask Claude to score each headline's escalatory signal
    # doing this in one batch call instead of one per headline
    headline_list = "\n".join([f"{i+1}. {h['title']}" for i, h in enumerate(raw)])
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""Score each headline for escalatory signal between {primary} and {target}.

-1.0 = clearly de-escalatory (ceasefire, diplomacy, talks, agreement)
 0.0 = neutral or unrelated
+1.0 = clearly escalatory (military action, sanctions, threats, buildup)

Headlines:
{headline_list}

Return ONLY a JSON array of numbers, one per headline, in order. No text outside the array.
Example: [-0.3, 0.8, 0.0, 0.5]"""
            }
        ]
    )
    
    raw_response = message.content[0].text.strip()
    clean = raw_response.replace("```json", "").replace("```", "").strip()
    scores = json.loads(clean)
    
    headlines = []
    for i, h in enumerate(raw):
        score = scores[i] if i < len(scores) else 0.0
        headlines.append(Headline(
            title=h["title"],
            source=h["source"],
            signal=float(score)
        ))
    
    return headlines