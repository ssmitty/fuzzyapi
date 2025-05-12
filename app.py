"""Flask API for fuzzy company name matching and ticker lookup."""

import logging
import sys
import subprocess
import time
import pandas as pd
from flask import Flask, jsonify, request, make_response
import data_utils

APP_VERSION = "0.1.0"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load company data at startup with error handling
try:
    COMBINED_DATA_PATH = "combined_with_tickers.csv"
    TICKERS_DATA_PATH = "supplemental_data/company_tickers.csv"
    combined_df = data_utils.load_combined_dataset(COMBINED_DATA_PATH)
    tickers_df = data_utils.load_public_companies(TICKERS_DATA_PATH)
except Exception as err:
    logging.critical("Failed to load data at startup: %s", err)
    sys.exit(1)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    """Main route for company matcher form and results."""
    result = None
    error_message = None
    try:
        if request.method == "POST":
            name = request.form.get("name")
            if not name:
                error_message = "No company name provided."
            else:
                try:
                    start = time.time()  # Start timing
                    (
                        match_name,
                        predicted_ticker,
                        all_possible_tickers,
                        state,
                        country,
                        score,
                        ticker_score,
                    ) = data_utils.best_match(name, combined_df, tickers_df)
                    end = time.time()  # End timing
                    api_latency = end - start
                    logging.info(
                        "API Latency for '%s': %.4f seconds", name, api_latency
                    )
                    result = {
                        "input_name": name,
                        "matched_name": match_name,
                        "predicted_ticker": predicted_ticker,
                        "all_possible_tickers": all_possible_tickers,
                        "state": state,
                        "country": country,
                        "match_score": score,
                        "ticker_score": ticker_score,
                    }
                except Exception as err:
                    logging.error("Error during matching: %s", err)
                    error_message = (
                        "An error occurred during matching. Please try again."
                    )
    except Exception as err:
        logging.error("Unexpected error in home route: %s", err)
        error_message = "An unexpected error occurred. Please try again."

    result_html = ""
    if error_message:
        result_html = (
            f"<div class='result' style='color:red;'><b>Error:</b> {error_message}</div>"
        )
    elif result:
        # Handle predicted_ticker as a single value or None
        ticker_display = result["predicted_ticker"]
        if isinstance(ticker_display, list):
            if len(ticker_display) == 0:
                ticker_display = "None"
            else:
                ticker_display = ", ".join(ticker_display)
        elif ticker_display is None:
            ticker_display = "None"
        # Handle all_possible_tickers as a list
        all_possible_tickers_display = ""
        if (
            isinstance(result["all_possible_tickers"], list)
            and len(result["all_possible_tickers"]) > 1
        ):
            all_possible_tickers_display = (
                "<br><b>All Possible Tickers:</b> "
                f"{', '.join(result['all_possible_tickers'])}"
            )
        # Conditionally add State and Country if not None or NaN
        state_val = result["state"]
        country_val = result["country"]
        state_html = (
            f"<b>State:</b> {state_val}<br>"
            if pd.notna(state_val)
            and str(state_val).strip().lower() not in ("", "none", "nan")
            else ""
        )
        country_html = (
            f"<b>Country:</b> {country_val}<br>"
            if pd.notna(country_val)
            and str(country_val).strip().lower() not in ("", "none", "nan")
            else ""
        )
        result_html = (
            f"<div class='result'><b>Input:</b> {result['input_name']}<br>"
            f"<b>Matched:</b> {result['matched_name']}<br>"
            f"<b>Predicted Ticker:</b> {ticker_display}<br>"
            f"{state_html}"
            f"{country_html}"
            f"<b>Company Match Score:</b> {result['match_score']}<br>"
            f"<b>Ticker Match Score:</b> {result['ticker_score']}<br>"
            f"{all_possible_tickers_display}</div>"
        )

    html = f"""
        <html>
            <head>
                <title>Company Matcher</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body>
                <div id="loading-overlay" class="loading-overlay" style="display:none;">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Updating tickers dataset...</div>
                </div>
                <div class="container">
                    <h2>Company Matcher</h2>
                    <form method="post" class="search-form">
                        <input type="text" name="name" placeholder="Enter company name" required>
                        <br>
                        <input type="submit" value="Match">
                    </form>
                    <form method="post" action="/update_tickers" id="update-tickers-form" class="update-form">
                        <input type="submit" value="Update Tickers Dataset">
                    </form>
                    {result_html}
                </div>
                <script>
                document.getElementById('update-tickers-form').addEventListener('submit', function() {{
                    document.getElementById('loading-overlay').style.display = 'flex';
                }});
                </script>
            </body>
        </html>
    """
    response = make_response(html)
    response.headers["X-API-Version"] = APP_VERSION
    return response

@app.route("/update_tickers", methods=["POST"])
def update_tickers():
    """Route to update tickers dataset by running update_tickers.py."""
    try:
        subprocess.run(["python3", "update_tickers.py"], check=True)
        message = "Tickers updated successfully."
    except subprocess.CalledProcessError as err:
        message = f"Error updating tickers: {err}"
    html = f"""
        <html>
            <head>
                <title>Update Tickers</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body>
                <div class="container">
                    <h2>Update Tickers</h2>
                    <div class='result'>{message}</div>
                    <a href="/">Back to Home</a>
                </div>
            </body>
        </html>
    """
    response = make_response(html)
    response.headers["X-API-Version"] = APP_VERSION
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080, use_reloader=False)
