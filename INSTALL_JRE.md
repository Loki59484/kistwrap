# JRE Installation Guide for Kisthelp Wrapper

The computational engine underlying this tool requires a Java Runtime Environment (JRE) to execute properly. If you plan to modify and compile the engine yourself,
you will specifically need the full Java Development Kit (JDK)

## Version Requirements
* **Required Version:** Java 17.x.x.
* **Why:** The engine's `.class` files are compiled targeting class file version 61.0, which strictly corresponds to Java 17.
* **Compatibility:** Running the Kisthelp Wrapper with an older Java version will result in an `UnsupportedClassVersionError` crash.
 Java 17 is the highly compatible version required to run this software in your terminal. 

## Installation Instructions

### Linux (Ubuntu/Debian)
Open your terminal and run the following commands to install the OpenJDK 17 runtime:
'''bash
sudo apt update
sudo apt install openjdk-17-jre
