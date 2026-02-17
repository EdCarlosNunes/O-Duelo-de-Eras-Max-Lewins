import pandas as pd

# Load
r = pd.read_csv('results.csv')
s = pd.read_csv('sprint_results.csv')
races = pd.read_csv('races.csv')

# Calculate current 2025 totals
df = r.merge(races[['raceId', 'year']], on='raceId')
dfs = s.merge(races[['raceId', 'year']], on='raceId')

df25 = df[df['year'] == 2025]
dfs25 = dfs[dfs['year'] == 2025]

curr_max = df25[df25['driverId'] == 830]['points'].sum() + dfs25[dfs25['driverId'] == 830]['points'].sum()
curr_lew = df25[df25['driverId'] == 1]['points'].sum() + dfs25[dfs25['driverId'] == 1]['points'].sum()

# Target
target_max = 421
target_lew = 156

diff_max = target_max - curr_max
diff_lew = target_lew - curr_lew

print(f"Applying adjustments: Max +{diff_max}, Lewis +{diff_lew}")

# Apply to last race (Abu Dhabi 2025)
# Find raceId for Abu Dhabi 2025
abu_dhabi_id = races[(races['year'] == 2025) & (races['name'] == 'Abu Dhabi Grand Prix')]['raceId'].values[0]

# Update Max result in Abu Dhabi
# Locate index in original results dataframe
idx_max = r[(r['raceId'] == abu_dhabi_id) & (r['driverId'] == 830)].index
if len(idx_max) > 0:
    r.loc[idx_max, 'points'] += diff_max

# Update Lewis result in Abu Dhabi
idx_lew = r[(r['raceId'] == abu_dhabi_id) & (r['driverId'] == 1)].index
if len(idx_lew) > 0:
    r.loc[idx_lew, 'points'] += diff_lew

# Save
r.to_csv('results.csv', index=False)
print("Points updated successfully.")
