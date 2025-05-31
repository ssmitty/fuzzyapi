"""Flask API for fuzzy company name matching and ticker lookup."""

import logging
import sys
import subprocess
import time
import pandas as pd
from flask import Flask,request, make_response, redirect
import data_utils
from flasgger import Swagger

APP_VERSION = "0.1.0"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load company data at startup with error handling
#loads all companies from ticker dataset-nasdaq and nyse stock exchange
try:
    TICKERS_DATA_PATH = "supplemental_data/company_tickers.csv"
    tickers_df = data_utils.load_public_companies(TICKERS_DATA_PATH)
    tickers_df = data_utils.add_preprocessed_column(tickers_df)
except Exception as err:
    logging.critical("Failed to load data at startup: %s", err)
    sys.exit(1)

app = Flask(__name__)
swagger = Swagger(app, template={
    "info": {
        "title": "Company Ticker Matching",
        "description": "API for fuzzy matching company names and tickers.",
        "version": "1.0.0"
    }
})

@app.route("/")
def root():
    return redirect("/apidocs")

@app.route("/", methods=["GET"])
def home_form():
    # Render your HTML form here
    return '''
    <form method="post" action="/match">
        <input type="text" name="name" placeholder="Enter company name" required>
        <input type="submit" value="Match">
    </form>
    '''

@app.route("/match", methods=["POST"])
def match_api():
    """
    Company Matcher Endpoint
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: The company name to match
    responses:
      200:
        description: Returns the best match and ticker info
    """
    result = None
    error_message = None
    try:
        name = request.form.get("name")
        if not name:
            error_message = "No company name provided."
        else:
            try:
                start = time.time()
                (
                    match_name,
                    predicted_ticker,
                    all_possible_tickers,
                    score,
                    ticker_score,
                    message,
                    top_matches,
                ) = data_utils.best_match(name, tickers_df)
                end = time.time()
                api_latency = end - start
                logging.info(
                    "API Latency for '%s': %.4f seconds", name, api_latency
                )
                result = {
                    "input_name": name,
                    "matched_name": match_name,
                    "predicted_ticker": predicted_ticker,
                    "all_possible_tickers": all_possible_tickers,
                    "match_score": score,
                    "ticker_score": ticker_score,
                    "message": message,
                    "top_matches": top_matches,
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
        ticker_display = result["predicted_ticker"]
        if isinstance(ticker_display, list):
            if len(ticker_display) == 0:
                ticker_display = "None"
            else:
                ticker_display = ", ".join(ticker_display)
        elif ticker_display is None:
            ticker_display = "None"
        all_possible_tickers_display = ""
        if (
            isinstance(result["all_possible_tickers"], list)
            and len(result["all_possible_tickers"]) > 1
        ):
            all_possible_tickers_display = (
                "<br><b>All Possible Tickers:</b> "
                f"{', '.join(result['all_possible_tickers'])}"
            )
        message_html = (
            f"<div class='result' style='color:orange;'><b>Note:</b> {result['message']}</div>"
            if result.get("message") else ""
        )
        top_matches_html = ""
        if result.get("top_matches"):
            top_matches_html = (
                "<div class='result'><b>Top Matches:</b><br>" +
                "<br>".join(
                    f"{m['company_name']} ({m['ticker']})" for m in result["top_matches"]
                ) + "</div>"
            )
        result_html = (
            f"<div class='result'><b>Input:</b> {result['input_name']}<br>"
            f"<b>Matched:</b> {result['matched_name']}<br>"
            f"<b>Predicted Ticker:</b> {ticker_display}<br>"
            f"<b>Company Match Score:</b> {result['match_score']}<br>"
            f"<b>Ticker Match Score:</b> {result['ticker_score']}<br>"
            f"{all_possible_tickers_display}"
            f"{message_html}"
            f"{top_matches_html}"
            f"</div>"
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

@app.route("/update_tickers", methods=["GET"])
def update_tickers():
    """
    Update Tickers Dataset
    ---
    responses:
      200:
        description: Tickers updated successfully or error message
    """
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
