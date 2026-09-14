"""
Terminal User Interface for Kistwrap to offer users an interactive tool to visualise and manipulate kisthelp.
"""
from textual.containers import Vertical, Horizontal, Center, Grid, VerticalScroll
from textual.widgets.option_list import Option
from textual.app import App, ComposeResult
from kistwrap.core import KisthelpEngine
from datetime import datetime
from pathlib import Path
from textual import work
import logging
import shutil
import time
import os
from textual.widgets import (
    Header,
    Footer, 
    Placeholder, 
    Input, 
    DirectoryTree, 
    Collapsible, 
    ProgressBar, 
    Label, 
    Button,
    OptionList,
    ContentSwitcher, 
    RadioSet, 
    RadioButton,
    Select,
    TabbedContent,
    TabPane,
    RichLog,
    Static
)


# --- Session-Based Log Archiving ---
LOG_FILE = 'kistwrap_debug.log'
ARCHIVE_DIR = 'log_archives'

# If a previous log exists, move it to the archive folder with a timestamp
if os.path.exists(LOG_FILE):
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    # Get the time the old log was last modified
    timestamp = datetime.fromtimestamp(os.path.getmtime(LOG_FILE)).strftime('%Y%m%d_%H%M%S')
    archived_name = os.path.join(ARCHIVE_DIR, f'kistwrap_{timestamp}.log')
    shutil.move(LOG_FILE, archived_name)

# Configure the global logger BEFORE initializing the App
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w', # 'w' explicitly starts a fresh file for the current session
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class FileRow(Horizontal):
    def __init__(self, *children, file_name:str = "", file_path: str = "", **kwargs):
        self.file_name = file_name
        self.file_path = file_path
        
        super().__init__(*children, **kwargs)


class KistwrapTUI(App):
    """A Textual TUI for the KiSThelP computational wrapper."""
    
    BINDINGS = [
        ("ctrl+e", "focus_command", "Enters command mode.")
    ]

    CSS = """
    /* --- Base Layout --- */
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 40 1fr;
        grid-rows: 1fr 2fr auto;
    }

    #command-input {
        column-span: 2;
        border: none;
        border-top: solid white;
        background: $surface;
    }

    /* --- Global Inputs & Placeholders --- */
    Input .input--placeholder {
        color: white 30%;
    }

    Input.active-value .input--placeholder {
        color: white 100%;
    }

    /* --- Global Buttons --- */
    .half-btns {
        margin: 1;
        width: 50%;
    }

    .full-btns {
        margin: 1;
        width: 100%;
    }

    .btn-remove-file {
        min-width: 5;
        width: 2;
        height: 1;
        border: none;
        background: red;
    }

    /* --- Left Sidebar & Variables --- */
    #left-sidebar {
        row-span:2;
        border: solid green;
        height: 100%;
        overflow-y: auto;
        background: $surface;
    }

    #file-progress-panel {
        height:75%;
    }

    #progress-container {
        padding: 1;
        height: auto;
    }

    #calc-menu {
        height: auto;
        border: none;
        background: $surface;
    }

    #temp-pressure-panel {
        border-top: solid cyan;
        background: $background;
        padding: 0;
    }

    #var-buttonholder {
        width: 100%;
    }

    .var-title {
        color: yellow;
        text-style: bold;
        margin-bottom: 1;
    }

    .var-row {
        height: 3;
        width: 100%;
    }

    .var-row Input {
        width: 1fr;
        min-width: 5;
        padding: 0 1;
    }

    /* --- Main Display & Tab Area --- */
    #display-panel {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 35 1fr;
        border: solid cyan;
        row-span: 2;
        background: $background;
    }

    #calc-config-area {
        border-right: solid white 30%;
        padding: 1;
        height: 100%;
    }

    #results-area {
        height: 100%;
    }

    /* --- Setup Wizard: Step 1 (File Selection) --- */
    #setup-tree-container {
        width: 1fr;
        border-right: solid white 30%;
        height: 100%;
        padding: 1;
    }

    #file-container-grid {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 1fr 5;
        padding: 1;
        width: 1fr;
        overflow-y: auto;
    }

    #selected-files-container {
        padding: 1;
        height: 100%;
        padding-bottom: -1;
        width: 1fr;
        overflow-y: auto;
    }

    .selected-file-row {
        height: auto;
        width: 100%;
        margin-bottom: 1;
        align: left middle;
    }

    .selected-file-row Label {
        width: 1fr;
        color: $success;
        padding-left: 1;
    }


    #out-filename-grid {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 1fr 5; /* Stretches the list, anchors the buttons */
        width: 1fr;
        padding:1;
        height: 100%;
    }

    #config-files-container {
        height: 100%;
        overflow-y: auto;
    }

        /* Flattened Configuration Row Styling */
    .config-row {
        height: 3;
        width: 100%;
        margin-bottom: 1;
        border-bottom: solid white 30%;
        align: left middle; /* Vertically centers the button alongside the text */
    }

    .config-label {
        width: 1fr;
        height: 3;
        color: $success;
        padding-left: 1;
    }

    .config-input {
        width: 1fr;
        height: 3;
        border: none;
        content-align: left bottom;
        background: $surface;
    }

    /* --- Execution & Job Explorer Styling --- */
    #sidebar-switcher {
        height: 100%;
        border-right: solid white 30%;
    }

    #job-explorer-area {
        height: 100%;
        layout: grid;
        grid-size: 1 2;
        grid-rows: auto 1fr;
        padding: 1;
    }

    #job-explorer-list {
        height: 100%;
        overflow-y: auto;
        border-top: solid white 30%;
        padding-top: 1;
        margin-top: 1;
    }

    .job-item {
        width: 100%;
        height: auto;
        padding: 1 0;
        content-align: left middle;
    }

"""

    def __init__(self, *args, **kwargs):
        """Initialize the app and setup double-click tracking variables."""
        super().__init__(*args, **kwargs)
        self.last_selected_file = None
        self.last_selected_time = 0.0
        self.engine = KisthelpEngine()


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        logger.debug("Initializing and composing UI widgets.")
        yield Header(show_clock=True)

        # 1. Left Sidebar
        with Vertical(id="left-sidebar"):
            with Vertical(id="file-progress-panel"):
                with Collapsible(title="Calculations Menu", id="calc-collapse", collapsed=False):
                    yield OptionList(
                        Option("1. Molec Properties", id="opt-molec"),
                        Option("2. Reaction Path", id="opt-rpath"),
                        Option("3. Rate Constants", id="opt-rates"),
                        Option("4. Equilibrium", id="opt-equil"),
                        id="calc-menu"
                    )

                with Collapsible(title="Batch Progress", id="progress-collapse", collapsed=True):
                    with Vertical(id="progress-container"):
                        yield Label("Current Job: None", id="current-job-label")
                        yield ProgressBar(total=100, show_eta=True, id="job-progress")
            
            # Interactive Temperature and Pressure Panel
            with Vertical(id="temp-pressure-panel"):
                yield Label("Temperature (K)", classes="var-title")
                with Horizontal(classes="var-row"):
                    yield Input(placeholder="Min: 298", id="t-min")
                    yield Input(placeholder="Max: 1000", id="t-max")
                    yield Input(placeholder="Step: 50", id="t-step")
                
                yield Label("Pressure (atm)", classes="var-title")
                with Horizontal(classes="var-row"):
                    yield Input(placeholder="Min: 1.0", id="p-min")
                    yield Input(placeholder="Max: 1.0", id="p-max")
                    yield Input(placeholder="Step: 0.0", id="p-step")
                    
                with Center(id="var-buttonholder"):
                    with Horizontal():
                        yield Button("Apply", id="apply-btn", variant="primary", classes='half-btns')
                        yield Button("Reset", id="reset-btn", variant="primary", classes='half-btns')
                
        # 2. Central Display Panel (Split Config vs Results)
        with Grid(id="display-panel"):
            
            # Left Sub-Panel: Dynamic Configuration Forms
            # Left Sub-Panel: Master Switcher (Info Mode vs Job Explorer)
            with ContentSwitcher(initial="calc-config-area", id="sidebar-switcher"):

                # State 1: Info Mode (Pre-Execution)
                with ContentSwitcher(initial="opt-molec", id="calc-config-area"):
                    
                    with Vertical(id="opt-molec"):
                        yield Label("Atom/Molecule Calculation.", classes="var-title")
                        yield Static("Saves a .kinp file containing thermodynamic properties of the input atom. Configure parameters in the sidebar.\n\nProceed to the wizard on the right to select files and initiate the batch process.")
                    
                    with Vertical(id="opt-rpath"):
                        yield Label("Reaction Path", classes="var-title")
                        yield Input(placeholder="Number of points (--pts)")
                        yield Input(placeholder="IRC points array")
                        yield Label("Select files in the wizard to continue.")
                    
                    with Vertical(id="opt-rates"):
                        yield Label("Rate Constants", classes="var-title")
                        yield RadioSet(RadioButton("TST"), RadioButton("VTST"), id="theory-set")
                        yield Select([("None", "none"), ("Wigner", "Wig"), ("Eckart", "Eck")], prompt="Tunneling", id="tunnel-select")
                        yield Input(placeholder="Reverse Barrier (-revb)")
                        yield Label("Select files in the wizard to continue.")
                    
                    with Vertical(id="opt-equil"):
                        yield Label("Equilibrium", classes="var-title")
                        yield Placeholder("Bimolecular File Inputs")

                # State 2: Job Explorer (Post-Execution)
                with Vertical(id="job-explorer-area"):
                    yield Label("Execution Status", classes="var-title")
                    yield Label("Processing batch queue...", id="job-status-label")
                    with VerticalScroll(id="job-explorer-list"):
                        with Collapsible(title="Pending Queue", id="queue-pending", collapsed=False):
                            pass
                        with Collapsible(title="Successful Jobs (0)", id="queue-success", collapsed=False):
                            pass
                        with Collapsible(title="Failed Jobs (0)", id="queue-failed", collapsed=False):
                            pass


            with TabbedContent(id="results-area"):
                with TabPane("Calculation Setup", id="tab-setup"):
                    with ContentSwitcher(initial="calc-setup-container", id="setup-switcher"):
                        with Horizontal(id="calc-setup-container"):
                            with Vertical(id="setup-tree-container"):
                                yield Label("1. Double-Click to Add Files", classes="var-title")
                                yield DirectoryTree(os.path.expanduser("~"), id="full-system-tree")
                            
                            with Grid(id="file-container-grid"):
                                with VerticalScroll(id="selected-files-container"):
                                    yield Label("2. Selected Batch Files", classes="var-title")
                                with Horizontal():
                                    yield Button("Clear",id="clear-files", variant="primary", classes="half-btns")
                                    yield Button("Continue",id="cont-selected-files", variant="primary", classes="half-btns")

                        with Horizontal(id="output-filename-setup"):                             
                             with Grid(id="out-filename-grid"):
                                 with VerticalScroll(id="config-files-container"):
                                     yield Label("3. Configure Output Filenames", classes="var-title")
                                 with Horizontal():
                                     yield Button("Back",id="back-to-file-select", variant="primary", classes="half-btns")
                                     yield Button("Run Calculation",id="run-calc", variant="primary", classes="half-btns")
                                     
                with TabPane("Console Logs", id="tab-console"):
                    yield RichLog(id="console-log", highlight=True, markup=True)
                with TabPane("Table Data"):
                    yield Placeholder("DataTable for parsed properties will render here.")
                with TabPane("Arrhenius Plot"):
                    yield Placeholder("Graphing component (Plotext) will render here.")

        # 4. Command Bar
        yield Input(placeholder="Enter commands:", id="command-input")

        yield Footer()

    def update_job_status(self, safe_id: str, status_text: str, color: str = "white") -> None:
        """Safely updates the Job Explorer labels from a background thread."""
        logger.debug(f"Updating job status for {safe_id}: {status_text}")
        try:
            job_label = self.query_one(f"#{safe_id}", Label)
            job_label.update(f"[{color}]{status_text}[/{color}]")
        except Exception:
            pass

    def route_job_label(self, safe_id: str, out_name: str, status: str, color: str, target_queue: str, count: int) -> None:
        """Moves a job label to the success or failed partition."""
        try:
            # Update the collapsible title count
            queue = self.query_one(target_queue, Collapsible)
            queue_title = "Successful Jobs" if "success" in target_queue else "Failed Jobs"
            queue.title = f"{queue_title} ({count})"
            
            # Remove from pending and mount in the new queue
            old_label = self.query_one(f"#{safe_id}", Label)
            old_label.remove()
            queue.mount(Label(f"[{color}]{status}: {out_name}[/{color}]", classes="job-item", id=f"result_{safe_id}"))
        except Exception as e:
            logger.error(f"UI Routing Error: {e}")


    @work(thread=True)
    def execute_kisthelp_batch(self, batch_jobs: list[tuple[str, str, str]], calc_type: str, tunneling: str) -> None:
        """Runs the Java engine, tracks success/failure, and partitions results."""
        logger.info(f"Background worker started for {len(batch_jobs)} jobs.")
        console = self.query_one("#console-log", RichLog)
        
        success_count = 0
        fail_count = 0
        
        for file_name, out_name, safe_id in batch_jobs:
            self.app.call_from_thread(self.update_job_status, safe_id, f"▶ Running: {out_name}", "yellow")
            self.app.call_from_thread(console.write, f"\n[bold yellow]--- Starting Job: {file_name} ---[/bold yellow]")

            job_failed = False
            for line in self.engine.stream_job(calc_type, file_name, out_name, tunneling):
                # Detect crash signatures from the Java engine or subprocess
                if "Process failed with exit code" in line or "Exception in thread" in line or "ERROR:" in line:
                    job_failed = True
                self.app.call_from_thread(console.write, line)
                
            # The routing method handles the status text update automatically now
            if job_failed:
                fail_count += 1
                self.app.call_from_thread(self.route_job_label, safe_id, out_name, "✖ Failed", "red", "#queue-failed", fail_count)
            else:
                success_count += 1
                self.app.call_from_thread(self.route_job_label, safe_id, out_name, "✔ Complete", "green", "#queue-success", success_count)
            
            self.app.call_from_thread(console.write, f"[bold green]--- Finished: {out_name} ---[/bold green]\n")
            logger.info(f"Worker finished job: {out_name}")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks across the app."""
        logger.debug(f"Button pressed: {event.button.id}")
        # 1. Handle Temperature/Pressure buttons
        input_map = {
            "t-min": ("Min","298"), "t-max": ("Max","1000"), "t-step": ("Step","50"),
            "p-min": ("Min","1.0"), "p-max": ("Max","1.0"), "p-step": ("Step","0.0")
        }

        if event.button.id == "apply-btn":
            logger.info("Apply button clicked for Temperature/Pressure variables.")
            for widget_id, prefix in input_map.items():

                input_widget = self.query_one(f"#{widget_id}", Input)
                if input_widget.value.strip():
                    new_val = input_widget.value.strip()
                    input_widget.placeholder = f"{prefix[0]}: {new_val}"
                    input_widget.value = ""
                    input_widget.add_class("active-value")
                    
        elif event.button.id == "reset-btn":
            logger.info("Reset button clicked for Temperature/Pressure variables.")
            for widget_id, prefix in input_map.items():

                input_widget = self.query_one(f"#{widget_id}", Input)
                input_widget.placeholder = f"{prefix[0]}: {prefix[1]}"
                input_widget.value = ""
                input_widget.remove_class("active-value")
        
        # 2. Handle File Selection (Switch to Setup Tab)
        elif event.button.id == "btn-select-files":
            tabs = self.query_one("#results-area", TabbedContent)
            tabs.active = "tab-setup"
            
        # 3. Handle Job Execution
        elif event.button.id == "btn-start-molec":
            self.notify("Batch Job Initiated! Gathering file data...")
            # Execution logic will go here

        # 4. Handle File Removal (Destroy the row if the "-" button is clicked)
        elif event.button.id and event.button.id.startswith("rm_file_"):
            logger.debug(f"Removed selected file row: {event.button.id}")
            event.button.parent.remove()
            
        elif event.button.id and event.button.id.startswith("rm_conf_"):
            logger.debug(f"Removed configuration file row: {event.button.id}")
            event.button.parent.remove()

        elif event.button.id == "clear-files":
            logger.info("Cleared all selected files from Step 1.")
            container = self.query_one("#selected-files-container", VerticalScroll)

        elif event.button.id == "cont-selected-files":
            logger.info("Continue button clicked in file selection step.")
            step1_container = self.query_one("#selected-files-container", VerticalScroll)
            rows = step1_container.query(".selected-file-row")
            
            if not rows:
                logger.warning("Continue clicked but no files were selected.")
                self.notify("Please select at least one file first!", severity="error")
                return
                                
            config_container = self.query_one("#config-files-container", VerticalScroll)
            
            # Clear previous configurations
            children = config_container.query(".config-row")
            config_container.remove_children(children)
            
            # Map selected files to the editable config rows
            for row in rows:
                file_name = str(row.file_name)
                file_path = str(row.file_path)
                # Strip original extension so we don't get double extensions
                base_name = os.path.splitext(file_name)[0]
                safe_id = f"conf_{file_name.replace('.', '_').replace(' ', '_')}"

                # 100% flat layout: Button -> Label -> Input
                new_row = FileRow(
                    Button("-", variant="error", classes="btn-remove-file", id=f"rm_{safe_id}"),
                    Label(file_name, classes="config-label"),
                    Input(value=f"{base_name}.kinp", id=f"out_{safe_id}", classes="config-input"),
                    classes="config-row",
                    id=f"row_{safe_id}",
                    file_name=file_name,
                    file_path=file_path
                )
                config_container.mount(new_row)
            
            # Flip the switcher to the config screen
            switcher = self.query_one("#setup-switcher", ContentSwitcher)
            switcher.current = "output-filename-setup"
            
        elif event.button.id == "back-to-file-select":
            logger.debug("Back button clicked in configuration step.")
            switcher = self.query_one("#setup-switcher", ContentSwitcher)

            switcher.current = "calc-setup-container"
            
        elif event.button.id == "run-calc":
            logger.info("Run Calculation button clicked.")
            
            sidebar_switcher = self.query_one("#sidebar-switcher", ContentSwitcher)
            sidebar_switcher.current = "job-explorer-area"

            # Query the pending queue directly, bypassing the master list
            pending_queue = self.query_one("#queue-pending", Collapsible)
            config_rows = self.query(".config-row")
            
            batch_jobs = []

            for row in config_rows:
                file_name = str(row.file_name)
                file_path = Path(row.file_path).resolve()
                
                kinp_input = row.query_one(".config-input", Input)
                out_name =file_path.parent / kinp_input.value
                
                safe_id = f"job_{file_name.replace('.', '_').replace(' ', '_')}"
                
                job_label = Label(f"⏳ Pending: {out_name}", classes="job-item", id=safe_id)
                # Mount straight into the pending partition
                pending_queue.mount(job_label)
                
                batch_jobs.append((str(file_path), str(out_name), safe_id))

            logger.debug(f"Batch queue assembled with {len(batch_jobs)} jobs: {batch_jobs}")

            tabs = self.query_one("#results-area", TabbedContent)
            tabs.active = "tab-console"

            console = self.query_one("#console-log", RichLog)
            console.focus()
            console.write("[bold cyan]Initializing KiSThelP Batch Execution...[/bold cyan]")
            
            # Dynamically grab the selected calculation type from the left sidebar
            calc_switcher = self.query_one("#calc-config-area", ContentSwitcher)
            selected_calc = calc_switcher.current
            
            # Attempt to grab the tunneling parameter if the user is on the Rates tab
            try:
                tunnel_select = self.query_one("#tunnel-select", Select)
                # Check if the value is a string to avoid Textual's NoSelection object
                tunnel_val = tunnel_select.value if isinstance(tunnel_select.value, str) else "none"
            except Exception:
                tunnel_val = "none"
            
            logger.info(f"Triggering background @work thread for {selected_calc} with tunneling: {tunnel_val}")
            self.execute_kisthelp_batch(batch_jobs, calc_type=selected_calc, tunneling=tunnel_val)


            

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Triggers when a file is selected from the setup directory tree."""
        if event.control.id != "full-system-tree":
            return
            
        file_path = str(event.path)
        current_time = time.monotonic()
        
        # Double-click / Double-tap logic (Must happen within 0.5 seconds)
        # Double-click / Double-tap logic (Must happen within 0.5 seconds)
        if file_path == self.last_selected_file and (current_time - self.last_selected_time) < 0.5:
            logger.debug(f"Double-click registered on file: {file_path}")
            # Reset tracker
            self.last_selected_file = None
            self.last_selected_time = 0.0
        else:
            # First click
            self.last_selected_file = file_path
            self.last_selected_time = current_time
            return
            
        file_name = event.path.name
        safe_id = f"file_{file_name.replace('.', '_').replace(' ', '_')}"

        # Prevent duplicates
        try:
            self.query_one(f"#row_{safe_id}")
            logger.warning(f"Duplicate file addition blocked: {file_name}")
            self.notify("File already added to the batch!", severity="warning")
            return
        except:
            pass
        is_valid, reason =self. engine.validate_output_file(file_path)
        
        if not is_valid:
            logger.warning(f"File validation failed for {file_name}: {reason}")
            self.notify(f"Invalid file: {reason}", severity="error")
            return

        # Create the compact row:  filename.out [ - ]
        logger.info(f"Added file to batch: {file_name}")
        new_row = FileRow(
            Label(file_name),
            Button("-", variant="error", classes="btn-remove-file", id=f"rm_{safe_id}"),
            classes="selected-file-row",
            id=f"row_{safe_id}",
            file_name=file_name,
            file_path=file_path
            
        )
        
        container = self.query_one("#selected-files-container", VerticalScroll)
        container.mount(new_row)
                    
    def action_focus_command(self) -> None:
        """Brings the command input widget to focus"""
        logger.debug("Command input focused via shortcut.")
        command_panel = self.query_one("#command-input", Input)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Switch the configuration panel when a new calculation is selected."""
        logger.info(f"Calculation menu option selected: {event.option.id}")
        switcher = self.query_one("#calc-config-area", ContentSwitcher)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Lock the .kinp extension robustly to prevent editing artifacts."""
        if event.input.id and event.input.id.startswith("out_conf_"):
            val = event.value
            
            # Only intercept if they mess with the actual extension
            if not val.endswith(".kinp"):
                logger.debug(f"Intercepted invalid extension edit on {event.input.id}. Attempted value: {val}")
                            
                
                # 1. Safely extract the base name by slicing at the last dot
                if "." in val:
                    base = val.rsplit(".", 1)[0]
                else:
                    # If they deleted the dot entirely, clear leftover fragments
                    base = val
                    for suffix in ["kinp", "inp", "np", "p"]:
                        if base.endswith(suffix):
                            base = base[:-len(suffix)]
                            break
                
                if not base:
                    base = "output"
                    
                # 2. Silently lock the value and prevent the cursor from jumping
                with event.input.prevent(Input.Changed):
                    logger.debug(f"Auto-corrected extension to: {base}.kinp")
                    event.input.value = f"{base}.kinp"
                    # Pin the cursor back to the base word so it doesn't get trapped in the extension
                    event.input.cursor_position = min(event.input.cursor_position, len(base))


if __name__ == "__main__":
    app = KistwrapTUI()
    app.run()



