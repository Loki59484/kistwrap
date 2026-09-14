import subprocess
import os
import logging
from pathlib import Path

# Initialize the logger for this specific module
logger = logging.getLogger(__name__)

class KisthelpEngine:
    """Bridge between Python and the Java KiSThelP engine."""
    
    def __init__(self, engine_dir="kisthelp_engine"):
        self.engine_dir = Path(engine_dir)
        self.classpath = f"{self.engine_dir}/bin:{self.engine_dir}/lib/*"
        self.main_class = "Kistep"
        logger.debug(f"KisthelpEngine initialized. Classpath: {self.classpath}. CWD: {os.getcwd()}")

    def validate_output_file(self, file_path: str) -> tuple[bool, str]:
        """
        Scans a computational chemistry log file to verify it is complete
        and contains the necessary thermodynamic data for KiSThelP.
        Returns a tuple: (is_valid: bool, reason: str).
        """
        path = Path(file_path)
        
        # 1. Surface Check
        valid_extensions = {".log", ".out", ".kinp"}
        if path.suffix.lower() not in valid_extensions:
            return False, f"Invalid extension. Expected .log, .out, or .kinp."
            
        if not path.exists() or path.stat().st_size < 1024:
            return False, "File is suspiciously small or empty."

        # If it is already a parsed .kinp file, bypass the raw log checks
        if path.suffix.lower() == ".kinp":
            return True, "Valid .kinp file."

        try:
            # 2. Read the file efficiently
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            if not lines:
                return False, "File is empty."

            # 3. Termination Check (Scan the last 100 lines backwards)
            terminated_normally = False
            for line in reversed(lines[-100:]):
                # Covers Gaussian and GAMESS standard termination strings
                if "Normal termination" in line or "TERMINATED NORMALLY" in line or "Total times" in line:
                    terminated_normally = True
                    break
                    
            if not terminated_normally:
                return False, "Calculation crashed or did not terminate normally."

            # 4. Thermodynamic Data Check (Scan for frequencies)
            has_freq = False
            for line in lines:
                # Covers Gaussian and GAMESS frequency block headers
                if "Harmonic frequencies" in line or "FREQUENCIES IN CM" in line or "Frequencies --" in line:
                    has_freq = True
                    break
                    
            if not has_freq:
                return False, "No frequency or thermodynamic data found in file."

            return True, "Valid"

        except Exception as e:
            logger.error(f"Validation failed due to file read error: {e}")
            return False, f"Validation error: {str(e)}"

        
    def build_command(self, calc_type: str, input_file: str, output_file: str, tunneling: str = "none") -> list[str]:
        """Constructs the Picocli command array for the Java subprocess."""
        command_map = {
            "opt-tst": "TST",
            "opt-vtst": "VTST",
            "opt-molec": "Molec",
            "opt-rpath": "Rpath",
            "opt-equil": "EQUIL"
        }
        java_cmd = command_map.get(calc_type, "TST")
        
        cmd = [
            "java", "-Djava.awt.headless=true", "-cp", self.classpath, self.main_class, "--headless",
            "calc", java_cmd, 
            "-i", input_file
        ]
        
        if isinstance(tunneling, str) and tunneling.lower() != "none":
            cmd.extend(["--tunnel", tunneling])
            
        logger.debug(f"Built Java Command: {' '.join(cmd)}")
        return cmd



    def stream_job(self, calc_type: str, input_file: str, output_file: str, tunneling: str = "none"):
        """Yields stdout lines one by one for real-time TUI streaming."""
        cmd = self.build_command(calc_type, input_file, output_file, tunneling)
        logger.info(f"Starting subprocess for {input_file} -> {output_file}| command {cmd}")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.getcwd() 
            )
            
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    clean_line = line.strip()
                    
                    if clean_line:
                        logger.debug(f"[JAVA ENGINE] {clean_line}")
                        
                    yield clean_line

                    
            process.wait()
            
            if process.returncode != 0:
                logger.error(f"Java process failed with exit code {process.returncode} for {input_file}")
                yield f"[bold red]Process failed with exit code {process.returncode}[/bold red]"
            else:
                logger.info(f"Successfully completed {input_file}")
                
        except FileNotFoundError as e:
            logger.error(f"FileNotFoundError: Could not find Java executable. {e}")
            yield "[bold red]ERROR: Java executable not found in system PATH.[/bold red]"
        except Exception as e:
            logger.critical(f"Unexpected Python error during subprocess execution: {e}", exc_info=True)
            yield f"[bold red]Critical Python Error: {e}[/bold red]"
