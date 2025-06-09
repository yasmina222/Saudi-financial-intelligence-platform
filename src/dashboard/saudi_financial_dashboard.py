import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

# page configuration
st.set_page_config(
    page_title="Saudi Financial Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# custom CSS for professional appearance
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# api configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# cache API calls for 5 minutes
@st.cache_data(ttl=300)
def fetch_api_data(endpoint):
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def create_compliance_gauge(score):
    """Create Sharia compliance gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={'reference': 80},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sharia Compliance Score", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "darkgreen" if score >= 80 else "orange"},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 80], 'color': "lightyellow"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# header
# NEW CODE TO ADD
st.header("DEMONSTRATION PLATFORM")
st.title("Saudi Financial Intelligence Dashboard")
st.markdown("Real-time sentiment analysis and market intelligence for the Saudi financial markets.")
st.markdown("A Proof-of-Concept built on a real-world architecture, demonstrating Saudi-specific AI capabilities using a custom, domain-focused dataset.")

# main metrics row
col1, col2, col3, col4 = st.columns(4)

# fetch market summary
market_data = fetch_api_data("/market-summary")

if market_data:
    with col1:
        st.metric("Total Articles Analyzed", market_data['total_articles'])
    
    with col2:
        positive_pct = round(market_data['sentiment_breakdown']['positive'] / market_data['total_articles'] * 100, 1)
        st.metric("Positive Sentiment", f"{positive_pct}%")
    
    with col3:
        compliance_data = fetch_api_data("/islamic/compliance")
        if compliance_data:
            st.metric("Sharia Compliance Score", f"{compliance_data['sharia_score']}%")
        else:
            st.metric("Sharia Compliance Score", "N/A")
    
    with col4:
        alert_count = len(market_data.get('critical_alerts', []))
        st.metric("Critical Alerts", alert_count, delta=None if alert_count == 0 else "!")

# critical alerts section
if market_data and market_data.get('critical_alerts'):
    with st.expander(f"⚠️ View {len(market_data['critical_alerts'])} Critical Alerts", expanded=False):
        for i, alert in enumerate(market_data['critical_alerts'], 1):
            st.error(f"{i}. {alert}")
else:
    st.success("✓ No critical alerts at this time")

# tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Market Overview", "Saudi Companies", "Islamic Finance", "Vision 2030", "Arabic Analysis"])

with tab1:
    st.header("Market Sentiment Analysis")
    
    if market_data:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            sentiment_df = pd.DataFrame([
                {"Sentiment": k.capitalize(), "Count": v} 
                for k, v in market_data['sentiment_breakdown'].items()
            ])
            
            fig = px.bar(
                sentiment_df, 
                x="Sentiment", 
                y="Count",
                color="Sentiment",
                color_discrete_map={
                    "Positive": "#28a745",
                    "Negative": "#dc3545",
                    "Neutral": "#6c757d"
                },
                title="Sentiment Distribution"
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Top Mentioned Entities")
            if market_data.get('top_entities'):
                for entity in market_data['top_entities'][:5]:
                    st.write(f"• {entity}")
            else:
                st.write("No Saudi entities detected")
                st.caption("Awaiting Tadawul data integration")
    

    st.header("Tadawul Market Movers")
    tadawul_data = fetch_api_data("/tadawul/top-movers")
    
    if tadawul_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Top Gainers")
            gainers_data = []
            # Use .get('top_gainers', []) to safely access the key
            for stock in tadawul_data.get('top_gainers', []):
                gainers_data.append({
                    "Symbol": stock.get('symbol'), # Use .get for safety
                    "Name": stock.get('name'),   # Use .get for safety
                    "Change": stock.get('change_percent') # <<< CHANGED 'change' to 'change_percent'
                })
            gainers_df = pd.DataFrame(gainers_data)
            st.dataframe(
                gainers_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Change": st.column_config.TextColumn(
                        "Change %", # Label is already "Change %" which is good
                        help="Daily percentage change"
                    )
                }
            )
        
        with col2:
            st.subheader("Top Losers")
            losers_data = []
            # Use .get('top_losers', []) to safely access the key
            for stock in tadawul_data.get('top_losers', []):
                losers_data.append({
                    "Symbol": stock.get('symbol'), # Use .get for safety
                    "Name": stock.get('name'),   
                    "Change": stock.get('change_percent') # 
                })
            losers_df = pd.DataFrame(losers_data)
            st.dataframe(
                losers_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Change": st.column_config.TextColumn(
                        "Change %", 
                        help="Daily percentage change"
                    )
                }
            )
        
        with col3:
            st.subheader(" Most Active")
            # Use .get('most_active_by_volume', []) for safety
            for symbol in tadawul_data.get('most_active_by_volume', []): 
                st.write(f"• {symbol}")
            st.caption(f"Market Trend: {tadawul_data.get('market_trend', 'neutral').upper()}") # API doesn't provide market_trend yet
            st.caption(f"Source: {tadawul_data.get('data_source_comment', 'Simulated Data')}")

with tab2:
    st.header("Saudi Company Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        companies = ["Saudi Aramco", "SABIC", "STC", "Al Rajhi Bank", "Maaden"]
        selected_company = st.selectbox("Select Company", companies)
        
        if st.button("Analyze Company", type="primary"):
            company_data = fetch_api_data(f"/saudi/sentiment/{selected_company}")
            
            if company_data:
                # display metrics in cards
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{selected_company.upper()}</h3>
                    <p><strong>Sentiment:</strong> {company_data['sentiment'].upper()}</p>
                    <p><strong>Confidence Score:</strong> {company_data['score']:.3f}</p>
                    <p><strong>Confidence Level:</strong> {company_data['confidence'].upper()}</p>
                    <p><small>Last Updated: {company_data['timestamp']}</small></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"No sentiment data available for {selected_company}")
                st.info("This indicates limited coverage in current news sources")
    
    with col2:
        st.subheader("Data Coverage")
        st.caption("Current data sources:")
        st.write("• Generic financial news")
        st.write("• Limited Saudi coverage")
        st.caption("Pending integration:")
        st.write("• Tadawul announcements")
        st.write("• Argaam financial data")

with tab3:
    st.header("Islamic Finance Monitoring")
    
    compliance_data = fetch_api_data("/islamic/compliance")
    
    if compliance_data:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # sharia compliance gauge
            fig = create_compliance_gauge(compliance_data['sharia_score'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # compliance details
            st.subheader("Compliance Breakdown")
            
            # zakat status
            zakat_icon = "✅" if compliance_data['zakat_payment'] else "❌"
            st.write(f"**Zakat Payment Status**: {zakat_icon} {'Compliant' if compliance_data['zakat_payment'] else 'Non-Compliant'}")
            
            # riba exposure with color coding
            riba_colors = {"low": "green", "medium": "orange", "high": "red"}
            riba_level = compliance_data['riba_exposure']
            st.markdown(f"**Riba Exposure Level**: <span style='color:{riba_colors[riba_level]}'>{riba_level.upper()}</span>", unsafe_allow_html=True)
            
            # recommendations
            st.subheader("Recommendations")
            if compliance_data['sharia_score'] >= 80:
                st.success("Maintain current Sharia compliance practices")
            else:
                st.warning("Review and enhance Sharia compliance measures")
    
    # islamic term analysis
    st.divider()
    st.subheader("Islamic Finance Term Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        islamic_terms = ["sukuk", "riba", "zakat", "murabaha"]
        selected_term = st.selectbox("Select Islamic Finance Term", islamic_terms)
    
    with col2:
        if st.button("Analyze Term", type="secondary"):
            term_data = fetch_api_data(f"/islamic/sentiment/{selected_term}")
            
            if term_data and 'overall_sentiment' in term_data:
                sentiment_color = {
                    "positive": "green",
                    "negative": "red",
                    "neutral": "gray"
                }
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{selected_term.upper()} Analysis</h4>
                    <p>Overall Sentiment: <span style='color:{sentiment_color[term_data['overall_sentiment']]}'>{term_data['overall_sentiment'].upper()}</span></p>
                    <p>Articles Found: {term_data['article_count']}</p>
                    <p>Average Score: {term_data['average_score']:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if term_data.get('articles'):
                    st.write("**Recent Articles:**")
                    for article in term_data['articles']:
                        st.write(f"- {article['title']}")
            else:
                st.info(f"No data available for term: {selected_term}")


with tab4:
    st.header("Vision 2030 Projects")
    st.caption("Mega-project sentiment and status tracking")
    
    # Load Vision 2030 progress data
    vision_progress = fetch_api_data("/vision2030/progress")  
    
    projects = ["neom", "red-sea", "qiddiya", "trojena", "diriyah"]
    
    # project grid with enhanced display
    for i in range(0, len(projects), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(projects):
                project = projects[i + j]
                with cols[j]:
                    project_data = fetch_api_data(f"/vision2030/{project}")
                    
                    if project_data:
                        # project card
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{project.upper()}</h4>
                            <p><strong>Sentiment:</strong> {project_data['sentiment'].upper()}</p>
                            <p><strong>Funding Mentions:</strong> {project_data['funding_mentions']}</p>
                            <p><strong>Status:</strong> {project_data['implementation_status'].replace('_', ' ').title()}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add progress bar
                        progress = project_data.get('completion_percentage', 0)
                        if progress > 0:
                            st.progress(progress / 100)
                            st.caption(f"📊 {progress}% Complete")
                            
                            # Add color-coded status
                            if progress == 100:
                                st.success("✅ Project Completed")
                            elif progress >= 75:
                                st.info("🚀 Final Phase")
                            elif progress >= 50:
                                st.warning("🏗️ Major Construction")
                            else:
                                st.caption("📋 Early Development")
                        else:
                            st.caption("📍 Planning Phase")

with tab5:
    st.header("Arabic Market Sentiment Analysis")
    st.info("Analysis based on the rule-based engine processing our custom-generated Arabic financial dataset.")

    # Fetch data from the new API endpoint
    arabic_summary_data = fetch_api_data("/arabic/market-summary")

    if arabic_summary_data:
        # Display Key Metrics
        acc = arabic_summary_data.get('accuracy', 0.0) * 100
        total_articles = arabic_summary_data.get('total_articles_analyzed', 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Analysis Type", "Rule-Based")
        with col2:
            st.metric("Total Arabic Articles", total_articles)
        with col3:
            st.metric("Model Accuracy", f"{acc:.1f}%")

        st.divider()

        col1_arabic, col2_arabic = st.columns([2, 1])

        # Display Sentiment Distribution Chart
        with col1_arabic:
            st.subheader("Sentiment Distribution (Arabic)")
            sentiment_data = arabic_summary_data.get('sentiment_breakdown', {})

            if sentiment_data:
                sentiment_df_ar = pd.DataFrame([
                    {"Sentiment": k.capitalize(), "Count": v}
                    for k, v in sentiment_data.items()
                ])

                fig_ar = px.bar(
                    sentiment_df_ar,
                    x="Sentiment",
                    y="Count",
                    color="Sentiment",
                    color_discrete_map={
                        "Positive": "#28a745",
                        "Negative": "#dc3545",
                        "Neutral": "#6c757d"
                    },
                    title="Sentiment of Generated Arabic Articles"
                )
                fig_ar.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_ar, use_container_width=True)
            else:
                st.warning("Sentiment breakdown data is not available.")

        # Display Top Mentioned Terms
        with col2_arabic:
            st.subheader("Top Mentioned Terms (Arabic)")
            top_terms = arabic_summary_data.get('top_mentioned_terms', [])
            if top_terms:
                # Use a dataframe for a cleaner look
                terms_df = pd.DataFrame(top_terms, columns=["Term"])
                st.dataframe(terms_df, hide_index=True, use_container_width=True)
            else:
                st.write("No recurring terms were detected in this analysis batch.")

    else:
        st.error("Could not fetch Arabic analysis summary. Please ensure the API is running and the analysis has been processed.")

# footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    Saudi Financial Intelligence Platform | Real-time market analysis for Vision 2030
</div>
""", unsafe_allow_html=True)

# sidebar
with st.sidebar:
    st.header("System Status")
    
    st.write(f"**Last Update**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.subheader("Data Sources")
    st.write("✅ Generic financial news")
    st.write("⏳ Tadawul integration pending")
    st.write("⏳ SAMA feed pending")
    st.write("⏳ Argaam integration pending")
    
    st.subheader("Coverage Analysis")
    if market_data:
        saudi_coverage = round(3/35 * 100, 1)  # based on your entity extraction
        st.metric("Saudi Content", f"{saudi_coverage}%", delta="-91.5%")
        st.caption("Demonstrates need for local sources")
    
    if st.button("Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()