import argparse
import sys
from kistwrap.tui import KistwrapTUI

def main():
    """Main entry point for the kistwrap CLI."""
    parser = argparse.ArgumentParser(
        description="KiSThelP Python Wrapper - High-throughput kinetics automation."
    )

    # We will add headless batch flags (like --calc, --input) here later.
    parser.add_argument(
        "--tui", 
        action="store_true", 
        help="Force launch the interactive Textual UI."
    )

    args = parser.parse_args()

    # If the user runs `kistwrap` or `kistwrap --tui`, boot the dashboard.
    # Once we add headless flags, we will route them to core.py instead.
    if args.tui or len(sys.argv) == 1:
        app = KistwrapTUI()
        app.run()
    else:
        # Placeholder for future headless execution
        print("Headless mode initiated. (Execution logic pending)")

if __name__ == "__main__":
    main()
