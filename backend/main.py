from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer import (
    find_app_by_url,
    collect_reviews,
    analyze_reviews,
    get_risk_level
)


app = FastAPI(title="App Risk Intelligence API")


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://10.16.114.114:5176",
],    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class AnalyzeRequest(BaseModel):
    url: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "App Risk Intelligence API is running"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# =========================================================
# ANALYZE APP
# =========================================================

@app.post("/analyze")
def analyze_app(request: AnalyzeRequest):

    url = request.url.strip()

    if not url:
        raise HTTPException(
            status_code=400,
            detail="Play Store URL is required."
        )

    # Get app details
    details = find_app_by_url(url)

    if not details:
        raise HTTPException(
            status_code=400,
            detail="Invalid or inaccessible Play Store URL."
        )

    # App ID
    app_id = details.get("appId")

    if not app_id:
        raise HTTPException(
            status_code=400,
            detail="Could not identify the app."
        )

    # Collect reviews
    review_data = collect_reviews(
        app_id,
        count=100
    )

    if not review_data:
        raise HTTPException(
            status_code=404,
            detail="No reviews could be collected for this app."
        )

    # Analyze reviews
    result = analyze_reviews(review_data)

    if not result:
        raise HTTPException(
            status_code=500,
            detail="Review analysis failed."
        )

    # Risk level
    risk_level = get_risk_level(
        result["risk_score"]
    )

    # Final response
    return {
        "app": {
            "name": details.get("title"),
            "developer": details.get("developer"),
            "rating": details.get("score"),
            "ratings_count": details.get("ratings")
        },

        "reviews_analyzed": result["total"],

        "sentiment": {
            "positive": round(result["positive"], 2),
            "neutral": round(result["neutral"], 2),
            "negative": round(result["negative"], 2)
        },

        "fraud_related_reviews": result["fraud_reviews"],

        "risk_score": round(
            result["risk_score"],
            2
        ),

        "risk_level": risk_level,

        "confidence": result["confidence"],

        "detected_concerns": result["concerns"]
    }
