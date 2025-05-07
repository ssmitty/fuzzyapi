# Company Matcher API

This project provides a Flask API and web interface to fuzzy match company names against a combined dataset and return the best match, including state, country, and ticker symbol (if the company is publicly traded).

## Features
- Fuzzy matching of company names using advanced preprocessing and token set ratio
- Ticker lookup using a merged NASDAQ and NYSE/AMEX dataset
- Returns company name, state, country, ticker, and match scores
- Batch processing utility for bulk matching
- Docker support for easy deployment

## Data Sources
- **Combined Dataset:** `3_combined_dataset_postproc.csv` ( main company database)
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

Can go in file and click run all services 

or

```bash
docker-compose up --build
```
#The second URL is simply for internal Docker use. Use the First url for local host access

## API Usage
- The root endpoint `/` supports both GET (form) and POST (form submission).
- The API returns the matched company, ticker, state, country, and match scores.



## Running Tests

To run the test suite:

```bash
python3 test_api.py
```



## Notes
- The ticker dataset is now a CSV, not JSON.
- Fuzzy matching is robust to suffixes, punctuation, and word order.
- Only companies with a ticker match score >= 90 are assigned a ticker.
- Uisng combined dataset NYSE and NASDAQ for tickers

## License
MIT 