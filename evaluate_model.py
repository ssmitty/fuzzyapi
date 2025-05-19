import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

import pandas as pd
from data_utils import best_match, load_public_companies

# Load your dataset (only public companies)
tickers_df = load_public_companies("supplemental_data/company_tickers.csv")

# Load your test cases
try:
    test_df = pd.read_csv('supplemental_data/nyse_test.csv')
    logging.info(f"Loaded test cases shape: {test_df.shape}")
    logging.info(f"Test cases columns: {test_df.columns}")
except Exception as e:
    logging.error(f"Error loading test cases: {e}")
    raise

correct_name = 0
correct_ticker = 0
correct_ticker_public = 0
public_total = 0
total = len(test_df)

for idx, row in test_df.iterrows():
    input_name = row["input_name"]
    expected_name = row["expected_name"]
    expected_ticker = row["expected_ticker"]

    try:
        (
            matched_name,
            predicted_ticker,
            all_possible_tickers,
            state,
            country,
            score,
            ticker_score,
            message,
        ) = best_match(input_name, None, tickers_df)
    except Exception as e:
        logging.error(f"Error in best_match for input '{input_name}': {e}")
        continue

    name_match = (
        matched_name
        and expected_name
        and matched_name.strip().lower() == expected_name.strip().lower()
    )

    expected_ticker_is_nan = pd.isna(expected_ticker) or expected_ticker == ""
    predicted_ticker_is_none = predicted_ticker is None or all_possible_tickers == []
    if expected_ticker_is_nan and predicted_ticker_is_none:
        ticker_match = True
    else:
        ticker_match = (
            predicted_ticker
            and expected_ticker
            and expected_ticker in all_possible_tickers
        )

    if name_match:
        correct_name += 1
    if ticker_match:
        correct_ticker += 1

    # Only count recall for public companies
    if not expected_ticker_is_nan:
        public_total += 1
        if expected_ticker in all_possible_tickers:
            correct_ticker_public += 1

    if not name_match or not ticker_match:
        logging.error(f"FAILED: Input: {input_name}")
        logging.error(f"  Expected Name: {expected_name}, Got: {matched_name}")
        logging.error(
            f"  Expected Ticker: {expected_ticker}, Got: {predicted_ticker}, All Possible: {all_possible_tickers}"
        )
        logging.error("---")

logging.info(f"Total test cases: {total}")
logging.info(f"Correct company name matches: {correct_name} ({correct_name/total:.2%})")
logging.info(f"Correct ticker matches: {correct_ticker} ({correct_ticker/total:.2%})")

# Recall for public companies (fixed)
recall = correct_ticker_public / public_total if public_total > 0 else 0
logging.info(f"Ticker prediction recall (public companies): {recall:.2%}")

# Specificity for non-public companies
non_public_cases = test_df[test_df['expected_ticker'].isna() | (test_df['expected_ticker'] == '')]
non_public_total = len(non_public_cases)
true_negatives = 0
for idx, row in non_public_cases.iterrows():
    input_name = row["input_name"]
    expected_ticker = row["expected_ticker"]
    (
        matched_name,
        predicted_ticker,
        all_possible_tickers,
        state,
        country,
        score,
        ticker_score,
        message,
    ) = best_match(input_name, None, tickers_df)
    if (pd.isna(expected_ticker) or expected_ticker == "") and (predicted_ticker is None or all_possible_tickers == []):
        true_negatives += 1
specificity = true_negatives / non_public_total if non_public_total > 0 else 0
logging.info(f"Non-public company specificity (true negative rate): {specificity:.2%}")
