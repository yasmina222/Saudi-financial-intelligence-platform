import json
import re
import os
from datetime import datetime
from collections import Counter

class SaudiEventDetector:
    def __init__(self):
        print("Initializing Saudi Event Detection...")
        
        # standard financial events
        self.generic_events = {
            'merger': ['merge', 'acquisition', 'acquire', 'takeover'],
            'ipo': ['ipo', 'initial public offering', 'going public'],
            'earnings': ['earnings', 'profit', 'loss', 'revenue'],
            'regulatory': ['fine', 'penalty', 'compliance', 'violation']
        }
        
        # saudi-specific events 
        self.saudi_events = {
            'sukuk_issuance': ['sukuk', 'islamic bond', 'صكوك'],
            'sharia_ruling': ['sharia', 'fatwa', 'halal', 'شريعة', 'فتوى'],
            'vision_2030': ['vision 2030', 'neom', 'red sea project', 'رؤية ٢٠٣٠'],
            'oil_update': ['opec', 'oil price', 'crude', 'barrel'],
            'saudi_regulation': ['sama', 'cma', 'tadawul rule', 'هيئة السوق'],
            # added: Giga-projects (critical for construction/banking sectors)
            'giga_projects': [
                'qiddiya', 'the line', 'oxagon', 'trojena', 'sindala',
                'القدية', 'ذا لاين', 'أوكساجون', 'تروجينا', 'سندالة',
                'neom bay', 'amaala', 'diriyah gate', 'roshn'
            ],
            # Interest rate decisions (moves bank stocks immediately)
            'interest_rates': [
                'سعر الفائدة', 'repo rate', 'sama rate decision',
                'reverse repo', 'معدل الريبو', 'قرار ساما'
            ]
        }
        
        # critical islamic finance events (ENHANCED)
        self.islamic_alerts = {
            'riba_concern': ['riba', 'interest rate', 'ربا'],
            'zakat_announcement': ['zakat', 'زكاة'],
            'shariah_compliance': ['shariah compliant', 'shariah board', 'متوافق مع الشريعة'],
            # NEW: Sukuk defaults (market panic trigger)
            'sukuk_default': [
                'sukuk default', 'تخلف عن سداد الصكوك',
                'تأخر السداد', 'missed payment', 'إعادة هيكلة الصكوك'
            ]
        }
        
        # Priority scoring for Saudi banks
        self.event_priority = {
            'interest_rates': 10,      # Immediate bank impact
            'sukuk_default': 9,        # Credit risk alert
            'saudi_regulation': 8,     # Compliance critical
            'giga_projects': 7,        # Lending opportunities
            'oil_update': 6,           # Economy-wide impact
            'vision_2030': 5           # Long-term strategic
        }
        
    def detect_events(self, text):
        text_lower = text.lower()
        detected_events = {
            'generic': [],
            'saudi_specific': [],
            'islamic_alerts': [],
            'event_importance': 'low',
            'priority_score': 0
        }
        
        # check generic events
        for event_type, keywords in self.generic_events.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_events['generic'].append(event_type)
                    break
                    
        # check saudi events with priority scoring
        for event_type, keywords in self.saudi_events.items():
            for keyword in keywords:
                if keyword in text_lower or keyword in text:
                    detected_events['saudi_specific'].append(event_type)
                    detected_events['event_importance'] = 'high'
                    # add priority score
                    detected_events['priority_score'] += self.event_priority.get(event_type, 1)
                    break
                    
        # check islamic alerts
        for alert_type, keywords in self.islamic_alerts.items():
            for keyword in keywords:
                if keyword in text_lower or keyword in text:
                    detected_events['islamic_alerts'].append(alert_type)
                    detected_events['event_importance'] = 'critical'
                    # sukuk defaults get highest priority
                    if alert_type == 'sukuk_default':
                        detected_events['priority_score'] += 10
                    break
                    
        return detected_events
    
    def process_entity_results(self, entity_file):
        with open(entity_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
            
        print(f"Detecting Saudi events in {len(articles)} articles...")
        
        results = []
        event_counts = {
            'generic': Counter(),
            'saudi_specific': Counter(),
            'islamic_alerts': Counter()
        }
        
        high_priority_articles = []
        
        for article in articles:
            events = self.detect_events(article['title'])
            
            # combine with existing data
            result = {
                **article,
                'events': events
            }
            results.append(result)
            
            # count events
            for event in events['generic']:
                event_counts['generic'][event] += 1
            for event in events['saudi_specific']:
                event_counts['saudi_specific'][event] += 1
            for event in events['islamic_alerts']:
                event_counts['islamic_alerts'][event] += 1
                
            # track high priority (score > 5)
            if events['priority_score'] >= 5:
                high_priority_articles.append(result)
                
        # sort by priority
        high_priority_articles.sort(key=lambda x: x['events']['priority_score'], reverse=True)
                
        self.print_event_summary(event_counts, high_priority_articles)
        
        return results
    
    def print_event_summary(self, event_counts, high_priority):
        print("\nSAUDI EVENT DETECTION SUMMARY")
        
        print("\nGeneric Financial Events:")
        for event, count in event_counts['generic'].most_common():
            print(f"  {event}: {count}")
            
        if event_counts['saudi_specific']:
            print("\nSaudi-Specific Events:")
            for event, count in event_counts['saudi_specific'].most_common():
                print(f"  {event}: {count}")
                # show priority
                priority = self.event_priority.get(event, 1)
                print(f"    Priority Level: {priority}/10")
        else:
            print("\nNo Saudi-specific events detected!")
            print("Missing: Interest rate decisions, giga-projects, oil updates")
            
        if event_counts['islamic_alerts']:
            print("\nIslamic Finance Alerts:")
            for alert, count in event_counts['islamic_alerts'].most_common():
                print(f"  {alert}: {count}")
                if alert == 'sukuk_default':
                    print("    >>> CRITICAL: Sukuk default detected!")
                
        print(f"\nHigh Priority Articles: {len(high_priority)}")
        
        if high_priority:
            print("\nTop 3 Priority Articles for Saudi Banks:")
            for i, article in enumerate(high_priority[:3], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Priority Score: {article['events']['priority_score']}")
                print(f"   Events: {article['events']['saudi_specific'] + article['events']['islamic_alerts']}")
                print(f"   Sentiment: {article['sentiment']} ({article['sentiment_score']})")
        else:
            print("\nNo high-priority Saudi banking events detected.")
            print("This confirms need for SAMA announcements & Tadawul feeds")
    
    def generate_bank_alerts(self, results):
        # simulate real-time alerts for Saudi banks
        alerts = []
        
        for article in results:
            if 'interest_rates' in article['events']['saudi_specific']:
                alerts.append({
                    'type': 'RATE_ALERT',
                    'message': f"SAMA rate decision detected: {article['title']}",
                    'action': 'Review loan portfolio pricing'
                })
            elif 'sukuk_default' in article['events']['islamic_alerts']:
                alerts.append({
                    'type': 'CREDIT_RISK',
                    'message': f"Sukuk default alert: {article['title']}",
                    'action': 'Immediate credit exposure review'
                })
            elif 'giga_projects' in article['events']['saudi_specific']:
                alerts.append({
                    'type': 'OPPORTUNITY',
                    'message': f"Giga-project update: {article['title']}",
                    'action': 'Assess project finance opportunities'
                })
                
        return alerts
    
    def save_results(self, results):
        output_file = f"data/processed/saudi_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"\nSaved Saudi event detection to: {output_file}")
        return output_file

def test_saudi_events():
    detector = SaudiEventDetector()
    
    # get latest entity file
    entity_files = sorted([f for f in os.listdir('data/processed') if f.startswith('saudi_entities_')])
    if not entity_files:
        print("No entity files found. Run entity extraction first.")
        return
        
    latest_entities = os.path.join('data/processed', entity_files[-1])
    print(f"Using entity file: {latest_entities}")
    
    results = detector.process_entity_results(latest_entities)
    
    # generate bank alerts
    alerts = detector.generate_bank_alerts(results)
    if alerts:
        print("\nSAUDI BANK ACTION ALERTS")
        for alert in alerts:
            print(f"\n[{alert['type']}] {alert['message']}")
            print(f"ACTION REQUIRED: {alert['action']}")
    else:
        print("\nNo actionable alerts for Saudi banks in current data.")
        
    output_file = detector.save_results(results)

if __name__ == "__main__":
    test_saudi_events()