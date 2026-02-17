import pandas as pd

# Load data
r = pd.read_csv('results.csv')
s = pd.read_csv('sprint_results.csv')
races = pd.read_csv('races.csv')

# Merge
df = r.merge(races[['raceId', 'year']], on='raceId')
dfs = s.merge(races[['raceId', 'year']], on='raceId')

# Filter 2025
df25 = df[df['year'] == 2025]
dfs25 = dfs[dfs['year'] == 2025]

# Calculate Totals
max_pts = df25[df25['driverId'] == 830]['points'].sum() + dfs25[dfs25['driverId'] == 830]['points'].sum()
lew_pts = df25[df25['driverId'] == 1]['points'].sum() + dfs25[dfs25['driverId'] == 1]['points'].sum()

print(f"Current Max 2025 Points: {max_pts}")
print(f"Current Lewis 2025 Points: {lew_pts}")

target_max = 421
target_lew = 156

print(f"Target Max: {target_max} (Diff: {target_max - max_pts})")
print(f"Target Lewis: {target_lew} (Diff: {target_lew - lew_pts})")
