import argparse
from pathlib import Path


def get_args():
    """
    Parse command-line arguments and return them
    """
    parser = argparse.ArgumentParser(
        description="Parse command-line arguments for plotting data"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.toml"),
        help="Path to the configuration file (e.g.,config.toml)",
    )
    parser.add_argument(
        "--field",
        type=str,
        required=True,
        help="shortname of variables (e.g., 2t, 10w, 10wg, tp)",
    )

    return parser.parse_args()
