import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

import pandas as pd
from data_utils import best_match, load_public_companies

# Load your dataset (only public companies)
tickers_df = load_public_companies("supplemental_data/company_tickers.csv")

# Load your test cases
try:
    test_df = pd.read_csv('supplemental_data/mispell.csv')
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
#iterates through each row in the test dataframe and calls best match function
for idx, row in test_df.iterrows():
    input_name = row["input_name"]
    expected_name = row["expected_name"]
    expected_ticker = row["expected_ticker"]

    try:
        (
            matched_name,
            predicted_ticker,
            all_possible_tickers,
            score,
            ticker_score,
            message,
            top_matches,
        ) = best_match(input_name, tickers_df)
    except Exception as e:
        logging.error(f"Error in best_match for input '{input_name}': {e}")
        continue

    def normalize_name(name):
        return name.strip().lower() if isinstance(name, str) else ""

    expected_name_norm = normalize_name(expected_name)
    top_names_norm = [normalize_name(m['company_name']) for m in top_matches]

    expected_name_is_nan = pd.isna(expected_name) or expected_name == ""
    matched_name_is_none = matched_name is None
    expected_ticker_is_nan = pd.isna(expected_ticker) or expected_ticker == ""

    # Updated logic: If matched_name is None and expected_ticker is NaN/empty, count as correct name match
    if matched_name is None and expected_ticker_is_nan:
        name_match = True
    else:
        name_match = (
            matched_name
            and expected_name
            and (
                normalize_name(matched_name) == expected_name_norm
                or expected_name_norm in top_names_norm
            )
        )
    #if expected ticker is nan or empty, then set ticker match to true if not check if predicted ticker is in all possible tickers
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
    #if name or ticker does not match, then log the error
    #if not name_match or not ticker_match:
        #logging.error(f"Input: {input_name}")
        #logging.error(f"  Expected Name: {expected_name}, Got: {matched_name}")
        #logging.error(
        #    f"  Expected Ticker: {expected_ticker}, Got: {predicted_ticker}, All Possible: {all_possible_tickers}"
        #)
        #logging.error("---")

#logs the results
logging.info(f"Total test cases: {total}")
logging.info(f"Correct company name matches: {correct_name} ({correct_name/total:.2%})")
logging.info(f"Correct ticker matches: {correct_ticker} ({correct_ticker/total:.2%})")

# Recall for public companies (fixed)
recall = correct_ticker_public / public_total if public_total > 0 else 0
#logging.info(f"Ticker prediction recall (public companies): {recall:.2%}")

# Specificity for non-public companies
#looks for all non-public companies and checks if the ticker is not in the all possible tickers because they are not public
non_public_cases = test_df[test_df['expected_ticker'].isna() | (test_df['expected_ticker'] == '')]
non_public_total = len(non_public_cases)
true_negatives = 0
for idx, row in non_public_cases.iterrows():
    input_name = row["input_name"]
    expected_ticker = row["expected_ticker"]
    #calls best match function and returns the result
    (
        matched_name,
        predicted_ticker,
        all_possible_tickers,
        score,
        ticker_score,
        message,
        top_matches,
    ) = best_match(input_name, tickers_df)
    if (pd.isna(expected_ticker) or expected_ticker == "") and (predicted_ticker is None or all_possible_tickers == []):
        true_negatives += 1
specificity = true_negatives / non_public_total if non_public_total > 0 else 0
#logging.info(f"Non-public company specificity (true negative rate): {specificity:.2%}")

results_summary = (
    f"Total test cases: {total}\n"
    f"Correct company name matches: {correct_name} ({correct_name/total:.2%})\n"
    f"Correct ticker matches: {correct_ticker} ({correct_ticker/total:.2%})\n"
    f"Ticker prediction recall (public companies): {recall:.2%}\n"
    f"Non-public company specificity (true negative rate): {specificity:.2%}\n"
)

with open("evaluation_results.txt", "w") as f:
    f.write(results_summary)
