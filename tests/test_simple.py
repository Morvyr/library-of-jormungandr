import pandas as pd

# Read the CSV
df = pd.read_csv('simple_test.csv', dtype=str, keep_default_na=False)
df = df.replace('', pd.NA)

print("BEFORE:")
print(df)
print("\nName column dtype:", df['Name'].dtype)
print("Email column dtype:", df['Email'].dtype)

# Try the transformation
df['Name'] = df['Name'].apply(lambda x: x.title() if pd.notna(x) and isinstance(x, str) else x)
df['Email'] = df['Email'].apply(lambda x: x.lower() if pd.notna(x) and isinstance(x, str) else x)

print("\nAFTER:")
print(df)