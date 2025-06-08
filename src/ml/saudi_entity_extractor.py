import spacy
import json
from datetime import datetime
import os
from collections import Counter
import re

class SaudiFinancialEntityExtractor:
    def __init__(self):
        print("Loading Saudi-focused entity extractor...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError: # More specific exception for model loading issues
            print("Downloading spaCy model 'en_core_web_sm'...")
            # It's generally better to let users know if a script is about to run a system command.
            # Consider if this automatic download is desired in all contexts.
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            
        # --- Focused Change for Company Standardization ---
        # Map keyword variations to a single standard company name.
        self.company_keyword_to_standard_name_map = {
            # Keyword variations : Standard Name
            'aramco': 'Saudi Aramco',
            'saudi aramco': 'Saudi Aramco',
            'أرامكو': 'Saudi Aramco',
            'أرامكو السعودية': 'Saudi Aramco', # Added another Arabic variation

            'sabic': 'SABIC',
            'سابك': 'SABIC',

            'stc': 'STC',
            'saudi telecom': 'STC',
            'الاتصالات السعودية': 'STC',
            'saudi telecommunication company': 'STC',

            'al rajhi': 'Al Rajhi Bank',
            'rajhi bank': 'Al Rajhi Bank',
            'مصرف الراجحي': 'Al Rajhi Bank',
            'alrajhi bank': 'Al Rajhi Bank',

            'alinma': 'Alinma Bank',
            'alinma bank': 'Alinma Bank',
            'مصرف الإنماء': 'Alinma Bank',

            # Samba merged with SNB. Mapping Samba keywords to SNB for data accuracy.
            # If you prefer to keep Samba separate, you can define a 'Samba Financial Group' standard name.
            'samba': 'Saudi National Bank (SNB)',
            'samba financial': 'Saudi National Bank (SNB)',
            'سامبا': 'Saudi National Bank (SNB)',
            'snb': 'Saudi National Bank (SNB)',
            'saudi national bank': 'Saudi National Bank (SNB)',
            'البنك الأهلي': 'Saudi National Bank (SNB)', # Common name for SNB
            'البنك الأهلي السعودي': 'Saudi National Bank (SNB)',


            'riyad bank': 'Riyad Bank',
            'بنك الرياض': 'Riyad Bank',

            'maaden': 'Maaden',
            'معادن': 'Maaden',
            'saudi arabian mining company': 'Maaden',

            'almarai': 'Almarai',
            'المراعي': 'Almarai'
        }
        # This set will contain all keywords from the map above for efficient iteration.
        self.saudi_company_keywords_set = set(self.company_keyword_to_standard_name_map.keys())
        # --- End of Focused Change for Company Standardization ---
        
        # Other entity definitions from your original script
        # saudi regulators (kept as your original set structure)
        self.saudi_regulators = {
            'sama', 'saudi central bank', 'مؤسسة النقد', # Consider adding 'البنك المركزي السعودي'
            'cma', 'capital market authority', 'هيئة السوق المالية',
            'tadawul', 'saudi exchange', 'تداول' # Consider adding 'البورصة السعودية'
        }
        
        # islamic finance terms (kept as your original dict structure: eng_term -> ar_term)
        self.islamic_terms = {
            'sukuk': 'صكوك', # Also could mean 'islamic bond'
            'sharia': 'شريعة', # Also 'shari\'a'
            'zakat': 'زكاة',
            'riba': 'ربا', # Could relate to 'interest' in some contexts, be mindful
            'murabaha': 'مرابحة',
            'halal': 'حلال',
            'islamic banking': 'المصرفية الإسلامية', # Could include 'islamic finance'
            'sharia compliant': 'متوافق مع الشريعة'
            # Consider adding: Takaful, Mudarabah, Musharakah, Gharar, Ijarah
        }
        
        # vision 2030 keywords (kept as your original set structure)
        self.vision_2030_keywords = { # Renamed from vision_2030 to avoid conflict if it was a variable
            'vision 2030', 'رؤية 2030', # Consider 'saudi vision 2030', 'رؤية المملكة 2030'
            'neom', 'نيوم',
            'red sea project', 'مشروع البحر الأحمر', # Also 'the red sea', 'red sea global'
            'qiddiya', 'القدية',
            'saudi green initiative', 'مبادرة السعودية الخضراء'
            # Consider adding: Diriyah, ROSHN, The Line, Trojena, Oxagon
        }
        
        # uae entities for validation (kept as your original set structure)
        self.uae_entities = {
            'first abu dhabi bank', 'fab',
            'emirates nbd', 'enbd',
            'adcb', 'abu dhabi commercial bank',
            'adx', 'abu dhabi exchange',
            'dfm', 'dubai financial market'
        }

    def _is_arabic_keyword(self, keyword):
        """Helper function to check if a keyword contains Arabic characters."""
        return any('\u0600' <= char <= '\u06FF' for char in keyword)

    def extract_entities(self, text):
        # Ensure text is a non-empty string before processing
        if not isinstance(text, str) or not text.strip():
            # Return empty structure if input is invalid
            return {
                'organizations': [], 'locations': [], 'people': [], 'money': [],
                'islamic_finance': [], 'saudi_specific': [], 
                'regulators': [], 'vision_2030': []
            }

        doc = self.nlp(text)
        text_lower = text.lower()
        
        # Using your original entity dictionary structure and keys
        entities = {
            'organizations': [],
            'locations': [],
            'people': [],
            'money': [],
            'islamic_finance': [], # For Islamic finance terms
            'saudi_specific': [],  # For standardized Saudi company names
            'regulators': [],      # For Saudi regulators
            'vision_2030': []      # For Vision 2030 related keywords
        }
        
        # Standard NER (Named Entity Recognition) using spaCy
        for ent in doc.ents:
            ent_text_stripped = ent.text.strip()
            if not ent_text_stripped: continue # Skip if entity text is empty after stripping

            if ent.label_ == "ORG" and ent_text_stripped not in entities['organizations']:
                entities['organizations'].append(ent_text_stripped)
            elif ent.label_ in ["GPE", "LOC"] and ent_text_stripped not in entities['locations']:
                entities['locations'].append(ent_text_stripped)
            elif ent.label_ == "PERSON" and ent_text_stripped not in entities['people']:
                entities['people'].append(ent_text_stripped)
            elif ent.label_ == "MONEY" and ent_text_stripped not in entities['money']:
                entities['money'].append(ent_text_stripped)
        
        # --- Saudi Companies: Standardized Extraction ---
        # This set tracks standard names added in the current text to avoid list duplicates from multiple keywords.
        standard_company_names_found_this_text = set() 
        for keyword_variation in self.saudi_company_keywords_set:
            # Determine search context: original text for Arabic, lowercased for English.
            text_to_search = text if self._is_arabic_keyword(keyword_variation) else text_lower
            # Normalize keyword for search if it's not Arabic
            normalized_keyword_for_search = keyword_variation if self._is_arabic_keyword(keyword_variation) else keyword_variation.lower()

            if normalized_keyword_for_search in text_to_search:
                standard_name = self.company_keyword_to_standard_name_map.get(keyword_variation)
                if standard_name and standard_name not in standard_company_names_found_this_text:
                    entities['saudi_specific'].append(standard_name)
                    
                    # Add to 'organizations' if not already present or very similar.
                    # This helps consolidate, but care is needed to avoid near-duplicates.
                    is_similar_org_already_present = False
                    for org_in_list in entities['organizations']:
                        if standard_name.lower() in org_in_list.lower() or \
                           org_in_list.lower() in standard_name.lower():
                            is_similar_org_already_present = True
                            break
                    if not is_similar_org_already_present:
                        entities['organizations'].append(standard_name)
                    
                    standard_company_names_found_this_text.add(standard_name)
        # --- End of Saudi Companies Section ---
        
        # Islamic finance terms - using your original logic and self.islamic_terms
        # This ensures this part remains as you designed it.
        found_islamic_terms_this_text = set() # To avoid duplicates in the list for this text
        for eng_term, ar_term in self.islamic_terms.items():
            # Check English term in lowercased text
            if eng_term.lower() in text_lower and eng_term not in found_islamic_terms_this_text:
                entities['islamic_finance'].append(eng_term) # Storing the English key as per original logic
                found_islamic_terms_this_text.add(eng_term)
            # Check Arabic term in original text (if not already added via English term)
            elif ar_term in text and eng_term not in found_islamic_terms_this_text:
                entities['islamic_finance'].append(eng_term) # Still storing the English key
                found_islamic_terms_this_text.add(eng_term)
        
        # Saudi regulators - using your original logic and self.saudi_regulators
        found_regulators_this_text = set()
        for reg_keyword in self.saudi_regulators:
            text_to_search = text if self._is_arabic_keyword(reg_keyword) else text_lower
            normalized_keyword_for_search = reg_keyword if self._is_arabic_keyword(reg_keyword) else reg_keyword.lower()
            if normalized_keyword_for_search in text_to_search:
                # Using uppercased version of the keyword as per original logic
                reg_to_add = reg_keyword.upper() 
                if reg_to_add not in found_regulators_this_text:
                    entities['regulators'].append(reg_to_add)
                    found_regulators_this_text.add(reg_to_add)

        # Vision 2030 keywords - using your original logic and self.vision_2030_keywords
        found_vision2030_this_text = set()
        for v2030_keyword in self.vision_2030_keywords: # Iterating your original set
            text_to_search = text if self._is_arabic_keyword(v2030_keyword) else text_lower
            normalized_keyword_for_search = v2030_keyword if self._is_arabic_keyword(v2030_keyword) else v2030_keyword.lower()
            if normalized_keyword_for_search in text_to_search:
                # Using title-cased version as per original logic
                v2030_to_add = v2030_keyword.title() 
                if v2030_to_add not in found_vision2030_this_text:
                    entities['vision_2030'].append(v2030_to_add)
                    found_vision2030_this_text.add(v2030_to_add)
        
        # Enhanced money detection for Saudi context - using your original logic
        sar_pattern = r'(?:SAR|ريال)\s*[\d,]+(?:\.\d+)?(?:\s*(?:billion|million|مليار|مليون))?'
        sar_matches = re.findall(sar_pattern, text, re.IGNORECASE)
        for match_val in sar_matches: # Iterate through found raw matches
            if match_val not in entities['money']: # Add if not already present
                 entities['money'].append(match_val)
        
        # Remove duplicates from lists if any slipped through (e.g. from spaCy + custom)
        # by converting to set and back to list, then sorting for consistent output.
        for key in entities:
            entities[key] = sorted(list(set(entities[key])))

        return entities
    
    # The following methods (process_sentiment_results, print_saudi_summary, 
    # save_results, test_saudi_entity_extraction) are kept IDENTICAL 
    # to your last provided version of this script, as the core change 
    # was targeted at the entity definition and extraction logic above.

    def process_sentiment_results(self, sentiment_file):
        # This method should be exactly as you had it.
        # It loads the sentiment_file, iterates articles, calls self.extract_entities,
        # aggregates results for the summary, and calls print_saudi_summary.
        # The key 'saudi_specific' from extract_entities will now contain standardized names.
        
        # Ensuring file exists
        if not os.path.exists(sentiment_file):
            print(f"Error: Sentiment file not found at '{sentiment_file}'")
            return []
        try:
            with open(sentiment_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{sentiment_file}'")
            return []
        except Exception as e:
            print(f"An unexpected error occurred loading '{sentiment_file}': {e}")
            return []
            
        print(f"Extracting Saudi-focused entities from {len(articles)} articles (source: {sentiment_file})...")
        
        results = []
        # These lists will store mentions for the overall summary.
        # The Counter in print_saudi_summary will count occurrences from these lists.
        all_saudi_entities_mentions = []
        all_islamic_terms_mentions = []
        all_regulators_mentions = []
        # If you want to track Vision 2030 mentions for the summary too:
        all_vision2030_mentions = [] 
        
        for i, article in enumerate(articles):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i+1}/{len(articles)} articles for entities...")

            # Use title for entity extraction, as per your original script.
            # Consider expanding to description if available and relevant.
            text_for_entities = article.get('title', '')
            entities_found = self.extract_entities(text_for_entities)
            
            # Combine original article data (with sentiment) with the extracted entities
            article_with_entities = {
                **article, # Spreads all keys from the sentiment analysis output (title, sentiment, etc.)
                'entities': entities_found # Adds the new entities dictionary
            }
            results.append(article_with_entities)
            
            # Aggregate entities for the summary printout
            all_saudi_entities_mentions.extend(entities_found['saudi_specific'])
            all_islamic_terms_mentions.extend(entities_found['islamic_finance'])
            all_regulators_mentions.extend(entities_found['regulators'])
            all_vision2030_mentions.extend(entities_found['vision_2030']) # Add this if summarizing Vision 2030
            
        # Call the summary printing function
        self.print_saudi_summary(
            all_saudi_entities_mentions, 
            all_islamic_terms_mentions, 
            all_regulators_mentions, 
            results # Pass the full results list for context if needed by summary
        ) 
        # Note: If print_saudi_summary expects all_vision2030_mentions, add it here.
        # Your original print_saudi_summary didn't explicitly take Vision 2030 mentions.
        
        return results
    
    def print_saudi_summary(self, saudi_entities_list, islamic_terms_list, regulators_list, results_list_context):
        # This method should be exactly as you had it.
        # It uses Counter on the lists of mentions passed to it.
        print("\nSAUDI MARKET INTELLIGENCE")
        
        if saudi_entities_list:
            print("\nSaudi Companies Mentioned:")
            # Counter will sum up occurrences of each standard name
            for entity, count in Counter(saudi_entities_list).most_common():
                print(f"  {entity}: {count}")
        else:
            # Using a more professional tone for warnings, avoiding emojis.
            print("\nNotice: No Saudi companies detected in this data batch.")
            
        if islamic_terms_list:
            print("\nIslamic Finance Terms:")
            for term, count in Counter(islamic_terms_list).most_common():
                print(f"  {term}: {count}")
        else:
            print("\nNotice: No Islamic finance terms detected. This may be critical for Saudi market analysis.")
            
        if regulators_list:
            print("\nRegulatory Bodies:")
            for reg, count in Counter(regulators_list).most_common():
                print(f"  {reg}: {count}")
        # Removed the "else" for regulators as it might be common not to find them in all news.
                
        # Saudi market score - using your original calculation logic
        # This score is based on total mentions, not unique articles with entities.
        saudi_score_val = len(saudi_entities_list) + len(islamic_terms_list) + len(regulators_list)
        total_articles_val = len(results_list_context)
        
        print(f"\nSaudi Relevance Score (based on total mentions): {saudi_score_val} mentions in {total_articles_val} articles.")
        if total_articles_val > 0 and saudi_score_val / total_articles_val < 0.5 : # Example: less than 0.5 mentions per article average
            print("Notice: Low density of Saudi-specific mentions. Consider data source or keyword review for deeper Saudi relevance.")
    
    def save_results(self, results_to_save, output_file=None): # Renamed parameters for clarity
        # This method should be exactly as you had it.
        if not results_to_save:
            print("No entity results to save.")
            return None

        if output_file is None:
            processed_dir = 'data/processed'
            os.makedirs(processed_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(processed_dir, f"saudi_entities_{timestamp}.json")
            
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_to_save, f, ensure_ascii=False, indent=2)
            print(f"\nSaved Saudi entity extraction to: {output_file}")
            return output_file
        except IOError as e:
            print(f"Error saving entity results to {output_file}: {e}")
            return None

def test_saudi_entity_extraction():
    # This method should be exactly as you had it for your testing purposes.
    # It will use the updated extractor logic.
    print("--- Initiating Test for SaudiFinancialEntityExtractor ---")
    extractor = SaudiFinancialEntityExtractor()
    
    processed_data_dir = 'data/processed'
    # Ensure processed directory exists for test outputs or dummy inputs
    if not os.path.exists(processed_data_dir):
        os.makedirs(processed_data_dir)

    # Attempt to find the latest sentiment file for a realistic test
    sentiment_input_files = []
    if os.path.exists(processed_data_dir):
        sentiment_input_files = sorted(
            [os.path.join(processed_data_dir, f) for f in os.listdir(processed_data_dir) if f.startswith('sentiment_') and f.endswith('.json')],
            key=os.path.getmtime,
            reverse=True
        )
    
    input_file_for_test = None
    if sentiment_input_files:
        input_file_for_test = sentiment_input_files[0]
        print(f"Using latest sentiment file for test: {input_file_for_test}")
    else:
        # Create a dummy sentiment file if no real one is found, for standalone testing
        print("No existing sentiment files found. Creating a dummy input file for testing.")
        input_file_for_test = os.path.join(processed_data_dir, "test_dummy_sentiment_data.json")
        dummy_data_for_test = [
            {"title": "Saudi Aramco and Aramco discuss NEOM. SABIC sukuk is Sharia compliant.", "source": "Test Feed", "url": "http://test.com/a1", "sentiment": "positive", "sentiment_score": 0.88, "analyzed_at": datetime.now().isoformat()},
            {"title": "Al Rajhi Bank and SAMA talk Vision 2030.", "source": "Test Feed", "url": "http://test.com/a2", "sentiment": "neutral", "sentiment_score": 0.6, "analyzed_at": datetime.now().isoformat()}
        ]
        try:
            with open(input_file_for_test, 'w', encoding='utf-8') as f_dummy:
                json.dump(dummy_data_for_test, f_dummy, indent=2)
        except IOError:
            print(f"Failed to create dummy test input file at: {input_file_for_test}")
            return # Cannot proceed with test
        
    extracted_results = extractor.process_sentiment_results(input_file_for_test)
    
    if extracted_results:
        test_output_path = os.path.join(processed_data_dir, f"test_run_saudi_entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        extractor.save_results(extracted_results, test_output_path)
    
        # Displaying entities from the first article in the test results for quick verification
        if extracted_results and extracted_results[0].get('entities'):
            print("\nExample Entities from First Test Article:")
            first_article_entities = extracted_results[0]['entities']
            for entity_category, entity_values in first_article_entities.items():
                if entity_values: # Only print if category has entities
                    print(f"  {entity_category.replace('_', ' ').title()}: {entity_values}")
    else:
        print("No results were produced by entity extraction during the test run.")
    print("--- Entity Extractor Test Concluded ---")

if __name__ == "__main__":
    test_saudi_entity_extraction()