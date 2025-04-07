import csv
import hashlib
import json
import os
from typing import Dict, List, Tuple

class MerkleTree:
    def __init__(self, leaves: List[Tuple[str, float]]):
        self.leaves = leaves
        # Pre-compute leaf hashes for faster lookups
        self.leaf_hashes = [self._hash(f"{addr}{amount}") for addr, amount in self.leaves]
        self.tree = self._build_tree()
        self.root = self.tree[0] if self.tree else None

    def _hash(self, data: str) -> str:
        """Hash data using keccak-256 (same as Ethereum)"""
        return hashlib.sha3_256(data.encode()).hexdigest()

    def _build_tree(self) -> List[str]:
        """Build a Merkle tree from the leaves"""
        if not self.leaves:
            return []

        # Use pre-computed leaf hashes
        tree = self.leaf_hashes.copy()
        level_size = len(self.leaf_hashes)
        
        while level_size > 1:
            level = []
            for i in range(0, level_size, 2):
                if i + 1 < level_size:
                    # Hash the pair of nodes
                    level.append(self._hash(tree[i] + tree[i + 1]))
                else:
                    # If there's an odd number of nodes, duplicate the last one
                    level.append(self._hash(tree[i] + tree[i]))
            
            tree.extend(level)
            level_size = len(level)
        
        return tree

    def get_proof(self, address: str, amount: float) -> Dict:
        """Get the Merkle proof for a given address and amount"""
        # Calculate the leaf hash
        leaf_hash = self._hash(f"{address}{amount}")
        
        # Find the index of the leaf hash
        try:
            leaf_index = self.leaf_hashes.index(leaf_hash)
        except ValueError:
            return {"error": "Address and amount not found in the tree"}

        # Calculate the path to the root
        proof = []
        current_index = leaf_index
        
        # Calculate the number of levels in the tree
        num_leaves = len(self.leaves)
        num_levels = 0
        level_size = num_leaves
        while level_size > 1:
            num_levels += 1
            level_size = (level_size + 1) // 2
        
        # Calculate the starting index of each level
        level_start_indices = [0]
        level_size = num_leaves
        for _ in range(num_levels):
            level_start_indices.append(level_start_indices[-1] + level_size)
            level_size = (level_size + 1) // 2
        
        # Build the proof
        for level in range(num_levels):
            level_start = level_start_indices[level]
            level_size = level_start_indices[level + 1] - level_start
            
            # Determine if the current node is a left or right child
            is_left = current_index % 2 == 0
            
            # Get the sibling node
            if is_left and current_index + 1 < level_size:
                sibling_index = level_start + current_index + 1
            elif not is_left:
                sibling_index = level_start + current_index - 1
            else:
                # If there's no sibling, use the node itself
                sibling_index = level_start + current_index
            
            # Add the sibling to the proof
            proof.append({
                "hash": self.tree[sibling_index],
                "isLeft": not is_left
            })
            
            # Move to the parent node
            current_index = current_index // 2
        
        return {
            "address": address,
            "amount": amount,
            "proof": proof,
            "root": self.root
        }

def main():
    # Check if input file exists
    input_file = "eigentrust_rankings.csv"
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        print("Please run compute_eigentrust.py first or specify a different input file")
        return
    
    # Read the CSV file
    print(f"Reading {input_file}...")
    addresses = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert score to float and round to 6 decimal places
            amount = float(row['score'])
            addresses.append((row['address'], amount))
    
    # Create the Merkle tree
    print("Generating Merkle tree...")
    merkle_tree = MerkleTree(addresses)
    
    # Generate proofs for all addresses
    print("Generating proofs...")
    proofs = []
    for address, amount in addresses:
        proof = merkle_tree.get_proof(address, amount)
        proofs.append(proof)
    
    # Save the proofs to a JSON file
    output_file = "merkle_proofs.json"
    with open(output_file, 'w') as f:
        json.dump(proofs, f, indent=2)
    
    print(f"Root hash: {merkle_tree.root}")
    print(f"Proofs saved to {output_file}")
    print(f"Total addresses: {len(addresses)}")

if __name__ == "__main__":
    main() 