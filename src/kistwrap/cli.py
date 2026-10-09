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
        
    # 2. True Headless Execution (Fast-Path & Batch Jobs)
    elif args.input:
        in_path = Path(args.input).resolve()
        if not in_path.exists():
            print(f"Error: Input file not found: {in_path}")
            sys.exit(1)
            
        engine = KisthelpEngine()
        
        # --- NEW: .job File Batch Processing ---
        if in_path.suffix.lower() == ".job":
            print(f"\n[Kistwrap Batch] Loading Job File: {in_path.name}")
            print("-" * 60)
            
            with open(in_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue
                        
                    parts = [p.strip() for p in line.split(";")]
                    if len(parts) < 5:
                        print(f"[WARNING] Skipping invalid line (requires 5 semicolon-separated parameters): {line}")
                        continue
                        
                    j_in, j_out, j_calc, j_temp, j_press = parts[:5]
                    
                    # Resolve paths relative to where the CLI was executed
                    j_in_path = Path(j_in).resolve()
                    j_out_path = Path(j_out).resolve()
                    
                    print(f"\n▶ Executing: {j_in_path.name} -> {j_out_path.name}")
                    print(f"  Calc: {j_calc} | Temp: {j_temp} | Press: {j_press}")
                    
                    if not j_in_path.exists():
                        print(f"  [ERROR] Input file not found: {j_in_path}")
                        continue
                        
                    for out_line in engine.stream_job(j_calc, str(j_in_path), str(j_out_path), tunneling="none", temp_range=j_temp, pressure_range=j_press):
                        sys.stdout.write(out_line + "\n")
                        sys.stdout.flush()
                        
            print("-" * 60)
            print("Batch processing complete.\n")
            
        # --- EXISTING: Single File Processing ---
        else:
            if args.output:
                out_path = Path(args.output).resolve()
            else:
                out_path = in_path.parent / f"{in_path.stem}.kinp"
            
            print(f"\n[Kistwrap Headless] Starting {args.calc} for {in_path.name}")
            print(f"Temperature: {args.temp} | Pressure: {args.pressure}")
            print("-" * 50)
            
            for line in engine.stream_job(args.calc, str(in_path), str(out_path), tunneling="none", temp_range=args.temp, pressure_range=args.pressure):
                sys.stdout.write(line + "\n")
                sys.stdout.flush()
                
            print("-" * 50)
            print(f"Process complete. Output saved to {out_path}\n")


if __name__ == "__main__":
    main()
