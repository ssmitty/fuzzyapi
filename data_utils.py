import pandas as pd
from fuzzywuzzy import process
import logging


def preprocess_name(name):
    """Remove common company suffixes, punctuation, and non-alphanumeric chars for better matching."""
    if not isinstance(name, str):
        return name
    import re

    name = name.lower()
    name = re.sub(r"[^a-z0-9 ]", "", name)  # Remove all non-alphanumeric except space
    suffixes = [
        " inc",
        " corporation",
        " corp",
        " ltd",
        " llc",
        " co",
        " - common stock",
        "- common stock",
        " common stock",
        " incorporated",
        " plc",
        " group",
        " holdings",
        " company",
        " companies",
        " lp",
        " ag",
        " sa",
        " nv",
        " spa",
        " srl",
        " limited",
        " the",
        " and",
        " of",
        " dba",
        " llp",
        " pty",
        " s p a",
        " s a",
        " inc",
        " inc",
        " inc",
        " inc",
    ]
    #gets rid of common company suffixes and normalizes whitespace
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    name = re.sub(r"\s+", " ", name)  # Normalize whitespace
    return name.strip()


def load_public_companies(csv_path):
    """Load public companies from a CSV file."""
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        logging.error(f"Error loading public companies from {csv_path}: {e}")
        raise


def add_preprocessed_column(tickers_df):
    tickers_df['preprocessed_title'] = tickers_df['title'].apply(preprocess_name)
    return tickers_df


def best_match(name, tickers_df):
    try:
        if not isinstance(name, str):
            logging.warning(f"Input name is not a string: {name}")
            return None, None, [], 0, None, "Company is not in public company list", []

        # 1. Try exact match against raw company names
        exact_matches = tickers_df[tickers_df['title'] == name]
        if not exact_matches.empty:
            matched_row = exact_matches.iloc[0]
            ticker = matched_row["ticker"] if "ticker" in matched_row and pd.notnull(matched_row["ticker"]) else None
            return matched_row['title'], ticker, [ticker] if ticker else [], 100, 100, None, [{
                "company_name": matched_row['title'],
                "ticker": ticker,
                "score": 100
            }]

        # 2. Preprocess input and match against preprocessed company names
        name_processed = preprocess_name(name)
        companies_list = tickers_df["preprocessed_title"].tolist()
        matches = process.extract(name_processed, companies_list, limit=10)
        strong_matches = [(company, score) for company, score in matches if score >= 90]

        if not strong_matches:
            logging.info(f"No strong matches (score >= 90) found for {name}")
            return None, None, [], 0, None, "Company is not in public company list", []

        # Get the best match (highest score)
        best_match_name, best_score = max(strong_matches, key=lambda x: x[1])
        matched_row = tickers_df[tickers_df["preprocessed_title"] == best_match_name]
        if matched_row.empty:
            logging.warning(f"Matched name {best_match_name} not found in public company list")
            return best_match_name, None, [], best_score, None, "Company is not in public company list", []
        matched_row = matched_row.iloc[0]
        ticker = matched_row["ticker"] if "ticker" in matched_row and pd.notnull(matched_row["ticker"]) else None

        # Get all possible tickers from strong matches
        all_possible_tickers = []
        top_matches = []
        for company, score in strong_matches:
            row = tickers_df[tickers_df["preprocessed_title"] == company]
            if not row.empty:
                t = row.iloc[0]["ticker"]
                if pd.notnull(t):
                    all_possible_tickers.append(t)
                top_matches.append({
                    "company_name": row.iloc[0]["title"],
                    "ticker": t if pd.notnull(t) else None,
                    "score": score
                })
        # Remove duplicates
        all_possible_tickers = list(dict.fromkeys(all_possible_tickers))

        ticker_score = 100 if ticker else None
        return matched_row['title'], ticker, all_possible_tickers, best_score, ticker_score, None, top_matches
    except Exception as e:
        logging.error(f"Error in best_match for name '{name}': {e}")
        return None, None, [], 0, None, "Company is not in public company list", []