# Kistwrap

**High-Throughput Automation & CLI/TUI Wrapper for KiSThelP**

Kistwrap is an open-source Python wrapper engineered to modernize and automate the KiSThelP computational chemistry engine[span_0](start_span)[span_0](end_span). While KiSThelP is an established standard for calculating thermodynamic and kinetic parameters, its reliance on a Java GUI and single-file processing creates a severe bottleneck for large-scale computational workflows[span_1](start_span)[span_1](end_span). 

Kistwrap solves this by bypassing the Java GUI entirely, wrapping the robust statistical mechanics math inside a modern, asynchronous Python architecture[span_2](start_span)[span_2](end_span). It provides both an interactive Terminal User Interface (TUI) for real-time visualization and a headless CLI for automated, high-throughput batch processing[span_3](start_span)[span_3](end_span).

![Kistwrap TUI Demo](link-to-your-gif-here.gif)
*(Note: Record a brief GIF of the TUI plotting interface and file wizard, and replace this link!)*

---

## ⚡ Key Features

* **Dual-Interface Architecture:** Seamlessly switch between an interactive Textual TUI and a headless `argparse` CLI for automated bash scripting[span_4](start_span)[span_4](end_span).
* **High-Throughput Automation:** Replaces tedious GUI clicks with a custom `.job` file parser, allowing users to queue dozens of molecules with dynamically assigned temperature and pressure ranges.
* **Asynchronous Engine:** Utilizes non-blocking Python background workers to stream Java subprocess execution logs directly to the terminal in real-time.
* **Terminal Data Visualization:** Integrates `pandas` and `plotext` to dynamically parse CSV outputs and render interactive thermodynamic profiles (Gibbs Free Energy, Enthalpy, Entropy) directly in the command line.
* **Intelligent Caching:** Automatically detects previously processed `.kinp` files and prevents redundant engine calculations.

---

## 🛠️ Installation & Setup

Kistwrap operates on a dual-language architecture. The core statistical mechanics engine requires Java, while the automation wrapper runs on Python[span_5](start_span)[span_5](end_span).

**Prerequisites:**
* **Java Development Kit (JDK)** (To compile and run the engine)[span_6](start_span)[span_6](end_span)
* **Python 3.10+** (For the wrapper agent)[span_7](start_span)[span_7](end_span)

**1. Clone the Repository**
```bash
git clone [https://github.com/Loki59484/kistwrap.git](https://github.com/Loki59484/kistwrap.git)
cd kistwrap
