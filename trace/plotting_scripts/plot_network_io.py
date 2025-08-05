import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

outdir = "./plots"


def create_network_utilization_timeline(
    root_dir="../../trace-result/", virtualization="host"
):
    """
    Creates a timeline plot with network utilization for every variant,
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
                # Check if network.csv exists in this directory
                network_file = os.path.join(item_path, f"{virtualization}/network.csv")
                if os.path.exists(network_file):
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
                            datetime_dirs.append((parsed_datetime, network_file))
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
        print("No network files found!")
        return

    # Define column names for the network CSV
    header_cols = [
        "hostname",
        "interval",
        "timestamp",
        "IFACE",
        "rxpck/s",
        "txpck/s",
        "rxkB/s",
        "txkB/s",
        "rxcmp/s",
        "txcmp/s",
        "rxmcst/s",
        "%ifutil",
    ]

    # Create subplots for different network metrics
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 12))

    # Define target interfaces based on virtualization
    if virtualization == "host":
        target_interfaces = ["tap_cvm", "mtap_cvm"]
    else:  # guest
        target_interfaces = ["enp0s7"]

    # Plot data for each variant
    for variant, network_file in latest_files.items():
        try:
            # Read the CSV file with explicit column names
            df = pd.read_csv(network_file, comment="#", names=header_cols)

            if df.empty:
                print(f"No network data found for {variant}")
                continue

            # Find the active interface for this variant
            active_interface = None
            for iface in target_interfaces:
                iface_data = df[df["IFACE"] == iface]
                if not iface_data.empty and (
                    iface_data["rxkB/s"].sum() > 0 or iface_data["txkB/s"].sum() > 0
                ):
                    active_interface = iface
                    break

            if active_interface is None:
                print(
                    f"No active target interface found for {variant} {virtualization}"
                )
                continue

            # Filter data for the active interface
            iface_df = df[df["IFACE"] == active_interface].reset_index(drop=True)

            if iface_df.empty:
                continue

            # Plot RX throughput (kB/s)
            ax1.plot(
                iface_df.index,
                iface_df["rxkB/s"],
                label=f"{variant} ({active_interface})",
                linewidth=2,
                marker="o",
                markersize=4,
            )

            # Plot TX throughput (kB/s)
            ax2.plot(
                iface_df.index,
                iface_df["txkB/s"],
                label=f"{variant} ({active_interface})",
                linewidth=2,
                marker="s",
                markersize=4,
            )

            # Plot RX packets per second
            ax3.plot(
                iface_df.index,
                iface_df["rxpck/s"],
                label=f"{variant} ({active_interface})",
                linewidth=2,
                marker="^",
                markersize=4,
            )

            # Plot TX packets per second
            ax4.plot(
                iface_df.index,
                iface_df["txpck/s"],
                label=f"{variant} ({active_interface})",
                linewidth=2,
                marker="d",
                markersize=4,
            )

        except Exception as e:
            print(f"Error processing {variant}: {e}")
            continue

    # Customize each subplot
    ax1.set_xlabel("Time Sample")
    ax1.set_ylabel("RX Throughput (kB/s)")
    ax1.set_title("Network RX Throughput Over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("Time Sample")
    ax2.set_ylabel("TX Throughput (kB/s)")
    ax2.set_title("Network TX Throughput Over Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3.set_xlabel("Time Sample")
    ax3.set_ylabel("RX Packets/s")
    ax3.set_title("Network RX Packets Over Time")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    ax4.set_xlabel("Time Sample")
    ax4.set_ylabel("TX Packets/s")
    ax4.set_title("Network TX Packets Over Time")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Overall title
    fig.suptitle(
        f"Network Utilization Timeline by Variant - {virtualization.capitalize()} (Latest Results)",
        fontsize=16,
        y=0.98,
    )

    plt.tight_layout()

    # Save the plot
    output_file = f"{outdir}/network_utilization_timeline_{virtualization}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Plot saved as: {output_file}")

    plt.show()


# Usage example:
if __name__ == "__main__":
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    # Create comprehensive network timeline
    create_network_utilization_timeline("../../trace-result/", "host")
    create_network_utilization_timeline("../../trace-result/", "guest")
