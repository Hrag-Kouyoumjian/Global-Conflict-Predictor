import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import ScenarioRequest, ConflictAssessment
from scraper import fetch_headlines
from analyzer import analyze

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=ConflictAssessment)
async def analyze_scenario(request: ScenarioRequest):

    if not request.primary or not request.target or not request.scenario:
        raise HTTPException(status_code=400, detail="primary, target, and scenario are required")

    # pull live headlines for both countries
    headlines = fetch_headlines(request.primary, request.target)

    # run bayesian update + claude analysis
    result = await analyze(request.primary, request.target, request.scenario, headlines)

    return result