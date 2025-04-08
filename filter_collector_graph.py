import pandas as pd

def filter_self_edges(input_filename="collector_graph.csv", output_filename="collector_graph.csv"):
    """
    Reads a collector graph CSV, removes rows where 'from' and 'to' are the same,
    and saves the filtered data to a new CSV file.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_filename)
        print(f"Read {len(df)} rows from {input_filename}")

        initial_rows = len(df)

        # Filter out self-edges
        df_filtered_self = df[df['from'] != df['to']]
        self_edges_removed = initial_rows - len(df_filtered_self)
        print(f"Removed {self_edges_removed} self-edges (where 'from' == 'to').")

        # Filter out zero-value edges
        df_filtered_value = df_filtered_self[df_filtered_self['value'] > 0].copy() # Use .copy()
        zero_value_removed = len(df_filtered_self) - len(df_filtered_value)
        print(f"Removed {zero_value_removed} zero-value edges (where 'value' == 0).")

        final_rows = len(df_filtered_value)
        total_removed = initial_rows - final_rows

        print(f"Total rows removed: {total_removed}")
        print(f"Writing {final_rows} rows to {output_filename}")

        # Save the filtered DataFrame to a new CSV file
        df_filtered_value.to_csv(output_filename, index=False)
        print(f"Filtered graph saved to {output_filename}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
    except KeyError as e:
        print(f"Error: Missing expected column '{e}' in {input_filename}. Make sure the CSV has 'from' and 'to' columns.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    filter_self_edges() 