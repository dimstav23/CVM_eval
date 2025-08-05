import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

outdir = "./plots"


def create_memory_consumption_timeline(
    root_dir="../../trace-result/", virtualization="host"
):
    """
    Creates a timeline plot with memory consumption for every variant,
    using the latest datetime results for each variant.

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
                # Check if memory.csv exists in this directory
                memory_file = os.path.join(item_path, f"{virtualization}/memory.csv")
                if os.path.exists(memory_file):
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
                            datetime_dirs.append((parsed_datetime, memory_file))
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
        print("No memory files found!")
        return

    # Create the plot
    plt.figure(figsize=(15, 10))

    # Define column names for the memory CSV
    header_cols = [
        "hostname",
        "interval",
        "timestamp",
        "kbmemfree",
        "kbavail",
        "kbmemused",
        "%memused",
        "kbbuffers",
        "kbcached",
        "kbcommit",
        "%commit",
        "kbactive",
        "kbinact",
        "kbdirty",
    ]

    # Create subplots for different memory metrics
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 12))

    # Plot data for each variant
    for variant, memory_file in latest_files.items():
        try:
            # Read the CSV file with explicit column names
            df = pd.read_csv(memory_file, comment="#", names=header_cols)

            if df.empty:
                print(f"No memory data found for {variant}")
                continue

            # Order by row numbers for precise ordering
            df = df.reset_index(drop=True)

            # Convert memory values from KB to MB for better readability
            df["mbmemused"] = df["kbmemused"] / 1024
            df["mbmemfree"] = df["kbmemfree"] / 1024
            df["mbcached"] = df["kbcached"] / 1024
            df["mbcommit"] = df["kbcommit"] / 1024

            # Plot memory used (MB)
            ax1.plot(
                df.index,
                df["mbmemused"],
                label=f"{variant}",
                linewidth=2,
                marker="o",
                markersize=4,
            )

            # Plot memory utilization percentage
            ax2.plot(
                df.index,
                df["%memused"],
                label=f"{variant}",
                linewidth=2,
                marker="s",
                markersize=4,
            )

            # Plot cached memory (MB)
            ax3.plot(
                df.index,
                df["mbcached"],
                label=f"{variant}",
                linewidth=2,
                marker="^",
                markersize=4,
            )

            # Plot commit percentage
            ax4.plot(
                df.index,
                df["%commit"],
                label=f"{variant}",
                linewidth=2,
                marker="d",
                markersize=4,
            )

        except Exception as e:
            print(f"Error processing {variant}: {e}")
            continue

    # Customize each subplot
    ax1.set_xlabel("Time Sample")
    ax1.set_ylabel("Memory Used (MB)")
    ax1.set_title("Memory Used Over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("Time Sample")
    ax2.set_ylabel("Memory Used (%)")
    ax2.set_title("Memory Utilization Percentage Over Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3.set_xlabel("Time Sample")
    ax3.set_ylabel("Cached Memory (MB)")
    ax3.set_title("Cached Memory Over Time")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    ax4.set_xlabel("Time Sample")
    ax4.set_ylabel("Commit (%)")
    ax4.set_title("Memory Commit Percentage Over Time")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Overall title
    fig.suptitle(
        f"Memory Consumption Timeline by Variant - {virtualization.capitalize()} (Latest Results)",
        fontsize=16,
        y=0.98,
    )

    plt.tight_layout()

    # Save the plot
    output_file = f"{outdir}/memory_consumption_timeline_{virtualization}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Plot saved as: {output_file}")

    plt.show()


# Usage examples:
if __name__ == "__main__":
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    # Create comprehensive memory timeline
    create_memory_consumption_timeline("../../trace-result/", "host")
    create_memory_consumption_timeline("../../trace-result/", "guest")
