import argparse
import sys
from pathlib import Path
from kistwrap.tui import KistwrapTUI
from kistwrap.core import KisthelpEngine

def main():
    """Main entry point for the kistwrap CLI."""
    parser = argparse.ArgumentParser(
        description="KiSThelP Python Wrapper - High-throughput kinetics automation."
    )

    parser.add_argument("-i", "--input", help="Input file to process.", default=None)
    parser.add_argument("-o", "--output", help="Custom output filename (must end in .kinp).", default=None)
    parser.add_argument("-c", "--calc", help="Calculation type (e.g., opt-molec)", default="opt-molec")
    parser.add_argument("-t", "--temp", help="Temperature (single value e.g. 298, or range 298,1000,50)", default="298")
    parser.add_argument("-p", "--pressure", help="Pressure (single value e.g. 1.0, or range 1.0,10.0,1.0)", default="1.0")
    parser.add_argument("--tui", action="store_true", help="Force launch the interactive Textual UI.")

    args = parser.parse_args()

    # 1. Boot the Interactive TUI
    if args.tui or len(sys.argv) == 1:
        app = KistwrapTUI(
            cli_input=args.input, 
            cli_calc=args.calc,
            cli_out=args.output,
            cli_temp=args.temp,
            cli_press=args.pressure
        )
        app.run()
        
    # 2. True Headless Execution (Fast-Path)
    elif args.input:
        in_path = Path(args.input).resolve()
        if not in_path.exists():
            print(f"Error: Input file not found: {in_path}")
            sys.exit(1)
            
        out_name = args.output if args.output else f"{in_path.stem}.kinp"
        out_path = in_path.parent / out_name
        
        print(f"\n[Kistwrap Headless] Starting {args.calc} for {in_path.name}")
        print(f"Temperature: {args.temp} | Pressure: {args.pressure}")
        print("-" * 50)
        
        engine = KisthelpEngine()
        # Ensure your stream_job method in core.py accepts the pressure_range kwarg!
        for line in engine.stream_job(args.calc, str(in_path), str(out_path), tunneling="none", temp_range=args.temp, pressure_range=args.pressure):
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
            
        print("-" * 50)
        print(f"Process complete. Output saved to {out_path.name}\n")

if __name__ == "__main__":
    main()
