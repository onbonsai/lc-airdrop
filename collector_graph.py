from web3 import Web3
import pandas as pd
import time
from lens_abi import lens_hub_abi as LENS_HUB_ABI
import os

# Connect to Polygon network
POLYGON_RPC_URL = os.environ.get("POLYGON_RPC_URL")
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

# Contract address and ABI
LENS_COLLECT = "0x0D90C58cBe787CD70B5Effe94Ce58185D72143fB"  # Collect Module
BONSAI_TOKEN = "0x3d2bD0e15829AA5C362a4144FdF4A1112fa29B5c"  # Bonsai Token
LENS_HUB_ADDRESS = "0xDb46d1Dc155634FbC732f92E853b10B288AD5a1d"

# ABI for the Collected event
COLLECTED_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "collectedProfileId", "type": "uint256"},
        {"indexed": True, "name": "collectedPubId", "type": "uint256"},
        {"indexed": True, "name": "collectorProfileId", "type": "uint256"},
        {"indexed": False, "name": "nftRecipient", "type": "address"},
        {"indexed": False, "name": "collectActionData", "type": "bytes"},
        {"indexed": False, "name": "collectActionResult", "type": "bytes"},
        {"indexed": False, "name": "collectNFT", "type": "address"},
        {"indexed": False, "name": "tokenId", "type": "uint256"},
        {"indexed": False, "name": "transactionExecutor", "type": "address"},
        {"indexed": False, "name": "timestamp", "type": "uint256"},
    ],
    "name": "Collected",
    "type": "event",
}

# Create contract instance
contract = w3.eth.contract(address=LENS_COLLECT, abi=[COLLECTED_EVENT_ABI])
lens_hub_contract = w3.eth.contract(address=LENS_HUB_ADDRESS, abi=LENS_HUB_ABI)

# Start block
START_BLOCK = 54264479
BLOCK_INCREMENT = 10000
FALLBACK_INCREMENT = 2000
MAX_RETRIES = 3

# Cache for profile owner addresses to reduce RPC calls
profile_owner_cache = {}


def get_owner_address(profile_id):
    # Check if profile_id is in cache first
    if profile_id in profile_owner_cache:
        return profile_owner_cache[profile_id]

    # If not in cache, make the contract call
    owner_address = lens_hub_contract.functions.ownerOf(profile_id).call()

    # Store result in cache for future use
    profile_owner_cache[profile_id] = owner_address

    return owner_address


def decode_collect_action_data(data):
    """Decode the collectActionData bytes to extract token and amount"""
    # Remove '0x' prefix if present
    if data.startswith("0x"):
        data = data[2:]

    # Extract token address (first 64 characters after removing 0x)
    token_address = "0x" + data[24:64]

    # Extract amount (next 64 characters)
    amount_hex = data[64:]
    amount = int(amount_hex, 16)

    return token_address.lower(), amount


def process_block_range(from_block, to_block, collector_graph):
    """Process a range of blocks and update the collector graph dictionary"""
    print(f"Processing blocks {from_block} to {to_block}...")

    # Create event filter for this block range
    collected_filter = contract.events.Collected.create_filter(fromBlock=from_block, toBlock=to_block)

    # Try to get events with retries and fallback to smaller block ranges
    block_increment = to_block - from_block + 1
    retries = 0

    while retries < MAX_RETRIES:
        try:
            # Get all events in this block range
            events = collected_filter.get_all_entries()
            print(f"Found {len(events)} Collected events in this range")

            # Process events
            for event in events:
                # Extract data from event
                collector_address = event["args"]["nftRecipient"].lower()
                collected_profile_id = event["args"]["collectedProfileId"]
                collect_action_data = event["args"]["collectActionData"].hex()

                # Decode collect action data
                token_address, amount = decode_collect_action_data(collect_action_data)

                # Check if this is a Bonsai token collection
                if token_address == BONSAI_TOKEN.lower():
                    # Get the address of the profile that was collected from
                    collected_from_address = get_owner_address(collected_profile_id).lower()

                    # Create a unique key for this collector-collected_from pair
                    edge_key = f"{collector_address}-{collected_from_address}"

                    # Add to collector graph
                    if edge_key in collector_graph:
                        collector_graph[edge_key]["value"] += amount
                    else:
                        collector_graph[edge_key] = {
                            "from": collector_address,
                            "to": collected_from_address,
                            "value": amount,
                        }

            # If we get here, the call was successful
            return collector_graph

        except Exception as e:
            retries += 1
            print(f"Error processing blocks {from_block} to {to_block}: {e}")

            # If we've tried the maximum number of retries, reduce the block range
            if retries >= MAX_RETRIES:
                # If we're already at the fallback increment, just skip this range
                if block_increment <= FALLBACK_INCREMENT:
                    print(f"Skipping blocks {from_block} to {to_block} after {MAX_RETRIES} retries")
                    return collector_graph

                # Reduce the block range and try again
                new_to_block = from_block + FALLBACK_INCREMENT - 1
                print(f"Reducing block range to {from_block} to {new_to_block}")

                # Process the first part of the range
                collector_graph = process_block_range(from_block, new_to_block, collector_graph)

                # If there are more blocks to process, continue with the next range
                if new_to_block < to_block:
                    next_from_block = new_to_block + 1
                    print(f"Continuing with blocks {next_from_block} to {to_block}")
                    collector_graph = process_block_range(next_from_block, to_block, collector_graph)

                return collector_graph

            # Wait before retrying
            time.sleep(2)

    return collector_graph


def main():
    print("Starting to fetch Collected events for collector graph...")

    # Get current block number
    current_block = w3.eth.block_number
    print(f"Current block: {current_block}")

    # Dictionary to store collector graph
    collector_graph = {}

    # Process blocks in increments
    for from_block in range(START_BLOCK, current_block, BLOCK_INCREMENT):
        to_block = min(from_block + BLOCK_INCREMENT - 1, current_block)
        collector_graph = process_block_range(from_block, to_block, collector_graph)

    print(f"Found {len(collector_graph)} collector-collected_from relationships")

    # Check if we have any relationships
    if not collector_graph:
        print("No collector relationships found in this block range")
        return

    # Convert to DataFrame
    df = pd.DataFrame(list(collector_graph.values()))

    # Convert amount from wei to ether
    df["value"] = df["value"].apply(lambda x: x / 1e18)

    # Save to CSV
    output_file = "collector_graph.csv"
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
    print(f"Total relationships: {len(df)}")

    # Print top 10 relationships by value
    print("\nTop 10 collector relationships by value:")
    print(df.sort_values("value", ascending=False).head(10))


if __name__ == "__main__":
    main()
