from transformers import pipeline, AutoTokenizer
import json
from datetime import datetime
import os

class FinancialSentimentAnalyzer:
    def __init__(self):
        print("Loading FinBERT...")
        self.classifier = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            device=-1
        )
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        
    def analyze_text(self, text):
        # finbert max tokens = 512
        tokens = self.tokenizer.encode(text, truncation=True, max_length=512)
        truncated_text = self.tokenizer.decode(tokens, skip_special_tokens=True)
        
        result = self.classifier(truncated_text)[0]
        
        return {
            'label': result['label'].lower(),
            'score': round(result['score'], 4),
            'confidence': 'high' if result['score'] > 0.7 else 'low'
        }
    
    def analyze_articles(self, articles_file):
        with open(articles_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
            
        print(f"Processing {len(articles)} articles")
        
        results = []
        for i, article in enumerate(articles):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(articles)}")
            
            title_sentiment = self.analyze_text(article['title'])
            
            results.append({
                'title': article['title'],
                'source': article['source'],
                'url': article['url'],
                'sentiment': title_sentiment['label'],
                'sentiment_score': title_sentiment['score'],
                'confidence': title_sentiment['confidence'],
                'analyzed_at': datetime.now().isoformat()
            })
            
        return results
    
    def save_results(self, results, output_file=None):
        if not output_file:
            output_file = f"data/processed/sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        os.makedirs('data/processed', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        return output_file
    
    def print_summary(self, results):
        total = len(results)
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for result in results:
            sentiments[result['sentiment']] += 1
            
        print(f"\nTotal: {total}")
        for sentiment, count in sentiments.items():
            print(f"{sentiment}: {count} ({count/total*100:.1f}%)")
        
        # show a couple examples
        for sentiment in ['positive', 'negative']:
            examples = [r for r in results if r['sentiment'] == sentiment][:2]
            if examples:
                print(f"\n{sentiment}:")
                for ex in examples:
                    print(f"  {ex['title'][:70]}...")

def test_sentiment_analyzer():
    analyzer = FinancialSentimentAnalyzer()
    
    # grab latest news file
    news_files = sorted([f for f in os.listdir('data/raw') if f.startswith('news_') and f.endswith('.json')])
    if not news_files:
        print("No news files found")
        return
        
    latest_file = os.path.join('data/raw', news_files[-1])
    print(f"Using: {latest_file}")
    
    results = analyzer.analyze_articles(latest_file)
    output_file = analyzer.save_results(results)
    analyzer.print_summary(results)
    
    print(f"\nOutput: {output_file}")

if __name__ == "__main__":
    test_sentiment_analyzer()