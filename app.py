from flask import Flask, jsonify, request, make_response
import data_utils
import logging
import sys
import subprocess

app = Flask(__name__)

API_VERSION = "0.1.0"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load company data at startup with error handling
try:
    combined_data_path = '3_combined_dataset_postproc.csv'
    tickers_data_path = 'supplemental_data/company_tickers.csv'
    combined_df = data_utils.load_combined_dataset(combined_data_path)
    tickers_df = data_utils.load_public_companies(tickers_data_path)
except Exception as e:
    logging.critical(f"Failed to load data at startup: {e}")
    sys.exit(1)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    error_message = None
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            if not name:
                error_message = "No company name provided."
            else:
                try:
                    match_name, predicted_ticker, all_possible_tickers, state, country, score, ticker_score = data_utils.best_match(name, combined_df, tickers_df)
                    result = {
                        "input_name": name,
                        "matched_name": match_name,
                        "predicted_ticker": predicted_ticker,
                        "all_possible_tickers": all_possible_tickers,
                        "state": state,
                        "country": country,
                        "match_score": score,
                        "ticker_score": ticker_score
                    }
                except Exception as e:
                    logging.error(f"Error during matching: {e}")
                    error_message = "An error occurred during matching. Please try again."
    except Exception as e:
        logging.error(f"Unexpected error in home route: {e}")
        error_message = "An unexpected error occurred. Please try again."

    result_html = ""
    if error_message:
        result_html = f"<div class='result' style='color:red;'><b>Error:</b> {error_message}</div>"
    elif result:
        # Handle predicted_ticker as a single value or None
        ticker_display = result['predicted_ticker']
        if isinstance(ticker_display, list):
            if len(ticker_display) == 0:
                ticker_display = "None"
            else:
                ticker_display = ', '.join(ticker_display)
        elif ticker_display is None:
            ticker_display = "None"
        # Handle all_possible_tickers as a list
        all_possible_tickers_display = ""
        if isinstance(result['all_possible_tickers'], list) and len(result['all_possible_tickers']) > 1:
            all_possible_tickers_display = (
                f"<br><b>All Possible Tickers:</b> {', '.join(result['all_possible_tickers'])}"
            )
        result_html = (
            f"<div class='result'><b>Input:</b> {result['input_name']}<br>"
            f"<b>Matched:</b> {result['matched_name']}<br>"
            f"<b>Predicted Ticker:</b> {ticker_display}<br>"
            f"<b>State:</b> {result['state']}<br>"
            f"<b>Country:</b> {result['country']}<br>"
            f"<b>Company Match Score:</b> {result['match_score']}<br>"
            f"<b>Ticker Match Score:</b> {result['ticker_score']}"
            f"{all_possible_tickers_display}</div>"
        )

    html = f'''
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
    '''
    response = make_response(html)
    response.headers["X-API-Version"] = API_VERSION
    return response

@app.route('/update_tickers', methods=['POST'])
def update_tickers():
    try:
        subprocess.run(['python3', 'update_tickers.py'], check=True)
        message = 'Tickers updated successfully.'
    except subprocess.CalledProcessError as e:
        message = f'Error updating tickers: {e}'
    html = f'''
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
    '''
    response = make_response(html)
    response.headers["X-API-Version"] = API_VERSION
    return response

# Optional: Add a global error handler for uncaught exceptions


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)

