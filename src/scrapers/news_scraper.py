import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import os

class FinancialNewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        os.makedirs('data/raw', exist_ok=True)
        
    def scrape_arab_news_economy(self):
        """Scrape Arab News Economy section"""
        url = "https://www.arabnews.com/economy"
        articles = []
        
        print("Fetching Arab News Economy...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                article_count = 0
                
                for link in soup.find_all('a', href=True):
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if (len(text) > 20 and 
                        '/node/' in href and 
                        article_count < 15):
                        
                        full_url = f"https://www.arabnews.com{href}" if not href.startswith('http') else href
                        
                        if not any(a['url'] == full_url for a in articles):
                            articles.append({
                                'title': text,
                                'url': full_url,
                                'source': 'Arab News',
                                'timestamp': datetime.now().isoformat(),
                                'category': 'economy'
                            })
                            article_count += 1
                
                print(f"Found {len(articles)} articles from Arab News")
                        
        except Exception as e:
            print(f"Error: {e}")
            
        return articles
    
    def scrape_financial_times_middle_east(self):
        """Get FT Middle East headlines via RSS"""
        articles = []
        url = "https://news.google.com/rss/search?q=site:ft.com+Middle+East+finance&hl=en"
        
        print("Fetching Financial Times (via Google News RSS)...")
        
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'lxml-xml')
            
            for item in soup.find_all('item')[:10]:
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                if title and link:
                    articles.append({
                        'title': title.text.split(' - ')[0],
                        'url': link.text,
                        'source': 'Financial Times',
                        'publishedAt': pub_date.text if pub_date else '',
                        'timestamp': datetime.now().isoformat(),
                        'category': 'middle_east_finance'
                    })
                    
            print(f"Found {len(articles)} articles from Financial Times")
                    
        except Exception as e:
            print(f"Error with FT: {e}")
            
        return articles
    
    def scrape_bloomberg_middle_east(self):
        """Get Bloomberg Middle East content via RSS"""
        articles = []
        url = "https://news.google.com/rss/search?q=site:bloomberg.com+Saudi+UAE+finance&hl=en"
        
        print("Fetching Bloomberg Middle East...")
        
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'lxml-xml')
            
            for item in soup.find_all('item')[:10]:
                title = item.find('title')
                link = item.find('link')
                
                if title and link:
                    articles.append({
                        'title': title.text.split(' - ')[0],
                        'url': link.text,
                        'source': 'Bloomberg',
                        'timestamp': datetime.now().isoformat(),
                        'category': 'middle_east_finance'
                    })
                    
            print(f"Found {len(articles)} articles from Bloomberg")
                    
        except Exception as e:
            print(f"Error with Bloomberg: {e}")
            
        return articles
    
    def scrape_all_sources(self):
        """Scrape all available sources"""
        all_articles = []
        
        sources = [
            self.scrape_arab_news_economy,
            self.scrape_financial_times_middle_east,
            self.scrape_bloomberg_middle_east
        ]
        
        for scraper_func in sources:
            try:
                articles = scraper_func()
                all_articles.extend(articles)
                time.sleep(1)
            except Exception as e:
                print(f"Error with {scraper_func.__name__}: {e}")
                
        return all_articles
    
    def save_articles(self, articles):
        """Save articles to JSON file"""
        filename = f"data/raw/news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
            
        print(f"\nSaved {len(articles)} articles to {filename}")
        print(f"File size: {os.path.getsize(filename):,} bytes")
        
        return filename
    
    def test_scraper(self):
        """Test all scrapers"""
        print("Starting Financial News Scraper...\n")
        
        articles = self.scrape_all_sources()
        
        if articles:
            print(f"\nTotal articles found: {len(articles)}")
            
            # Show breakdown by source
            sources = {}
            for article in articles:
                source = article['source']
                sources[source] = sources.get(source, 0) + 1
                
            print("\nArticles by source:")
            for source, count in sources.items():
                print(f"  - {source}: {count}")
            
            print("\nSample articles:")
            for i, article in enumerate(articles[:5], 1):
                print(f"\n{i}. {article['title'][:80]}...")
                print(f"   Source: {article['source']}")
            
            filename = self.save_articles(articles)
            
            if os.path.exists(filename):
                print(f"\nSuccess! Articles saved to: {filename}")
                
                # Show first article as sample
                with open(filename, 'r') as f:
                    data = json.load(f)
                    if data:
                        print("\nFirst article details:")
                        print(json.dumps(data[0], indent=2))
            
        else:
            print("\nNo articles found from any source")

if __name__ == "__main__":
    scraper = FinancialNewsScraper()
    scraper.test_scraper()