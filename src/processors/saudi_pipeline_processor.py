import json
import os
from datetime import datetime

class SaudiDataProcessor:
    def __init__(self):
        self.sentiment_file = None
        self.entity_file = None
        self.event_file = None
        
    def load_saudi_data(self):
        """Load the latest Saudi data"""
        saudi_file = "data/raw/saudi/latest_saudi_data.json"
        with open(saudi_file, 'r') as f:
            return json.load(f)
    
    def prepare_for_sentiment_analysis(self, saudi_data):
        """Convert Saudi data to format expected by sentiment analyzer"""
        print("Preparing Saudi data for sentiment analysis...")
        
        all_articles = []
        
        # combine all article types
        for article in saudi_data['saudi_finance']:
            all_articles.append({
                'title': article['title'],
                'url': article['url'],
                'source': article['source'],
                'category': 'saudi_finance',
                'sentiment_hint': article.get('sentiment_hints', 'neutral')
            })
            
        for article in saudi_data['islamic_finance']:
            all_articles.append({
                'title': article['title'],
                'url': article['url'],
                'source': article['source'],
                'category': 'islamic_finance',
                'sentiment_hint': article.get('sentiment_hints', 'neutral')
            })
            
        for article in saudi_data['vision_2030']:
            all_articles.append({
                'title': article['title'],
                'url': article['url'],
                'source': article['source'],
                'category': 'vision_2030',
                'sentiment_hint': article.get('sentiment_hints', 'neutral')
            })
        
        # save in format expected by sentiment analyzer
        output_file = f"data/raw/saudi_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(all_articles, f, indent=2)
            
        print(f"Saved {len(all_articles)} articles ready for sentiment analysis: {output_file}")
        return output_file
    
    def run_sentiment_analysis(self, news_file):
        """Run sentiment analysis on Saudi data"""
        print("\nRunning sentiment analysis on Saudi data...")
        
        # import and run existing sentiment analyzer
        import sys
        sys.path.append('src/ml')
        from sentiment_analyser import FinancialSentimentAnalyzer
        
        analyzer = FinancialSentimentAnalyzer()
        results = analyzer.analyze_articles(news_file)
        self.sentiment_file = analyzer.save_results(results)
        analyzer.print_summary(results)
        
        return self.sentiment_file
    
    def run_entity_extraction(self, sentiment_file):
        """Run entity extraction on sentiment results"""
        print("\nRunning Saudi entity extraction...")
        
        # import and run existing entity extractor
        import sys
        sys.path.append('src/ml')
        from saudi_entity_extractor import SaudiFinancialEntityExtractor
        
        extractor = SaudiFinancialEntityExtractor()
        results = extractor.process_sentiment_results(sentiment_file)
        self.entity_file = extractor.save_results(results)
        
        return self.entity_file
    
    def run_event_detection(self, entity_file):
        """Run event detection on entity results"""
        print("\nRunning Saudi event detection...")
        
        # import and run existing event detector
        import sys
        sys.path.append('src/ml')
        from saudi_event_detector import SaudiEventDetector
        
        detector = SaudiEventDetector()
        results = detector.process_entity_results(entity_file)
        self.event_file = detector.save_results(results)
        
        return self.event_file
    
    def update_dashboard_data(self):
        """Update dashboard to show Vision 2030 progress"""
        print("\nUpdating dashboard with Saudi data...")
        
        # load Saudi data for Vision 2030 progress
        saudi_data = self.load_saudi_data()
        
        # extract progress data
        progress_data = {}
        for project, updates in saudi_data['metadata']['vision_2030_projects'].items():
            if updates:
                max_progress = max([u.get('progress', 0) for u in updates])
                progress_data[project] = max_progress
        
        # save for dashboard
        dashboard_file = "data/processed/vision_2030_progress.json"
        with open(dashboard_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
            
        print(f"Vision 2030 progress data saved: {dashboard_file}")
        print("Progress percentages:")
        for project, progress in progress_data.items():
            print(f"  {project.upper()}: {progress}%")
            
        return dashboard_file
    
    def process_complete_pipeline(self):
        """Run the complete Saudi data processing pipeline"""
        print("=" * 60)
        print("SAUDI DATA PROCESSING PIPELINE")
        print("=" * 60)
        
        # load Saudi data
        saudi_data = self.load_saudi_data()
        
        # step 1: prepare for sentiment
        news_file = self.prepare_for_sentiment_analysis(saudi_data)
        
        # step 2: sentiment analysis
        sentiment_file = self.run_sentiment_analysis(news_file)
        
        # step 3: entity extraction
        entity_file = self.run_entity_extraction(sentiment_file)
        
        # step 4: event detection
        event_file = self.run_event_detection(entity_file)
        
        # step 5: update dashboard data
        dashboard_file = self.update_dashboard_data()
        
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE!")
        print("=" * 60)
        print(f"Sentiment results: {sentiment_file}")
        print(f"Entity results: {entity_file}")
        print(f"Event results: {event_file}")
        print(f"Dashboard data: {dashboard_file}")
        
        print("\nNext steps:")
        print("1. Restart your API server: python src/api/saudi_api.py")
        print("2. Refresh your dashboard: streamlit run src/dashboard/saudi_dashboard.py")
        print("3. You'll now see:")
        print("   - Real Saudi company sentiment")
        print("   - Vision 2030 progress bars")
        print("   - Islamic finance alerts")
        print("   - 55.6% Saudi relevance score")

def main():
    processor = SaudiDataProcessor()
    processor.process_complete_pipeline()

if __name__ == "__main__":
    main()