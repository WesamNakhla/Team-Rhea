# Mnemonic Volatility3 GUI

## Overview
Mnemonic Volatility3 GUI is a robust Python/Tkinter application designed for managing volatile memory analysis using Volatility 3. Unlike typical design tools, this application uses a unique development approach integrating ChatGPT with Python/Tkinter, facilitating rapid prototyping and efficient iteration. This GUI allows users to manage memory dumps, execute forensic commands, and customize application preferences...

## Features

### Import Frame
- **Drag and Drop:** Users can drag and drop memory dump files directly into the GUI.
- **Browse Functionality:** Alternatively, users can browse their filesystem to select a memory dump file.

### Workspace Frame
- **Command Execution:** Executes forensic analysis commands with options for custom commands.
- **Interactive UI:** Displays command details and allows selection from a dropdown menu.
- **Progress Tracking:** Visual progress bar for command executions.
- **Output Management:** Tabbed interface for viewing multiple command outputs, with text formatting and highlighting capabilities.

### Preferences Frame
- **Customization:** Users can set global font sizes, line spacing, and other output preferences to tailor the application to their needs.

### Export Frame
- **Data Exporting:** Allows users to compile and export findings into a ZIP file, with options to include or exclude specific types of data.

### Navigation Bar
- **Streamlined Navigation:** Easy access to all frames and functionalities via a top navigation bar.

## Getting Started

### Prerequisites
- Python 3.x
- Tkinter installed with Python (usually comes with Python installation)
- Additional Python packages: `tkinterdnd2`

### Installation
1. Clone the repository:
`git clone https://github.com/yourgithubrepo/mnemonic_volatility3_gui.git`
2. Navigate to the project directory:
`cd mnemonic_volatility3_gui`
### Running the Application
Execute the main Python script to start the application:
`python main.py`

## Contributing
Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## License
We dont know yet.

## Acknowledgments
- Volatility Foundation for Volatility 3
- Our team members and contributors who have invested time in improving this tool.