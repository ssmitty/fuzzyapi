import os
import pandas as pd

# Load the original file
file_path = 'supplemental_data/testmod.csv'
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    df = pd.read_csv(file_path)

# Create the new DataFrame
new_df = pd.DataFrame({
    'input_name': df['title'],
    'expected_name': df['title'],
    'expected_ticker': df['ticker']
})

# Save the reformatted file (first 100 rows for brevity)
new_df.head(100).to_csv('supplemental_data/testmod_reformatted.csv', index=False)
print("Reformatted testmod.csv saved as supplemental_data/testmod_reformatted.csv")