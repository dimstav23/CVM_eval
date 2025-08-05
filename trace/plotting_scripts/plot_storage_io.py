import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

outdir = "./plots"


def create_storage_io_timeline(root_dir="../../trace-result/", virtualization="host"):
    """
    Creates a timeline plot with storage I/O utilization for every variant,
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
                # Check if disk.csv exists in this directory
                disk_file = os.path.join(item_path, f"{virtualization}/disk.csv")
                if os.path.exists(disk_file):
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
                            datetime_dirs.append((parsed_datetime, disk_file))
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
        print("No disk files found!")
        return

    # Define column names for the disk CSV
    header_cols = [
        "hostname",
        "interval",
        "timestamp",
        "DEV",
        "tps",
        "rkB/s",
        "wkB/s",
        "dkB/s",
        "areq-sz",
        "aqu-sz",
        "await",
        "%util",
    ]

    # Create subplots for different storage metrics
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 12))

    # Define target devices based on virtualization
    if virtualization == "host":
        target_devices = ["nvme1n1", "nvme0n1"]
    else:  # guest
        target_devices = ["vda", "sda"]

    # Plot data for each variant
    for variant, disk_file in latest_files.items():
        try:
            # Read the CSV file with explicit column names
            df = pd.read_csv(disk_file, comment="#", names=header_cols)

            if df.empty:
                print(f"No disk data found for {variant}")
                continue

            # Find the active device for this variant
            active_device = None
            for device in target_devices:
                device_data = df[df["DEV"] == device]
                if not device_data.empty and (
                    device_data["rkB/s"].sum() > 0 or device_data["wkB/s"].sum() > 0
                ):
                    active_device = device
                    break

            if active_device is None:
                print(f"No active target device found for {variant} {virtualization}")
                continue

            # Filter data for the active device
            device_df = df[df["DEV"] == active_device].reset_index(drop=True)

            if device_df.empty:
                continue

            # Plot Read throughput (kB/s)
            ax1.plot(
                device_df.index,
                device_df["rkB/s"],
                label=f"{variant} ({active_device})",
                linewidth=2,
                marker="o",
                markersize=4,
            )

            # Plot Write throughput (kB/s)
            ax2.plot(
                device_df.index,
                device_df["wkB/s"],
                label=f"{variant} ({active_device})",
                linewidth=2,
                marker="s",
                markersize=4,
            )

            # Plot Transactions per second (IOPS)
            ax3.plot(
                device_df.index,
                device_df["tps"],
                label=f"{variant} ({active_device})",
                linewidth=2,
                marker="^",
                markersize=4,
            )

            # Plot Device utilization percentage
            ax4.plot(
                device_df.index,
                device_df["%util"],
                label=f"{variant} ({active_device})",
                linewidth=2,
                marker="d",
                markersize=4,
            )

        except Exception as e:
            print(f"Error processing {variant}: {e}")
            continue

    # Customize each subplot
    ax1.set_xlabel("Time Sample")
    ax1.set_ylabel("Read Throughput (kB/s)")
    ax1.set_title("Storage Read Throughput Over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("Time Sample")
    ax2.set_ylabel("Write Throughput (kB/s)")
    ax2.set_title("Storage Write Throughput Over Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3.set_xlabel("Time Sample")
    ax3.set_ylabel("Transactions per Second (IOPS)")
    ax3.set_title("Storage IOPS Over Time")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    ax4.set_xlabel("Time Sample")
    ax4.set_ylabel("Device Utilization (%)")
    ax4.set_title("Storage Device Utilization Over Time")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Overall title
    fig.suptitle(
        f"Storage I/O Timeline by Variant - {virtualization.capitalize()} (Latest Results)",
        fontsize=16,
        y=0.98,
    )

    plt.tight_layout()

    # Save the plot
    output_file = f"{outdir}/storage_io_timeline_{virtualization}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Plot saved as: {output_file}")

    plt.show()


# Usage examples:
if __name__ == "__main__":
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    # Create comprehensive storage I/O timeline
    create_storage_io_timeline("../../trace-result/", "host")
    create_storage_io_timeline("../../trace-result/", "guest")
