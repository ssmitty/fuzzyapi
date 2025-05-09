print("Script started")
import pandas as pd
from data_utils import best_match, load_combined_dataset, load_public_companies

# Load your datasets
combined_df = load_combined_dataset('combined_with_tickers.csv')
tickers_df = load_public_companies('supplemental_data/company_tickers.csv')

# Load your test cases
try:
    # test_df = pd.read_csv('supplemental_data/testmod_first2words.csv')
    test_df = pd.read_csv('supplemental_data/nyse_test.csv')
    print("Loaded test cases shape:", test_df.shape)
    print("Test cases columns:", test_df.columns)
except Exception as e:
    print("Error loading test cases:", e)
    raise

correct_name = 0
correct_ticker = 0
total = len(test_df)

for idx, row in test_df.iterrows():
    print(f"\nProcessing row {idx}:")
    print(row)
    input_name = row['input_name']
    expected_name = row['expected_name']
    expected_ticker = row['expected_ticker']

    # Check if input_name is present in the combined dataset
    matches = combined_df[combined_df['Name'].str.strip().str.lower() == input_name.strip().lower()]
    if not matches.empty:
        print(f"Exact match found in combined dataset for input_name: {input_name}")
        print(matches)
    else:
        print(f"No exact match found in combined dataset for input_name: {input_name}")

    try:
        matched_name, predicted_ticker, all_possible_tickers, state, country, score, ticker_score = best_match(
            input_name, combined_df, tickers_df
        )
        print(f"best_match output: matched_name={matched_name}, predicted_ticker={predicted_ticker}, all_possible_tickers={all_possible_tickers}, state={state}, country={country}, score={score}, ticker_score={ticker_score}")
    except Exception as e:
        print(f"Error in best_match for input '{input_name}':", e)
        continue

    name_match = matched_name and expected_name and matched_name.strip().lower() == expected_name.strip().lower()

    # Updated ticker_match logic
    expected_ticker_is_nan = pd.isna(expected_ticker) or expected_ticker == ''
    predicted_ticker_is_none = predicted_ticker is None or all_possible_tickers == []
    if expected_ticker_is_nan and predicted_ticker_is_none:
        ticker_match = True
    else:
        ticker_match = predicted_ticker and expected_ticker and expected_ticker in all_possible_tickers

    if name_match:
        correct_name += 1
    if ticker_match:
        correct_ticker += 1

    if not name_match or not ticker_match:
        print(f"FAILED: Input: {input_name}")
        print(f"  Expected Name: {expected_name}, Got: {matched_name}")
        print(f"  Expected Ticker: {expected_ticker}, Got: {predicted_ticker}, All Possible: {all_possible_tickers}")
        print("---")

print(f"Total test cases: {total}")
print(f"Correct company name matches: {correct_name} ({correct_name/total:.2%})")
print(f"Correct ticker matches: {correct_ticker} ({correct_ticker/total:.2%})")