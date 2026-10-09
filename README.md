# Kistwrap

**High-Throughput Automation & CLI/TUI Wrapper for KiSThelP**

Kistwrap is an open-source Python wrapper engineered to modernize and automate
the KiSThelP computational chemistry engine. While KiSThelP is an established
standard for calculating thermodynamic properties and kinetic rate constants,
its reliance on a Java GUI and single-file processing creates a severe
bottleneck for modern, high-throughput computational workflows.

Kistwrap eliminates this bottleneck by bypassing the Java GUI entirely and
wrapping KiSThelP's statistical mechanics backend inside an asynchronous Python
architecture. It offers a dual-interface design: an interactive Terminal User
Interface (TUI) for real-time data visualization and a headless command-line
interface (CLI) for high-throughput batch automation.

---

## 📸 Interface Preview

![Kistwrap TUI Demo](./demo.gif)

---

## ⚡ Key Features

- **Dual-Interface Architecture:** Seamlessly switch between an interactive
  Textual TUI (`kistwrap --tui`) and a headless `argparse` CLI for bash
  scripting.
- **High-Throughput Automation:** Replace manual GUI clicking with a custom
  `.job` file parser to queue dozens of molecules with dynamic temperature and
  pressure ranges.
- **Asynchronous Execution:** Non-blocking Python background workers (`@work`)
  stream Java subprocess logs in real-time directly to the terminal.
- **Terminal Data Visualization:** Integrates `pandas` and `textual-plotext` to
  parse CSV outputs and render interactive thermodynamic plots (Gibbs Free
  Energy, Enthalpy, Entropy, $C_p$) directly in the command line.
- **Intelligent Caching:** Automatically detects previously processed files and
  prevents redundant engine re-calculations.

---

## 🛠️ Installation & Setup

### Option 1: Current Method (Build from Source)

Currently, Kistwrap requires compiling the underlying Java engine locally
alongside setting up the Python wrapper:

#### Prerequisites

- **Java Development Kit (JDK 17+)**: Required to compile and run class file
  version 61.0 binaries.
- **Python 3.10+**: Required for the wrapper agent and Textual TUI.

#### Step-by-Step Build Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Loki59484/kistwrap.git
   cd kistwrap
   ```

2. **Compile the Java Engine:**
   ```bash
   cd kisthelp_engine
   mkdir -p bin
   javac -encoding ISO-8859-1 -cp "lib/*" -d bin @sources.txt src/CLIinterface.java
   cd ..
   ```

3. **Set Up Python Virtual Environment & Install:**
   ```bash
   python3 -m venv kistvenv
   source kistvenv/bin/activate
   pip install -e .
   ```

---

### Option 2: Future Release Plan (Complete Pre-packaged Bundle)

_Coming in future releases:_

- **Pre-compiled Wheel (`pip install kistwrap`):** All Java computational engine
  binaries will be bundled into a pre-compiled `.jar` inside the Python package
  (`kistwrap/bin/kisthelp-engine.jar`), requiring only a basic Java Runtime
  Environment (JRE 17+) without needing `javac` or manual compilation.
- **Standalone Executables:** Pre-packaged single-binary executables will be
  published under
  [GitHub Releases](https://github.com/Loki59484/kistwrap/releases) for
  zero-dependency execution across Linux and HPC cluster environments.

---

## 🚀 Usage

### 1. Interactive TUI Mode

Launch the full terminal dashboard to select files, configure ranges, and view
terminal plots:

```bash
kistwrap --tui
```

### 2. Headless CLI Mode

Execute a single molecular property calculation directly from the terminal
without launching the UI:

```bash
kistwrap -i /path/to/molecule.log -o /path/to/output.kinp -c opt-molec -t 298,1000,50 -p 1.0
```

### 3. High-Throughput Batch Processing (`.job` file)

Create a semicolon-delimited `.job` file to process multiple distinct molecules
with custom parameters:

```text
# master_run.job
# Input_File ; Output_File ; Calc_Type ; Temp_Range ; Pressure_Range

molecule1.log ; mol1.kinp ; opt-molec ; 298 ; 1.0
molecule2.log ; mol2.kinp ; opt-molec ; 298,1000,50 ; 10.0
molecule3.log ; mol3.kinp ; opt-molec ; 298,500,10 ; 1.0,5.0,0.5
```

Execute the batch run with a single command:

```bash
kistwrap -i master_run.job
```

---

## 🗺️ Development Roadmap

- [x] Repository cleanup and `.gitignore` standardization
- [x] Java Picocli CLI interface integration for core engine modules
      (`CLIinterface.java`)
- [x] Dual-interface orchestrator (Textual TUI & `argparse` CLI)
- [x] Molecular Properties pipeline (`calcMolec`) with `pandas` table &
      `textual-plotext` plotting
- [ ] Complete pre-packaged binary/PyPI distribution release with bundled `.jar`
- [ ] Multi-file Rate Constants pipeline (TST, VTST, RRKM) and multi-file UI
      mapping
- [ ] Thermodynamic Equilibrium Constants pipeline (`calcEquil`)
- [ ] Automated CCSD(T) IRC energy injection pipeline

---

## 🏗️ Directory Layout

```text
kistwrap/
├── .gitignore               # Excludes compiled binaries, virtualenvs, and log archives
├── README.md                # Project documentation
├── pyproject.toml           # Python package configuration and console entry points
├── src/
│   └── kistwrap/
│       ├── __init__.py
│       ├── cli.py           # Headless argparse entry point and CLI router
│       ├── core.py          # Subprocess bridge and KisthelpEngine manager
│       └── tui.py           # Interactive Textual TUI dashboard
├── kisthelp_engine/
│   ├── src/                 # Java engine source files (CLIinterface.java)
│   ├── bin/                 # Local compiled .class output folder
│   └── lib/                 # Engine dependencies (Picocli, JMathPlot)
└── test_examples/           # Sample chemistry outputs for validation testing
```

## 📜 License & Acknowledgments

### Kistwrap

The Python automation wrapper agent is licensed under the **MIT License**.

### KiSThelP Engine Attribution & Non-Commercial Use Notice

The underlying computational kinetics backend is based on KiSThelP:

- **Authors & Copyright:** (c) 2013 Sebastien Canneaux, Frederic Bohr, Eric
  Henon (University of Reims Champagne-Ardenne & UST Lille).
- **License & Terms:** KiSThelP is provided for non-commercial use and
  modification, provided author attribution and copyright notices are preserved
  in all copies and associated documentation.
- **Official Website:** kisthelp.univ-reims.fr

### Third-Party Dependencies

- **JMathPlot:** Distributed under the BSD License (Copyright (c) 2003, Yann
  RICHET).
- **Picocli & Apache Commons:** Distributed under the Apache License, Version
  2.0.

> 🤖 **AI-Assisted Project** This project was developed with significant
> contributions from artificial intelligence tools, which assisted in code
> generation, optimization, and architecture design.
