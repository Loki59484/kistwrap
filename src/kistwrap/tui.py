"""
Terminal User Interface for Kistwrap to offer users an interactive tool to visualise and manipulate kisthelp.
"""

import os
import time
from textual.app import App, ComposeResult
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
    TabPane
)
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal, Center, Grid, VerticalScroll

class KistwrapTUI(App):
    """A Textual TUI for the KiSThelP computational wrapper."""
    
    BINDINGS = [
        ("ctrl+e", "focus_command", "Enters command mode.")
    ]

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 40 1fr;
        grid-rows: 1fr 2fr auto;
    }

    /* Placeholder Opacity */
    Input .input--placeholder {
        color: white 30%;
    }
    Input.active-value .input--placeholder {
        color: white 100%;
    }
    
    /* Sidebar Styling */
    #left-sidebar {
        layout: grid;
        grid-size: 1 3;
        row-span: 2;
        border: solid green;
        height: 100%;
        overflow-y: auto;
        background: $surface;
    }

    #file-progress-panel {
        row-span: 2;
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

    .half-btns {
        margin: 1;
        width: 50%;
    }

    #var-buttonholder {
        width: 100%;
        padding: 1;
    }

    /* Main Display Panel */
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

    #command-input {
        column-span: 2;
        border: none;
        border-top: solid white;
        background: $surface;
    }

    /* Split Calculation Setup Panel */


    #setup-tree-container {
        width: 1fr;
        border-right: solid white 30%;
        height: 100%;
        padding: 1;
    }

    #file-container-grid {
        layout:grid;
        grid-size:1 2;
        grid-rows: 1fr 5;
        padding:1;
        padding-bottom:-1;
        width: 1fr;
        overflow-y: auto;
    }

    #selected-files-container {
        padding:1;
        height:100%;
        padding-bottom:-1;
        width: 1fr;
        overflow-y: auto;
    }



    /* Removable File Row Styling */
    .selected-file-row {
        height: auto; /* Makes the row compact */
        width: 100%;
        margin-bottom: 1;
        align: left middle;
    }

    .selected-file-row Label {
        width: 1fr;
        color: $success;
        padding-left: 1;
    }

    .btn-remove-file {
        min-width: 5;
        width: 2;
        height: 1;
        border: none;
        background:red;
    }

    .full-btns {
        margin:1;
        width:100%;
    }
    """

    def __init__(self, *args, **kwargs):
        """Initialize the app and setup double-click tracking variables."""
        super().__init__(*args, **kwargs)
        self.last_selected_file = None
        self.last_selected_time = 0.0

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
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
            with ContentSwitcher(initial="opt-molec", id="calc-config-area"):
                
                with Vertical(id="opt-molec"):
                    yield Label("Thermodynamic Properties", classes="var-title")
                    yield Button("Choose File(s)", id="btn-select-files", variant="primary", classes="full-btns")
                    yield Button("Start Batch Job", id="btn-start-molec", variant="primary", classes="full-btns")
                
                with Vertical(id="opt-rpath"):
                    yield Label("Reaction Path", classes="var-title")
                    yield Input(placeholder="Number of points (--pts)")
                    yield Input(placeholder="IRC points array")
                    yield Button("Run RPath", variant="success")
                
                with Vertical(id="opt-rates"):
                    yield Label("Rate Constants", classes="var-title")
                    yield RadioSet(RadioButton("TST"), RadioButton("VTST"), id="theory-set")
                    yield Select([("None", "none"), ("Wigner", "Wig"), ("Eckart", "Eck")], prompt="Tunneling", id="tunnel-select")
                    yield Input(placeholder="Reverse Barrier (-revb)")
                    yield Button("Run Rates", variant="success")
                
                with Vertical(id="opt-equil"):
                    yield Label("Equilibrium", classes="var-title")
                    yield Placeholder("Bimolecular File Inputs")

            with TabbedContent(id="results-area"):
                with TabPane("Calculation Setup", id="tab-setup"):
                    with Horizontal(id="calc-setup-container"):
                        # Left Side: Full System File Explorer
                        with Vertical(id="setup-tree-container"):
                            yield Label("1. Double-Click to Add Files", classes="var-title")
                            yield DirectoryTree(os.path.expanduser("~"), id="full-system-tree")
                        
                        # Right Side: Added Files List
                        with Grid(id="file-container-grid"):
                            with VerticalScroll(id="selected-files-container"):
                                yield Label("2. Selected Batch Files", classes="var-title")
                            with Horizontal():
                                yield Button("Clear",id="clear-files", variant="primary", classes="half-btns")
                                yield Button("Continue",id="cont-selected-files", variant="primary", classes="half-btns")
                    
                with TabPane("Table Data"):
                    yield Placeholder("DataTable for parsed properties will render here.")
                with TabPane("Arrhenius Plot"):
                    yield Placeholder("Graphing component (Plotext) will render here.")

        # 4. Command Bar
        yield Input(placeholder="Enter commands:", id="command-input")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks across the app."""
        # 1. Handle Temperature/Pressure buttons
        input_map = {
            "t-min": ("Min","298"), "t-max": ("Max","1000"), "t-step": ("Step","50"),
            "p-min": ("Min","1.0"), "p-max": ("Max","1.0"), "p-step": ("Step","0.0")
        }

        if event.button.id == "apply-btn":
            for widget_id, prefix in input_map.items():
                input_widget = self.query_one(f"#{widget_id}", Input)
                if input_widget.value.strip():
                    new_val = input_widget.value.strip()
                    input_widget.placeholder = f"{prefix[0]}: {new_val}"
                    input_widget.value = ""
                    input_widget.add_class("active-value")
                    
        elif event.button.id == "reset-btn":
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
            event.button.parent.remove()

        elif event.button.id == "clear-files":
            container = self.query_one("#selected-files-container", VerticalScroll)
            children_to_remove = container.query(Horizontal)
            container.remove_children(children_to_remove)

        elif event.button.id == "cont-selected-files":
            #EVENT HANDLING REQUIRED HERE
            pass
            
    def on_molec_files_selected(self):
        """Triggers when the selected files for Molecular calculations are submitted using Continue button."""
        panel = self.query_one("#tab-setup")
        panel.clear()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Triggers when a file is selected from the setup directory tree."""
        if event.control.id != "full-system-tree":
            return
            
        file_path = str(event.path)
        current_time = time.monotonic()

        # Double-click / Double-tap logic (Must happen within 0.5 seconds)
        if file_path == self.last_selected_file and (current_time - self.last_selected_time) < 0.5:
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
            self.notify("File already added to the batch!", severity="warning")
            return
        except:
            pass

        # Create the compact row:  filename.out [ - ]
        new_row = Horizontal(
            Label(file_name),
            Button("-", variant="error", classes="btn-remove-file", id=f"rm_{safe_id}"),
            classes="selected-file-row",
            id=f"row_{safe_id}"
        )
        
        container = self.query_one("#selected-files-container", VerticalScroll)
        container.mount(new_row)
                    
    def action_focus_command(self) -> None:
        """Brings the command input widget to focus"""
        command_panel = self.query_one("#command-input", Input)
        command_panel.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Switch the configuration panel when a new calculation is selected."""
        switcher = self.query_one("#calc-config-area", ContentSwitcher)
        switcher.current = event.option.id

if __name__ == "__main__":
    app = KistwrapTUI()
    app.run()



