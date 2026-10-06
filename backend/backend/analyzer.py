from google_play_scraper import app, reviews, Sort
from urllib.parse import urlparse, parse_qs
import re


# =========================================================
# PLAY STORE URL → APP ID
# =========================================================

def get_app_id_from_url(url):
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return params.get("id", [None])[0]
    except Exception:
        return None


# =========================================================
# GET APP DETAILS
# =========================================================

def find_app_by_url(url):
    app_id = get_app_id_from_url(url)

    if not app_id:
        return None

    try:
        return app(
            app_id,
            lang="en",
            country="in"
        )
    except Exception:
        return None


# =========================================================
# COLLECT REVIEWS
# =========================================================

def collect_reviews(app_id, count=100):
    try:
        review_data, _ = reviews(
            app_id,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=count
        )

        return review_data

    except Exception:
        return []


# =========================================================
# SENTIMENT
# =========================================================

positive_words = [
    "good", "great", "excellent", "best",
    "awesome", "love", "nice", "easy",
    "helpful", "fast", "amazing",
    "super", "satisfied", "working",
    "useful", "genuine", "trusted",
    "reliable"
]

negative_words = [
    "bad", "worst", "poor", "terrible",
    "hate", "useless", "slow",
    "problem", "issue", "disappointed",
    "angry", "waste", "failed",
    "fake", "horrible"
]


def sentiment_analysis(text):
    text = text.lower()

    positive_score = 0
    negative_score = 0

    for word in positive_words:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            positive_score += 1

    for word in negative_words:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            negative_score += 1

    if positive_score > negative_score:
        return "positive"

    elif negative_score > positive_score:
        return "negative"

    else:
        return "neutral"


# =========================================================
# FRAUD PATTERNS
# =========================================================

fraud_patterns = {

    "Money deduction": [
        "money deducted",
        "amount deducted",
        "money was deducted",
        "money got deducted",
        "money taken",
        "money lost",
        "lost my money"
    ],

    "Withdrawal problems": [
        "withdrawal",
        "cannot withdraw",
        "can't withdraw",
        "unable to withdraw",
        "withdrawal failed",
        "withdraw my money"
    ],

    "Refund complaints": [
        "refund",
        "refund not received",
        "refund pending",
        "money not refunded",
        "didn't get refund"
    ],

    "Unauthorized transactions": [
        "unauthorized",
        "unknown transaction",
        "without my permission",
        "without permission"
    ],

    "Scam / Fraud complaints": [
        "scam",
        "fraud",
        "fraudulent",
        "cheated",
        "cheating",
        "fake app",
        "stole my money"
    ],

    "Job / Earning complaints": [
        "job scam",
        "fake job",
        "earning scam",
        "work from home scam",
        "captcha job",
        "captcha work",
        "didn't pay me",
        "not paid"
    ],

    "Account blocking complaints": [
        "account blocked",
        "blocked my account",
        "account suspended",
        "account banned",
        "locked my account"
    ],

    "Payment problems": [
        "payment failed",
        "payment issue",
        "payment problem",
        "transaction failed",
        "payment not received"
    ]
}


def detect_fraud_patterns(text):
    text = text.lower()

    detected = []

    for category, patterns in fraud_patterns.items():

        for pattern in patterns:

            if pattern in text:
                detected.append(category)
                break

    return detected


# =========================================================
# ANALYZE REVIEWS
# =========================================================

def analyze_reviews(review_data):

    total = len(review_data)

    positive = 0
    neutral = 0
    negative = 0

    fraud_reviews = 0

    detected_concerns = set()

    evidence_score = 0

    for review in review_data:

        text = review.get("content", "").strip()

        if not text:
            continue

        # Sentiment
        sentiment = sentiment_analysis(text)

        if sentiment == "positive":
            positive += 1

        elif sentiment == "negative":
            negative += 1

        else:
            neutral += 1

        # Fraud patterns
        concerns = detect_fraud_patterns(text)

        if concerns:

            fraud_reviews += 1

            for concern in concerns:
                detected_concerns.add(concern)

            evidence_score += min(
                len(concerns) * 2,
                6
            )

    if total == 0:
        return None

    positive_percent = positive / total * 100
    neutral_percent = neutral / total * 100
    negative_percent = negative / total * 100

    fraud_percent = fraud_reviews / total * 100

    # Risk calculation
    sentiment_risk = negative_percent

    fraud_risk = min(
        fraud_percent * 2.5,
        70
    )

    evidence_risk = min(
        evidence_score * 0.5,
        20
    )

    risk_score = (
        sentiment_risk * 0.20
        + fraud_risk * 0.60
        + evidence_risk * 0.20
    )

    risk_score = min(
        max(risk_score, 0),
        100
    )

    # Confidence
    if total >= 100:
        confidence = "High"

    elif total >= 50:
        confidence = "Medium"

    else:
        confidence = "Low"

    return {
        "total": total,
        "positive": positive_percent,
        "neutral": neutral_percent,
        "negative": negative_percent,
        "fraud_reviews": fraud_reviews,
        "concerns": sorted(list(detected_concerns)),
        "risk_score": risk_score,
        "confidence": confidence
    }


# =========================================================
# RISK LEVEL
# =========================================================

def get_risk_level(score):

    if score <= 30:
        return "LOW"

    elif score <= 60:
        return "MEDIUM"

    else:
        return "HIGH"
