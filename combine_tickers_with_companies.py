import pandas as pd

print("Loading main combined dataset...")
# Load your main combined dataset
main_df = pd.read_csv('3_combined_dataset_postproc.csv')
print(f"Main dataset loaded: {main_df.shape[0]} rows, {main_df.shape[1]} columns")

# Remove 'id' and 'number' columns if they exist
cols_to_drop = [col for col in ['id', 'number', 'IDNum', 'Number'] if col in main_df.columns]
if cols_to_drop:
    print(f"Dropping columns: {cols_to_drop}")
    main_df = main_df.drop(columns=cols_to_drop)
else:
    print("No ID/number columns to drop.")

print("Loading tickers dataset...")
# Load tickers (NASDAQ + NYSE/AMEX)
tickers_df = pd.read_csv('supplemental_data/company_tickers.csv')
print(f"Tickers dataset loaded: {tickers_df.shape[0]} rows, {tickers_df.shape[1]} columns")

tickers_df['Name'] = tickers_df['title']
tickers_df['State'] = ''
tickers_df['Country'] = ''

main_columns = [col for col in main_df.columns]
print(f"Main columns for combined DataFrame: {main_columns}")
tickers_for_combined = pd.DataFrame(columns=main_columns)
for col in main_columns:
    if col == 'Name':
        tickers_for_combined[col] = tickers_df['Name']
    elif col == 'State':
        tickers_for_combined[col] = ''
    elif col == 'Country':
        tickers_for_combined[col] = ''
    else:
        tickers_for_combined[col] = ''
print(f"Tickers for combined DataFrame created: {tickers_for_combined.shape[0]} rows, {tickers_for_combined.shape[1]} columns")

print("Concatenating main and tickers DataFrames...")
combined = pd.concat([main_df, tickers_for_combined], ignore_index=True)
print(f"Combined DataFrame shape: {combined.shape[0]} rows, {combined.shape[1]} columns")
combined.to_csv('combined_with_tickers.csv', index=False)
print("Combined dataset saved as combined_with_tickers.csv (tickers have blank state and country fields)")

# Save the tickers-only dataset (already done by update_tickers.py, but you can uncomment to refresh)
tickers_df[['ticker', 'title']].to_csv('supplemental_data/company_tickers.csv', index=False)
# print("Tickers-only dataset saved as supplemental_data/company_tickers.csv") 