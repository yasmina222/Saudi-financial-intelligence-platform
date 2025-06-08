from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from collections import Counter

app = FastAPI(
    title="Saudi Financial Intelligence API",
    description="Real-time sentiment and alerts for Saudi financial markets",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class SentimentResponse(BaseModel):
    company: str
    sentiment: str
    score: float
    confidence: str
    timestamp: str

class IslamicAlert(BaseModel):
    term: str
    alert_type: str
    severity: str
    description: str

class MarketSummary(BaseModel):
    market: str
    total_articles: int
    sentiment_breakdown: Dict[str, int]
    top_entities: List[str]
    critical_alerts: List[str]

class IslamicCompliance(BaseModel):
    sharia_score: float
    zakat_payment: bool
    riba_exposure: str  # 'high/medium/low'

class Vision2030ProjectData(BaseModel):
    project: str
    sentiment: str
    completion_percentage: int
    funding_mentions: int
    implementation_status: str

# --- Global Variables & Helper Functions ---
TADAWUL_TOP = ["2222.SR", "2010.SR", "1120.SR"]  # ARAMCO, SABIC, ALRAJHI

# Entity name mapping for common variations
# These should match EXACTLY what's in saudi_entity_extractor.py
ENTITY_MAPPINGS = {
    "aramco": "Saudi Aramco",
    "saudi aramco": "Saudi Aramco",
    "al rajhi": "Al Rajhi Bank",
    "al rajhi bank": "Al Rajhi Bank",
    "alrajhi": "Al Rajhi Bank",
    "rajhi": "Al Rajhi Bank",
    "sabic": "SABIC",
    "stc": "STC",
    "saudi telecom": "STC",
    "saudia": "Saudia",
    "saudi airlines": "Saudia",
    "ncb": "NCB",
    "national commercial bank": "NCB",
    "snb": "Saudi National Bank (SNB)",
    "saudi national bank": "Saudi National Bank (SNB)",
    "samba": "Saudi National Bank (SNB)",
    "maaden": "Maaden",
    "ma'aden": "Maaden",
    "saudi arabian mining": "Maaden",
    "almarai": "Almarai",
    "riyad bank": "Riyad Bank",
    "alinma": "Alinma Bank",
    "alinma bank": "Alinma Bank"
}

def normalize_entity_name(entity_name):
    """Normalize entity names to match processed data"""
    # Convert to lowercase for comparison
    lower_name = entity_name.lower().strip()
    
    # Check if we have a direct mapping
    if lower_name in ENTITY_MAPPINGS:
        return ENTITY_MAPPINGS[lower_name]
    
    # Return original name if no mapping found
    return entity_name

def load_latest_data(prefix: str, directory: str = "data/processed"):
    if not os.path.exists(directory):
        return None
    files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(".json")]
    if not files:
        return None
    latest_file = sorted(files, reverse=True)[0]
    try:
        with open(os.path.join(directory, latest_file), 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None

def load_vision_2030_progress():
    progress_file = "data/processed/vision_2030_progress.json"
    if not os.path.exists(progress_file):
        return None
    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None

# --- API Endpoints ---
@app.get("/")
def root():
    return {
        "message": "Saudi Financial Intelligence API",
        "available_endpoints": [
            "/saudi/sentiment/{company_name}",
            "/market-summary",
            "/islamic/alerts",
            "/islamic/sentiment/{term}",
            "/islamic/compliance",
            "/tadawul/top-movers",
            "/vision2030/{project_name}",
            "/arabic/market-summary",
            "/docs"
        ]
    }

@app.get("/saudi/sentiment/{company_name}", response_model=SentimentResponse)
def get_saudi_company_sentiment(company_name: str):
    # Load processed entity data
    data = load_latest_data(prefix="saudi_entities_")
    if not data:
        raise HTTPException(status_code=404, detail="No processed entity data available.")
    
    # Normalize the company name for matching
    normalized_query = normalize_entity_name(company_name)
    
    # Track if we found any data
    found_articles = []
    
    # Iterate through the list of processed articles
    for article in data:
        entities = article.get('entities', {})
        # Get saudi companies (these are already standardized by the entity extractor)
        saudi_companies_in_article = entities.get('saudi_specific', [])
        
        # Check if our normalized query matches any company in the article
        if normalized_query in saudi_companies_in_article:
            found_articles.append(article)
    
    if not found_articles:
        raise HTTPException(
            status_code=404, 
            detail=f"No sentiment data available for company: {company_name}. This indicates limited coverage in current news sources."
        )
    
    # Get the most recent article's sentiment (or aggregate if needed)
    # For now, return the first match
    article = found_articles[0]
    
    return SentimentResponse(
        company=company_name,  # Return original name as passed
        sentiment=article.get('sentiment', 'neutral'),
        score=article.get('sentiment_score', 0.0),
        confidence=article.get('confidence', 'low'),
        timestamp=article.get('analyzed_at', datetime.now().isoformat())
    )

@app.get("/market-summary", response_model=MarketSummary)
def get_market_summary(market: str = Query('saudi', description="Specify market: 'saudi' or 'uae'")):
    if market.lower() == 'uae':
        return {
            "market": "UAE (United Arab Emirates)",
            "total_articles": 0,
            "sentiment_breakdown": {},
            "top_entities": [],
            "critical_alerts": ["UAE market analysis coming soon - In Development"]
        }
    
    # Saudi market analysis
    processed_articles = load_latest_data(prefix="saudi_entities_")
    event_data = load_latest_data(prefix="saudi_events_")
    
    if not processed_articles:
        raise HTTPException(status_code=404, detail="No processed Saudi data available for market summary.")
    
    total_articles_count = len(processed_articles)
    sentiments_counter = Counter()
    all_saudi_entities_list = []
    
    for article in processed_articles:
        sentiments_counter[article.get('sentiment', 'neutral')] += 1
        entities_dict = article.get('entities', {})
        all_saudi_entities_list.extend(entities_dict.get('saudi_specific', []))
    
    top_saudi_entities = [entity for entity, count in Counter(all_saudi_entities_list).most_common(5)]
    
    critical_alerts_list = []
    if event_data:
        for article_event_info in event_data:
            article_events = article_event_info.get('events', {})
            if article_events.get('event_importance') == 'critical':
                critical_alerts_list.append(article_event_info.get('title', 'Untitled Alert')[:100] + "...")
    
    return MarketSummary(
        market="Saudi Arabia",
        total_articles=total_articles_count,
        sentiment_breakdown=dict(sentiments_counter),
        top_entities=top_saudi_entities,
        critical_alerts=critical_alerts_list
    )

@app.get("/islamic/alerts", response_model=List[IslamicAlert])
def get_islamic_finance_alerts():
    data = load_latest_data(prefix="saudi_events_")
    if not data:
        return []
    
    alerts_found = []
    for article_event_info in data:
        islamic_alerts_list = article_event_info.get('events', {}).get('islamic_alerts', [])
        article_title = article_event_info.get('title', 'Untitled Article')

        for alert_type_keyword in islamic_alerts_list:
            if alert_type_keyword == 'sukuk_default':
                alerts_found.append(IslamicAlert(
                    term="sukuk",
                    alert_type="Default Risk",
                    severity="Critical",
                    description=f"Potential sukuk default indicated in: {article_title[:100]}..."
                ))
            elif alert_type_keyword == 'riba_concern':
                alerts_found.append(IslamicAlert(
                    term="riba",
                    alert_type="Compliance Concern",
                    severity="High",
                    description=f"Riba (interest) concern noted in: {article_title[:100]}..."
                ))
    
    return alerts_found

@app.get("/islamic/sentiment/{term}")
def get_islamic_term_sentiment(term: str):
    data = load_latest_data(prefix="saudi_entities_")
    if not data:
        raise HTTPException(status_code=404, detail="No processed data available for Islamic term analysis.")
    
    term_lower = term.lower()
    matching_articles_details = []
    
    for article in data:
        islamic_terms_in_article = [str(t).lower() for t in article.get('entities', {}).get('islamic_finance', [])]
        if term_lower in islamic_terms_in_article:
            matching_articles_details.append({
                "title": article.get('title', 'Untitled Article'),
                "sentiment": article.get('sentiment', 'neutral'),
                "score": article.get('sentiment_score', 0.0)
            })
    
    if not matching_articles_details:
        raise HTTPException(status_code=404, detail=f"No data found for Islamic term: {term}")
    
    positive_count = sum(1 for art in matching_articles_details if art['sentiment'] == 'positive')
    negative_count = sum(1 for art in matching_articles_details if art['sentiment'] == 'negative')
    
    overall_sentiment_label = "neutral"
    if positive_count > negative_count:
        overall_sentiment_label = "positive"
    elif negative_count > positive_count:
        overall_sentiment_label = "negative"
        
    average_score = sum(art['score'] for art in matching_articles_details) / len(matching_articles_details)
    
    return {
        "term_analyzed": term,
        "overall_sentiment": overall_sentiment_label,
        "average_sentiment_score": round(average_score, 3),
        "articles_count": len(matching_articles_details),
        "sample_articles": matching_articles_details[:5]
    }

@app.get("/islamic/compliance", response_model=IslamicCompliance)
def get_islamic_market_compliance():
    data = load_latest_data(prefix="saudi_entities_")
    
    if not data:
        return IslamicCompliance(
            sharia_score=100.0,
            zakat_payment=True,
            riba_exposure="low"
        )
    
    riba_mentions_count = 0
    zakat_mentions_count = 0
    total_articles_analyzed = len(data)
    
    for article in data:
        islamic_terms_in_article = article.get('entities', {}).get('islamic_finance', [])
        if 'riba' in islamic_terms_in_article:
            riba_mentions_count += 1
        if 'zakat' in islamic_terms_in_article:
            zakat_mentions_count += 1
            
    current_sharia_score = 100.0
    riba_exposure_level = "low"
    
    if total_articles_analyzed > 0:
        riba_ratio = riba_mentions_count / total_articles_analyzed
        if riba_ratio > 0.2:
            current_sharia_score = 60.0
            riba_exposure_level = "high"
        elif riba_ratio > 0.1:
            current_sharia_score = 80.0
            riba_exposure_level = "medium"

    is_zakat_payment_mentioned = zakat_mentions_count > 0
    if is_zakat_payment_mentioned and current_sharia_score < 95:
         current_sharia_score = min(current_sharia_score + 5, 100.0)

    return IslamicCompliance(
        sharia_score=current_sharia_score,
        zakat_payment=is_zakat_payment_mentioned,
        riba_exposure=riba_exposure_level
    )

@app.get("/tadawul/top-movers")
def get_tadawul_stock_movers():
    return {
        "data_source_comment": "Simulated data until live Tadawul API integration is feasible.",
        "last_simulated_update": datetime.now().isoformat(),
        "top_gainers": [
            {"symbol": "2222.SR", "name": "Saudi Aramco", "change_percent": "+2.1%"},
            {"symbol": "2010.SR", "name": "SABIC", "change_percent": "+1.8%"},
            {"symbol": "1120.SR", "name": "Al Rajhi Bank", "change_percent": "+1.5%"}
        ],
        "top_losers": [
            {"symbol": "4001.SR", "name": "Al Othaim Markets", "change_percent": "-2.3%"},
            {"symbol": "2050.SR", "name": "Savola Group", "change_percent": "-1.9%"},
            {"symbol": "4002.SR", "name": "Mouwasat Medical Services", "change_percent": "-1.4%"}
        ],
        "most_active_by_volume": TADAWUL_TOP
    }

@app.get("/vision2030/{project_name}", response_model=Vision2030ProjectData)
def get_vision2030_project_info(project_name: str):
    project_key = project_name.lower().replace('-', '_')

    vision_progress_data = load_vision_2030_progress()
    processed_event_data = load_latest_data(prefix="saudi_events_")

    project_sentiment_value = "neutral"
    completion_percentage_value = 0
    funding_mentions_count = 0
    implementation_status_text = "Not Found"

    if vision_progress_data and project_key in vision_progress_data:
        completion_percentage_value = vision_progress_data[project_key]
    elif vision_progress_data is None and processed_event_data is None:
         raise HTTPException(status_code=404, detail="No Vision 2030 data (progress or events) available.")

    if completion_percentage_value == 100:
        implementation_status_text = "Completed"
    elif completion_percentage_value > 0:
        implementation_status_text = "In Progress"
    elif vision_progress_data and project_key in vision_progress_data:
        implementation_status_text = "Planning"

    if processed_event_data:
        articles_about_project_found = False
        for article in processed_event_data:
            article_title_lower = article.get('title', '').lower()
            original_project_field = article.get('project', '').lower()

            if project_key in article_title_lower or project_key == original_project_field:
                articles_about_project_found = True
                project_sentiment_value = article.get('sentiment', project_sentiment_value)
                
                description_lower = article.get('description', '').lower()
                if "fund" in article_title_lower or "invest" in article_title_lower or \
                   "fund" in description_lower or "invest" in description_lower:
                    funding_mentions_count += 1

        if not articles_about_project_found and not (vision_progress_data and project_key in vision_progress_data):
             raise HTTPException(status_code=404, detail=f"Specific information for project '{project_name}' not found in processed data.")
        elif articles_about_project_found and implementation_status_text == "Not Found":
            implementation_status_text = "Mentioned (No specific progress data)"

    return Vision2030ProjectData(
        project=project_name,
        sentiment=project_sentiment_value,
        completion_percentage=completion_percentage_value,
        funding_mentions=funding_mentions_count,
        implementation_status=implementation_status_text
    )

# --- Arabic Analysis Endpoints ---
def load_arabic_analysis_report():
    """Helper function to load the JSON report from the rule-based analyzer."""
    report_path = "data/processed/rule_based_arabic_analysis_report.json"
    if not os.path.exists(report_path):
        return None
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None

@app.get("/arabic/market-summary")
def get_arabic_market_summary():
    """
    Provides a summary of the sentiment analysis performed on the Arabic dataset.
    Data is sourced from the output of the rule-based analyzer.
    """
    report = load_arabic_analysis_report()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Arabic analysis report not found. Please run the enhanced_arabic_analyser.py script first."
        )

    accuracy = report.get('accuracy', 0.0)
    total_articles = report.get('total_examples', 0)
    confusion_matrix = report.get('confusion_matrix', {})

    sentiment_breakdown = {
        'positive': sum(confusion_matrix.get('positive', {}).values()),
        'negative': sum(confusion_matrix.get('negative', {}).values()),
        'neutral': sum(confusion_matrix.get('neutral', {}).values())
    }

    all_matched_terms = Counter()
    for item in report.get('results_breakdown', []):
        for sentiment_type, terms in item.get('matched_terms', {}).items():
            all_matched_terms.update(terms)

    top_entities = [term for term, count in all_matched_terms.most_common(5)]

    return {
        "analysis_type": "Rule-Based Arabic Sentiment",
        "accuracy": accuracy,
        "total_articles_analyzed": total_articles,
        "sentiment_breakdown": sentiment_breakdown,
        "top_mentioned_terms": top_entities
    }

# --- Main execution ---
if __name__ == "__main__":
    import uvicorn
    print("Starting Saudi Financial Intelligence API...")
    print("Access API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Add this test endpoint temporarily
@app.get("/test-normalization/{company_name}")
def test_normalization(company_name: str):
    normalized = normalize_entity_name(company_name)
    return {
        "input": company_name,
        "normalized": normalized,
        "mappings": ENTITY_MAPPINGS
    }