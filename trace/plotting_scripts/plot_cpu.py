import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from glob import glob
from pathlib import Path

outdir = "./plots"


def create_cpu_utilization_timeline(
    root_dir="../../trace-result/", virtualization="host"
):
    """
    Creates a timeline plot with CPU utilization for every variant,
    using the latest datetime results for each variant.
    Uses aggregate CPU data (CPU = -1) and orders by row numbers for precise ordering.

    Args:
        root_dir (str): Root directory containing variant folders
        virtualization (str): 'host' or 'guest' for virtualization type
    """

    # Dictionary to store the latest file path for each variant
    latest_files = {}

    # Scan root directory for variant folders
    for variant in os.listdir(root_dir):
        variant_path = os.path.join(root_dir, variant)

        # Skip if not a directory
        if not os.path.isdir(variant_path):
            continue

        # Find all datetime directories in this variant folder
        datetime_dirs = []

        for item in os.listdir(variant_path):
            item_path = os.path.join(variant_path, item)
            if os.path.isdir(item_path):
                # Check if cpu.csv exists in this directory
                cpu_file = os.path.join(item_path, f"{virtualization}/cpu.csv")
                if os.path.exists(cpu_file):
                    try:
                        # Try to parse datetime from directory name
                        possible_formats = [
                            "%Y-%m-%d-%H-%M-%S",
                            "%Y%m%d_%H%M%S",
                            "%Y-%m-%d_%H%M%S",
                            "%Y%m%d-%H%M%S",
                        ]

                        parsed_datetime = None
                        for fmt in possible_formats:
                            try:
                                parsed_datetime = datetime.strptime(item, fmt)
                                break
                            except ValueError:
                                continue

                        if parsed_datetime:
                            datetime_dirs.append((parsed_datetime, cpu_file))
                    except:
                        continue

        # Get the latest datetime directory for this variant
        if datetime_dirs:
            latest_datetime, latest_file = max(datetime_dirs, key=lambda x: x[0])
            latest_files[variant] = latest_file
            print(
                f"Latest file for {variant} {virtualization}: {latest_file} ({latest_datetime})"
            )

    if not latest_files:
        print("No CPU files found!")
        return

    # Create the plot
    plt.figure(figsize=(15, 8))

    # Define column names for the CSV (since header parsing might be inconsistent)
    header_cols = [
        "hostname",
        "interval",
        "timestamp",
        "CPU",
        "%usr",
        "%nice",
        "%sys",
        "%iowait",
        "%steal",
        "%irq",
        "%soft",
        "%guest",
        "%gnice",
        "%idle",
    ]

    # Plot data for each variant
    for variant, cpu_file in latest_files.items():
        try:
            # Read the CSV file with explicit column names
            df = pd.read_csv(cpu_file, comment="#", names=header_cols)

            # Filter aggregate data where CPU = -1
            df_aggregate = df[df["CPU"] == -1].copy()

            if df_aggregate.empty:
                print(f"No aggregate CPU data found for {variant}")
                continue

            # Order artificially by row numbers (reset index for clear ordering)
            df_aggregate = df_aggregate.reset_index(drop=True)

            # Calculate total utilization (100 - idle)
            df_aggregate["total_util"] = 100 - df_aggregate["%idle"]

            # Plot using row index as x-axis for precise ordering
            plt.plot(
                df_aggregate.index,
                df_aggregate["total_util"],
                label=f"{variant}",
                linewidth=2,
                marker="o",
                markersize=4,
            )

        except Exception as e:
            print(f"Error processing {variant}: {e}")
            continue

    # Customize the plot
    plt.xlabel("Time sample", fontsize=12)
    plt.ylabel("CPU Utilization (%)", fontsize=12)
    plt.title(
        f"CPU Utilization Timeline by Variant - {virtualization.capitalize()} (Latest Results)",
        fontsize=14,
    )
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save the plot
    output_file = f"{outdir}/cpu_utilization_timeline_{virtualization}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Plot saved as: {output_file}")

    plt.show()


# Usage example:
if __name__ == "__main__":
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    # Run the function with current directory
    create_cpu_utilization_timeline("../../trace-result/", "host")
    create_cpu_utilization_timeline("../../trace-result/", "guest")
