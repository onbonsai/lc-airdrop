# Lens Protocol Collector Analysis

This repository contains tools for analyzing collector behavior on the Lens Protocol, specifically focusing on Bonsai token collectors. The project helps identify and rank top collectors, generate collector graphs, and compute EigenTrust scores.

## Features

- Collector graph generation from Lens Protocol events
- Top collector identification and ranking
- EigenTrust score computation
- Merkle tree generation for airdrop eligibility
- Integration with Lens Protocol smart contracts

## Prerequisites

- Python 3.x
- Access to a Polygon RPC node
- Web3.py
- Pandas
- OpenRank SDK

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/lc-airdrop.git
cd lc-airdrop
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Polygon RPC URL:

```
POLYGON_RPC_URL=your_polygon_rpc_url_here
```

## Project Structure

- `collector_graph.py`: Generates a graph of collector interactions
- `top_collectors.py`: Identifies and ranks top collectors
- `compute_eigentrust.py`: Computes EigenTrust scores for collectors
- `generate_merkle_tree.py`: Creates a Merkle tree for airdrop eligibility
- `lens_abi.py`: Contains Lens Protocol smart contract ABIs
- `filter_collector_graph.py`: Filters the collector graph to remove self-edges and zero-value edges

## Usage

1. Generate collector graph:

```bash
python collector_graph.py
```

2. Identify top collectors:

```bash
python top_collectors.py
```

2.1 Filter collector graph:
Not strictly necessary but removes warnings when running compute_eigentrust.py

```bash
python filter_collector_graph.py
```

3. Compute EigenTrust scores:

```bash
python compute_eigentrust.py
```

4. Generate Merkle tree:

```bash
python generate_merkle_tree.py
```

## Output Files

- `collector_graph.csv`: Contains the generated collector interaction graph
- `ranked_bonsai_collectors.csv`: List of ranked Bonsai token collectors
- `eigentrust_rankings.csv`: List of ranked collectors with EigenTrust scores
- `merkle_proofs.json`: Merkle proofs for airdrop eligibility
