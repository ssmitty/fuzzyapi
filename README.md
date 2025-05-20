# Company Matcher API

This project provides a Flask API and web interface to fuzzy match company names against a combined dataset and return the best match, including the ticker symbol (if the company is publicly traded).

## Features
- Fuzzy matching of company names using advanced preprocessing and token set ratio
- Ticker lookup using a merged NASDAQ and NYSE/AMEX dataset
- Returns company name, ticker, and match scores
- Batch processing utility for bulk matching
- Docker support for easy deployment

## Data Sources
- **Combined Dataset:** `3_combined_dataset_postproc.csv` (your main company database)
- **Tickers Dataset:** `supplemental_data/company_tickers.csv` (merged NASDAQ and NYSE/AMEX tickers, updated via script)

## Setup
1. **Clone the repository and install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Update the tickers dataset (recommended before first run):**
   ```bash
   python3 update_tickers.py
   ```
   This script downloads and merges the latest NASDAQ and NYSE/AMEX tickers into `supplemental_data/company_tickers.csv`.

3. **Run the Flask app:**
   ```bash
   python3 app.py
   ```
   By default, the app runs on port 8080. If you see "Address already in use", either kill the process using that port or change the port in `app.py` (e.g., to 5000).

4. **Access the web interface:**
   - Go to [http://localhost:8080](http://localhost:8080) (or your chosen port)
   - Enter a company name to get the best match and ticker info

## Running with Docker

To build and run the app using Docker:

```bash
docker build -t company-matcher-api .
docker run -p 8080:8080 company-matcher-api
```

Or, using Docker Compose:

```bash
docker-compose up --build
```
# The second URL is simply for internal Docker use. Use the first URL for local host access

## API Usage
- The root endpoint `/` supports both GET (form) and POST (form submission).
- The API returns the matched company, ticker, and match scores.

## Running Tests

To run the test suite:
- Make sure the local host is running and open a new terminal
- In the new terminal input:

```bash
python3 test_api.py
```

To evaluate the model on its success for determining public company names and tickers run:

```bash
python3 evaluate_model.py
```

**About How I Evaluated the Model:**
I created a CSV of all public company names along with alot of private/non-public company names(fulltest.csv and mini version with 157 companies nyse_test.csv. Takes a very long time to run fulltest). The CSV file has three columns: `input_name` (the name that the "user" would enter, which is the first 2 words of the expected name), `expected_name` (the actual listed public company name on NASDAQ or NYSE), and `expected_ticker` (the ticker listed on NASDAQ or NYSE). The model goes through each row in the file and gives a point if it matches the correct name and ticker based on the "user input". For recall, it checks only the public company names and sees how many ticker matches it got correctly. For specificity, it checks how many false positive ticker matches occurred for non-public companies.

## Troubleshooting
- **Port already in use:**
  - Find and kill the process using the port:
    ```bash
    lsof -i :8080
    kill <PID>
    ```
  - Or, change the port in `app.py` to a free port (e.g., 5000).
- **Ticker not found for public company:**
  - Make sure you have run `update_tickers.py` to get the latest tickers.
  - The fuzzy matching logic now uses advanced preprocessing and token set ratio for better accuracy.

## Notes
- The ticker dataset is now a CSV, not JSON.
- Fuzzy matching is robust to suffixes, punctuation, and word order.
- Only companies with a ticker match score >= 90 are assigned a ticker.
- Using a combined dataset of NYSE and NASDAQ for tickers and company names.

## License
MIT 