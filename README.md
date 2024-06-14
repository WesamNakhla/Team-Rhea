


# VolGUI

![Logo](img/git/Logo3.png)

## Overview

VolGUI is a Python/Tkinter application designed to simplify volatile memory analysis using Volatility3. This tool provides a user-friendly interface, making it accessible for researchers, investigators, and security professionals involved in digital forensics and security analysis.

## Features

### Import Frame
![ImportFrame](img/git/import_frame.png)
- **Drag and Drop**: Easily import memory dump files by dragging them into the GUI.
- **Browse Functionality**: Alternatively, use a file browser to select memory dump files.

### Workspace Frame
![WorkspaceFrame](img/git/workspace_frame.png)
- **Command Execution**: Execute forensic analysis commands with custom command options.
- **Output Management**: Tabbed interface for viewing multiple command outputs, with highlighting capabilities.
- **Tab Functionalities**: Rearrange tabs by dragging and dropping, and close tabs to manage workspace efficiently.
- **Highlighting**: Users can easily highlight specific sections of the output to enhance analysis and focus on critical data points. There is a button for setting the highlight color, allowing users to choose their preferred color for highlighting. Additionally, there is a remove highlight button to clear any unwanted highlights.
- **File Selection**: The sidebar allows users to quickly select and switch between multiple loaded files. Users can add or remove files for analysis without needing to restart the GUI, facilitating a seamless and efficient workflow.
- **Custom Commands**: Add and manage custom commands to tailor the forensic analysis workflow to specific needs.
- **Input Parameters**: Users can enter custom parameters for each command, providing flexibility and precision in forensic analysis. This feature allows for tailored command execution based on specific investigative needs.
- **Closing Tabs**: Close unnecessary tabs to keep the workspace organized and focused.

### Settings Frame
![SettingsFrame](img/git/settings_frame.png)
- **Path to Volatility3**: Allows users to specify the location of their Volatility3 installation, ensuring the GUI can connect and interact with it seamlessly.
- **Font Sizes**: Users can set font sizes to ensure that text is displayed in a way that best suits their visual comfort levels.
- **Line Spacing**: Users can adjust the line spacing to improve the presentation and readability of output data.
- **Letter Spacing**: Users can adjust the letter spacing to enhance the readability and aesthetics of the text.

### Command Management Frame
![CommandFrame](img/git/command_frame.png)
- **Add Commands**: Expand and customize the list of available forensic analysis commands by adding new commands.
- **Remove Commands**: Simplify and customize the command set to suit specific requirements by removing existing commands.

### Export Frame
![ExportFrame](img/git/export_frame.png)
- **Export Options**: Choose to include the original memory dump file and text formatting (highlighting) in the exported package.
- **Tabbed Output Export**: Each tab in the GUI, representing different analysis outputs or data views, is saved as a separate text file.
- **ZIP File Compilation**: All exported items, including text files with analysis results, the commands used, and the memory dump, are compiled into a single ZIP file. This makes it convenient for users to store, share, or archive their analysis data.
- **Metadata File**: The `metadata.json` file within the ZIP package encapsulates the commands executed, the parameters used, and the output generated. This file is crucial for recreating the analysis environment or for future reference.

## Hotkeys
- **CTRL + F**: Toggle the search function in the Workspace Frame.
- **CTRL + E**: Navigate directly to the Export Frame.
- **CTRL + O**: Open new memory dump files.
- **CTRL + Q**: Quit the program.

## Menu and Navigation
VolGUI features a straightforward menu system that provides easy access to various functions and settings, enhancing the overall user experience. The menu is divided into two main sections: File and Edit.

- **File Menu**:
  - **Open**: Load new memory dump files into the application for analysis.
  - **New**: Start a new analysis session.
  - **Export**: Navigate to the Export Frame to compile and export analysis results.
  - **Exit**: Quit the application.

- **Edit Menu**:
  - **Settings**: Access the Settings Frame to customize font sizes, line spacing, letter spacing, and specify the path to the Volatility3 installation.
  - **Manage Commands**: Open the Command Management Frame to add, remove, or manage forensic analysis commands.
  - **Add Custom Plugins**: Incorporate additional plugins into the GUI to extend its functionality.

## Getting Started

### Prerequisites
- Python 3.x
- Tkinter (usually comes with Python installation)
- Additional Python packages: `Pillow`, `tkinterdnd2`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/WesamNakhla/Team-Rhea.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Team-Rhea
   ```

### Running the Application

Execute the main Python script to start the application:
```bash
python main.py
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository. We appreciate your interest in working with Team Rhea to improve VolGUI.

## License

The license for this project is currently unknown.

## Acknowledgments

Team Rhea: A group of eight students from Høyskolen Kristiania, combining E-Business and Cybersecurity expertise. The team members are:
- Intikhab Alam Khan
- Stephanie Norna Schraml
- Jakob Andar
- Mikael Björkli
- Ummar Amjad
- Mathias Oliver Haslien
- Wesam Nakhla
- Ahmad Taisir Al Aboud

This project started as an Agile school project at Høyskolen Kristiania, as an exam case presented by the company Mnemonic.

Mnemonic: A leading IT security services provider, focusing on digital forensics, managed security services, and security consulting.

Høyskolen Kristiania: A Norwegian university renowned for applied sciences and hands-on learning.

Volatility 3: An open-source framework for memory analysis created by the Volatility Foundation.

## Contact

For more information, please visit our [GitHub repository](https://github.com/WesamNakhla/Team-Rhea).
