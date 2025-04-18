import pandas as pd
from openrank_sdk import EigenTrust
import os

# Initialize EigenTrust. No API key needed.
eigentrust = EigenTrust(api_key="")

# Read the collector graph data
print("Reading collector graph data...")
df = pd.read_csv("collector_graph.csv")

# Convert the data to the format expected by OpenRank
print("Converting data to OpenRank format...")
localtrust = []
for _, row in df.iterrows():
    localtrust.append({
        "i": row["from"],
        "j": row["to"],
        "v": row["value"]
    })

# Compute EigenTrust rankings
print("Computing EigenTrust rankings...")
rankings = eigentrust.run_eigentrust(localtrust)

# Convert rankings to a DataFrame for easier viewing
rankings_df = pd.DataFrame(rankings)
rankings_df.columns = ["address", "score"]

# Sort by score in descending order
rankings_df = rankings_df.sort_values("score", ascending=False)

# Save rankings to CSV
output_file = "eigentrust_rankings.csv"
rankings_df.to_csv(output_file, index=False)
print(f"Rankings saved to {output_file}")

# Print top 10 addresses by EigenTrust score
print("\nTop 10 addresses by EigenTrust score:")
print(rankings_df.head(10)) 