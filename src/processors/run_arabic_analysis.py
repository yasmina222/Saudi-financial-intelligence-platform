import json
import os
from collections import Counter
from src.ml.arabic_sentiment_analyser import ArabicSentimentAnalyzer

def main():
    """
    This script tests the baseline Arabic sentiment analyzer on the
    generated Arabic financial dataset.
    """
    print("--- Running Baseline Arabic Sentiment Analysis Test ---")

    # 1. Initialize the Arabic Sentiment Analyzer
    analyzer = ArabicSentimentAnalyzer()
    if analyzer.classifier is None:
        print("\nERROR: Analyzer could not be initialized. Aborting test.")
        return

    # 2. Load the generated Arabic dataset
    arabic_dataset_path = "data/raw/arabic/latest_arabic_dataset.json"
    if not os.path.exists(arabic_dataset_path):
        print(f"\nERROR: Arabic dataset not found at '{arabic_dataset_path}'")
        print("Please run the arabic_data_generator.py script first.")
        return

    try:
        with open(arabic_dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        articles_to_process = dataset.get('articles', [])
        if not articles_to_process:
            print("No articles found in the dataset.")
            return
    except Exception as e:
        print(f"Failed to load or parse the dataset file: {e}")
        return

    # 3. Prepare documents for batch analysis
    # The analyzer's batch method expects a list of dicts with 'id' and 'text'
    documents_for_batch = [
        {'id': article.get('id'), 'text': article.get('title', '')}
        for article in articles_to_process
    ]

    # 4. Run the analysis
    analysis_results = analyzer.analyze_financial_batch(documents_for_batch)

    # 5. Evaluate the results
    if not analysis_results:
        print("Analysis did not produce any results.")
        return

    correct_predictions = 0
    total_predictions = len(analysis_results)
    sentiment_comparison = []

    result_map = {res['id']: res for res in analysis_results}

    for article in articles_to_process:
        article_id = article.get('id')
        expected_label = article.get('expected_sentiment')
        
        if article_id in result_map:
            predicted_label = result_map[article_id].get('sentiment')
            is_correct = (expected_label == predicted_label)
            if is_correct:
                correct_predictions += 1
            
            sentiment_comparison.append({
                'id': article_id,
                'title': article.get('title', '')[:70] + "...",
                'expected': expected_label,
                'predicted': predicted_label,
                'correct': is_correct
            })

    # 6. Print Summary Report
    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0

    print("\n" + "="*50)
    print("Baseline Model Performance Summary")
    print("="*50)
    print(f"Model Tested: CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment")
    print(f"Total Articles Analyzed: {total_predictions}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Baseline Accuracy: {accuracy:.2f}%")
    print("="*50)

    print("\nSample of Incorrect Predictions (if any):")
    incorrect_samples = [item for item in sentiment_comparison if not item['correct']][:5] # Show up to 5
    if incorrect_samples:
        for sample in incorrect_samples:
            print(f"  - Title: {sample['title']}")
            print(f"    -> Expected: {sample['expected'].upper()}, Predicted: {sample['predicted'].upper()}")
    else:
        print("  No incorrect predictions in this run, or all were correct!")

    print("\n--- Test Complete ---")
    print("\nThis accuracy score gives us a baseline. The next step, fine-tuning, aims to improve this score.")


if __name__ == "__main__":
    main()