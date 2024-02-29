# Map Navigator and Route Optimization System

#### Overview
This project aims to provide a versatile and efficient navigation and route optimization system. It includes both a GUI application for interactive navigation and a console-based system for batch processing. The project employs various algorithms and data structures for efficient route calculation, including priority queues and Fibonacci heaps.

#### Components

1. **GUI Application (`GUI.py`)**:
   - Developed using the Kivy framework for cross-platform compatibility and intuitive user interaction.
   - Allows users to select map and query files, visualize routes, and view detailed route information.
   - Features interactive elements such as buttons and file choosers for seamless navigation.

2. **Fibonacci Heap Implementation (`FibHeap.py`)**:
   - Implements the Fibonacci heap data structure, a key component for efficient priority queue operations.
   - Provides methods for inserting, extracting minimum, decreasing key, and merging heaps.
   - Utilizes advanced techniques such as cascading cuts and consolidation to maintain heap structure and ensure optimal performance.

#### Usage
1. **GUI Application**:
   - Execute `GUI.py` to launch the GUI application.
   - Select a map file and a query file using the provided buttons.
   - View route information and visualizations within the application interface.
   - Perform batch processing of queries by executing the "Execute All" button.

2. **Console-Based Navigation**:
   - Utilize the provided algorithms and data structures for navigation and route optimization in console environments.
   - Modify the source code and integrate it into your project as needed.
   - Ensure appropriate input data formats and file paths are provided for seamless execution.

#### Dependencies
- Kivy: A Python framework for rapid development of applications.
- Matplotlib: A plotting library for Python, used for generating route visualizations.
- TQDM: A fast, extensible progress bar for Python and CLI.

#### Requirements
```
Kivy==2.2.1
matplotlib==3.8.2
tqdm==4.66.1
```

#### Notes
- Ensure proper configuration of input and output paths in the source code to prevent errors during execution.
- Experiment with different map and query files to test the system's versatility and performance.
- Feedback and contributions to the project are welcome for further enhancements and optimizations.
