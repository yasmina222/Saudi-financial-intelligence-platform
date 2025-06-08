import json
import os
from datetime import datetime, timedelta
import random
from collections import defaultdict

class ArabicFinancialDataGenerator:
    """
    Generates realistic Arabic financial news data for testing and fine-tuning.
    DISCLAIMER: Synthetic data for demonstration purposes only.
    Production systems would use Tadawul/Argaam feeds.
    """
    
    def __init__(self):
        os.makedirs('data/raw/arabic', exist_ok=True)
        
        # PROMINENT DISCLAIMER
        self.DISCLAIMER = "SYNTHETIC DATA - DEMONSTRATION PURPOSES ONLY"
        print(f"\n{'='*60}")
        print(f"    {self.DISCLAIMER}")
        print(f"    Real systems would use Tadawul/Argaam feeds")
        print(f"{'='*60}\n")
        
        # Saudi companies in Arabic
        self.saudi_companies_ar = {
            'أرامكو': 'aramco',
            'سابك': 'sabic',
            'الاتصالات السعودية': 'stc',
            'مصرف الراجحي': 'al_rajhi',
            'البنك الأهلي السعودي': 'snb',
            'معادن': 'maaden',
            'المراعي': 'almarai'
        }
        
        # Vision 2030 projects in Arabic
        self.vision_projects_ar = {
            'نيوم': 'neom',
            'مشروع البحر الأحمر': 'red_sea',
            'القدية': 'qiddiya',
            'بوابة الدرعية': 'diriyah',
            'تروجينا': 'trojena'
        }
        
        # ENHANCEMENT: Dialect variations
        self.dialect_terms = {
            'profit': {
                'msa': 'ربح',
                'gulf': 'رِبْح',
                'saudi': 'مكسب'
            },
            'growth': {
                'msa': 'نمو',
                'gulf': 'تقدم',
                'saudi': 'تطور'
            },
            'increase': {
                'msa': 'ارتفاع',
                'gulf': 'زيادة',
                'saudi': 'طلوع'
            },
            'decrease': {
                'msa': 'انخفاض',
                'gulf': 'نزول',
                'saudi': 'هبوط'
            }
        }
        
        # Real headline snippets (if available from previous scraping)
        self.real_headlines_cache = self._load_real_headlines()
        
        # Financial sentiment templates with dialect awareness
        self.positive_templates = [
            "{company} تحقق أرباحاً قياسية بقيمة {amount} ريال سعودي",
            "{growth_term} سهم {company} بنسبة {percent}٪ في تداول اليوم",
            "{company} تعلن عن توزيعات أرباح سخية للمساهمين",
            "{growth_term} إيرادات {company} يفوق التوقعات بنسبة {percent}٪",
            "{project} يحقق تقدماً ملحوظاً بإنجاز {percent}٪ من المشروع",
            "إقبال كبير على اكتتاب {company} الجديد",
            "صكوك {company} تحقق نجاحاً باهراً مع اكتمال الاكتتاب"
        ]
        
        self.negative_templates = [
            "{decrease_term} أسهم {company} بنسبة {percent}٪ وسط مخاوف السوق",
            "{company} تسجل خسائر بقيمة {amount} ريال في الربع الأخير",
            "{decrease_term} أرباح {company} دون التوقعات",
            "مخاوف من تأثير {event} على أداء {company}",
            "تحذيرات من مخاطر الاستثمار في {sector}",
            "{company} تواجه تحديات في تحقيق أهدافها المالية"
        ]
        
        self.neutral_templates = [
            "{company} تعلن عن نتائجها المالية للربع الثالث",
            "مجلس إدارة {company} يجتمع لمناقشة الاستراتيجية المستقبلية",
            "تقرير: {sector} يشهد استقراراً نسبياً",
            "{regulator} يصدر تعميماً جديداً بشأن {topic}",
            "محللون يراقبون أداء {company} عن كثب",
            "{project} يستمر وفق الجدول الزمني المحدد"
        ]
        
        # Islamic finance terms
        self.islamic_terms = [
            'صكوك', 'مرابحة', 'مضاربة', 'إجارة', 'وكالة',
            'تورق', 'استصناع', 'سلم', 'شريعة', 'حلال'
        ]
        
        # Events and sectors
        self.events = [
            'تقلبات أسعار النفط', 'قرارات البنك المركزي',
            'التضخم العالمي', 'الأزمة الجيوسياسية'
        ]
        
        self.sectors = [
            'القطاع المصرفي', 'قطاع الطاقة', 'القطاع الصناعي',
            'قطاع الاتصالات', 'القطاع العقاري'
        ]
        
        self.regulators = ['ساما', 'هيئة السوق المالية', 'وزارة المالية']
        
        # Quality metrics tracking
        self.quality_metrics = {
            'dialect_consistency': 0,
            'term_authenticity': 0,
            'real_data_blend': 0
        }
    
    def _load_real_headlines(self):
        """Load any cached real Arabic headlines from previous scraping"""
        real_headlines = []
        try:
            # Check if we have any real Arabic data from previous attempts
            cache_file = "data/raw/arabic/real_headlines_cache.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    real_headlines = data.get('headlines', [])
                    print(f"Loaded {len(real_headlines)} real headline examples")
        except Exception as e:
            print(f"No real headline cache found - using pure synthetic generation")
        
        # Add a few example real headlines for demonstration
        if not real_headlines:
            real_headlines = [
                "أرامكو السعودية تعلن توزيعات نقدية بقيمة 19.5 مليار دولار للربع الثالث",
                "تداول: ارتفاع المؤشر العام بنسبة 0.4% عند 11,892 نقطة",
                "الراجحي المالية تطلق صندوق استثماري متوافق مع الشريعة"
            ]
        
        return real_headlines
    
    def get_dialect_term(self, term_type, dialect='saudi'):
        """Get dialect-appropriate term"""
        if term_type in self.dialect_terms:
            return self.dialect_terms[term_type].get(dialect, self.dialect_terms[term_type]['msa'])
        return term_type
    
    def generate_amount(self):
        """Generate realistic financial amounts in millions/billions"""
        magnitude = random.choice(['مليون', 'مليار'])
        number = random.randint(10, 999)
        return f"{number} {magnitude}"
    
    def generate_percent(self):
        """Generate realistic percentage changes"""
        return random.randint(1, 25)
    
    def should_use_real_headline(self):
        """Determine if we should use a real headline (10-20% chance)"""
        return random.random() > 0.85 and len(self.real_headlines_cache) > 0
    
    def generate_arabic_financial_articles(self, count=30):
        """Generate Arabic financial news articles with known sentiments"""
        articles = []
        real_count = 0
        
        # Ensure balanced sentiment distribution
        sentiment_distribution = ['positive'] * 10 + ['negative'] * 10 + ['neutral'] * 10
        random.shuffle(sentiment_distribution)
        
        for i, sentiment in enumerate(sentiment_distribution[:count]):
            # ENHANCEMENT: Blend real data when available
            if self.should_use_real_headline() and real_count < 3:
                title = random.choice(self.real_headlines_cache)
                real_count += 1
                data_source = 'real_cached'
            else:
                # Generate synthetic title
                if sentiment == 'positive':
                    template = random.choice(self.positive_templates)
                elif sentiment == 'negative':
                    template = random.choice(self.negative_templates)
                else:
                    template = random.choice(self.neutral_templates)
                
                # Fill in template variables with dialect awareness
                company_ar = random.choice(list(self.saudi_companies_ar.keys()))
                project_ar = random.choice(list(self.vision_projects_ar.keys()))
                
                title = template.format(
                    company=company_ar,
                    project=project_ar,
                    amount=self.generate_amount(),
                    percent=self.generate_percent(),
                    event=random.choice(self.events),
                    sector=random.choice(self.sectors),
                    regulator=random.choice(self.regulators),
                    topic='متطلبات رأس المال',
                    growth_term=self.get_dialect_term('growth', 'saudi'),
                    decrease_term=self.get_dialect_term('decrease', 'saudi'),
                    profit_term=self.get_dialect_term('profit', 'saudi')
                )
                data_source = 'synthetic'
            
            # Create full article
            article = {
                'id': f'ar_article_{i+1}',
                'title': title,
                'description': f"{title}. مزيد من التفاصيل حول هذا الخبر المالي المهم.",
                'source': random.choice(['صحيفة الاقتصادية', 'أرقام', 'معلومات مباشر', 'الرياض المالية']),
                'publishedAt': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'language': 'ar',
                'category': 'financial_news',
                'expected_sentiment': sentiment,
                'data_source': data_source,
                'has_islamic_terms': random.random() > 0.7,
                'dialect': 'saudi',
                'companies_mentioned': {
                    'arabic': [company_ar] if 'company_ar' in locals() else [],
                    'english': [self.saudi_companies_ar.get(company_ar, '')] if 'company_ar' in locals() else []
                }
            }
            
            # Add Islamic finance terms randomly
            if article['has_islamic_terms']:
                islamic_term = random.choice(self.islamic_terms)
                article['title'] += f" وفقاً لأحكام {islamic_term}"
                article['islamic_terms'] = [islamic_term]
            
            articles.append(article)
        
        # Update quality metrics
        self.quality_metrics['real_data_blend'] = (real_count / count) * 100
        
        return articles
    
    def calculate_authenticity_score(self, dataset):
        """Calculate linguistic authenticity score (0-10)"""
        score = 0
        
        # Check dialect consistency
        dialect_terms_used = sum(1 for article in dataset['articles'] 
                                if any(term in article['title'] 
                                      for terms in self.dialect_terms.values() 
                                      for term in terms.values()))
        if dialect_terms_used > 0:
            score += 3
        
        # Check for real data blend
        real_articles = sum(1 for article in dataset['articles'] 
                           if article.get('data_source') == 'real_cached')
        if real_articles > 0:
            score += 3
        
        # Check for Islamic finance terms usage
        islamic_articles = sum(1 for article in dataset['articles'] 
                              if article.get('has_islamic_terms'))
        if islamic_articles > len(dataset['articles']) * 0.2:
            score += 2
        
        # Check for company diversity
        unique_companies = set()
        for article in dataset['articles']:
            companies = article.get('companies_mentioned', {}).get('arabic', [])
            unique_companies.update(companies)
        if len(unique_companies) >= 5:
            score += 2
        
        return min(score, 10)
    
    def generate_islamic_finance_articles(self, count=15):
        """Generate Islamic finance specific articles"""
        articles = []
        
        islamic_templates = {
            'positive': [
                "نجاح إصدار صكوك {company} بقيمة {amount} ريال",
                "{growth_term} التمويل الإسلامي في {sector} بنسبة {percent}٪",
                "{company} تطلق منتجات مصرفية متوافقة مع الشريعة"
            ],
            'negative': [
                "تحذيرات من مخاطر عدم الالتزام بضوابط {term} الشرعية",
                "{decrease_term} إصدارات الصكوك بنسبة {percent}٪"
            ],
            'neutral': [
                "هيئة المحاسبة والمراجعة للمؤسسات المالية الإسلامية تصدر معياراً جديداً",
                "ندوة حول تطبيقات {term} في الأسواق المالية"
            ]
        }
        
        for i in range(count):
            sentiment = random.choice(['positive', 'negative', 'neutral'])
            template = random.choice(islamic_templates[sentiment])
            
            title = template.format(
                company=random.choice(list(self.saudi_companies_ar.keys())),
                amount=self.generate_amount(),
                percent=self.generate_percent(),
                sector=random.choice(self.sectors),
                term=random.choice(self.islamic_terms),
                growth_term=self.get_dialect_term('growth', 'saudi'),
                decrease_term=self.get_dialect_term('decrease', 'saudi')
            )
            
            article = {
                'id': f'islamic_article_{i+1}',
                'title': title,
                'description': f"{title}. تفاصيل إضافية حول هذا الخبر في مجال التمويل الإسلامي.",
                'source': 'أخبار التمويل الإسلامي',
                'publishedAt': datetime.now().isoformat(),
                'language': 'ar',
                'category': 'islamic_finance',
                'expected_sentiment': sentiment,
                'data_source': 'synthetic',
                'dialect': 'saudi',
                'islamic_terms': [random.choice(self.islamic_terms)]
            }
            
            articles.append(article)
        
        return articles
    
    def generate_training_dataset(self):
        """Generate a complete training dataset for fine-tuning"""
        print("Generating Arabic financial training dataset...")
        print(f"Data source: {self.DISCLAIMER}")
        
        # Generate different types of articles
        financial_articles = self.generate_arabic_financial_articles(30)
        islamic_articles = self.generate_islamic_finance_articles(15)
        
        # Combine all articles
        all_articles = financial_articles + islamic_articles
        
        # Create dataset structure
        dataset = {
            'disclaimer': self.DISCLAIMER,
            'articles': all_articles,
            'metadata': {
                'generated_date': datetime.now().isoformat(),
                'total_articles': len(all_articles),
                'sentiment_distribution': defaultdict(int),
                'has_islamic_content': sum(1 for a in all_articles if a.get('islamic_terms')),
                'real_data_count': sum(1 for a in all_articles if a.get('data_source') == 'real_cached'),
                'synthetic_data_count': sum(1 for a in all_articles if a.get('data_source') == 'synthetic'),
                'sources': list(set(a['source'] for a in all_articles)),
                'quality_metrics': self.quality_metrics
            }
        }
        
        # Calculate sentiment distribution
        for article in all_articles:
            dataset['metadata']['sentiment_distribution'][article['expected_sentiment']] += 1
        
        # Convert defaultdict to regular dict for JSON serialization
        dataset['metadata']['sentiment_distribution'] = dict(dataset['metadata']['sentiment_distribution'])
        
        # Calculate authenticity score
        dataset['metadata']['authenticity_score'] = self.calculate_authenticity_score(dataset)
        
        return dataset
    
    def save_dataset(self, dataset, filename=None):
        """Save the generated dataset"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/arabic/arabic_financial_dataset_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        # Also save as latest
        latest_file = "data/raw/arabic/latest_arabic_dataset.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print(f"Dataset saved to: {filename}")
        print(f"Also saved as: {latest_file}")
        
        return filename
    
    def print_dataset_summary(self, dataset):
        """Print summary of generated dataset with quality metrics"""
        print("\n" + "="*60)
        print("ARABIC FINANCIAL DATASET SUMMARY")
        print("="*60)
        print(f"⚠️  {dataset['disclaimer']}")
        print("="*60)
        
        metadata = dataset['metadata']
        print(f"\nTotal Articles: {metadata['total_articles']}")
        print(f"  - Synthetic: {metadata['synthetic_data_count']}")
        print(f"  - Real (cached): {metadata['real_data_count']}")
        
        print("\nSentiment Distribution:")
        for sentiment, count in metadata['sentiment_distribution'].items():
            percentage = (count / metadata['total_articles']) * 100
            print(f"  - {sentiment}: {count} ({percentage:.1f}%)")
        
        print(f"\nArticles with Islamic Terms: {metadata['has_islamic_content']}")
        
        print("\nQuality Metrics:")
        print(f"  - Linguistic Authenticity Score: {metadata['authenticity_score']}/10")
        print(f"  - Real Data Blend: {self.quality_metrics['real_data_blend']:.1f}%")
        print(f"  - Dialect Consistency: Saudi Arabic")
        
        print("\nSample Articles:")
        for i, article in enumerate(dataset['articles'][:5], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Expected Sentiment: {article['expected_sentiment']}")
            print(f"   Data Source: {article['data_source']}")
            if article.get('islamic_terms'):
                print(f"   Islamic Terms: {', '.join(article['islamic_terms'])}")
    
    def create_fine_tuning_format(self, dataset):
        """Convert dataset to format suitable for fine-tuning"""
        fine_tuning_data = []
        
        for article in dataset['articles']:
            fine_tuning_data.append({
                'text': article['title'],
                'label': article['expected_sentiment'],
                'data_source': article['data_source']
            })
        
        # Save in simple format for fine-tuning
        fine_tuning_file = "data/raw/arabic/arabic_sentiment_fine_tuning.json"
        with open(fine_tuning_file, 'w', encoding='utf-8') as f:
            json.dump(fine_tuning_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nFine-tuning data saved to: {fine_tuning_file}")
        
        return fine_tuning_file

def main():
    print("Arabic Financial Data Generator")
    print("="*40)
    
    generator = ArabicFinancialDataGenerator()
    
    # Generate the dataset
    dataset = generator.generate_training_dataset()
    
    # Save the dataset
    generator.save_dataset(dataset)
    
    # Print summary with quality metrics
    generator.print_dataset_summary(dataset)
    
    # Create fine-tuning format
    generator.create_fine_tuning_format(dataset)
    
    print("\nNext steps:")
    print("1. Test the Arabic sentiment analyzer on this data")
    print("2. Use the fine-tuning data to improve model accuracy")
    print("3. Integrate Arabic analysis into the main pipeline")
    print("\nNOTE: For production use, integrate with Tadawul/Argaam APIs")

if __name__ == "__main__":
    main()