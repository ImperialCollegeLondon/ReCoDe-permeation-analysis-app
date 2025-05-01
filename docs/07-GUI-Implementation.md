# GUI Implementation for Time Lag Analysis

## Overview

This document outlines the implementation of the Graphical User Interface (GUI) in `app.py`. The GUI provides an interactive front-end for the time lag analysis workflow, allowing users to select data, input parameters, execute calculations, and visualise results. A snapshot is provided in Figure 1. It leverages the CustomTkinter library for modern UI elements and integrates Matplotlib for plotting.

<img src="assets/GUI-demo.gif" alt="GUI Demo" style="max-width: 600; height: auto;">

*Figure 1: Demonstration of the GUI.*

## Design Philosophy and Structure

The core design aims for clarity and ease of use, separating user inputs from results visualisation.

1.  **Framework Choice**: [`customtkinter`](https://customtkinter.tomschimansky.com/) is a modern UI-library based on Tkinter. It is selected for its modern appearance and theme support, providing a better user experience than standard Tkinter. [`matplotlib`](https://matplotlib.org/) is used for its flexible plotting capabilities, integrated with `customtkinter` via `FigureCanvasTkAgg`.
2.  **Layout Strategy**: The main application window (`App` class) utilises a `grid` layout. It's divided into three primary sections:
    *   **Input Panel (Left)**: Contains all user controls (file selection, parameter entries, buttons) and the numerical results text box (`result_text`). This panel occupies less horizontal space.
    *   **Plot Panel (Right)**: Dedicated to displaying the four key analysis plots. This panel is configured to expand significantly more than the input panel when the window is resized horizontally, ensuring ample space for visualisations.
    *   **Footer (Bottom)**: Displays static information (author, version) and does not expand vertically when the window is resized.

## Designing CustomTkinter Elements

In `customtkinter`, UI elements (or widgets) are typically instantiated as attributes of the main application class (e.g., `self.run_button = ctk.CTkButton(...)`).
*   **Appearance**: Configured through parameters (e.g., `fg_color`, `font`, `width`) passed during creation or by calling the widget's `.configure()` method later.
*   **Behaviour**: Defined by linking actions to events, often using the `command` parameter (for buttons, checkboxes, etc.) to specify a function to call, or by using the `.bind()` method for more general event handling.

To position these elements within the window or within container widgets (like `CTkFrame`), layout managers such as `grid` or `pack` are used. For instance, `widget.grid(row=0, column=1, padx=5, pady=5, sticky='w')` places a widget in a specific row and column within its parent container, adding padding (`padx`, `pady`) for spacing, and controlling alignment (`sticky`). This application primarily uses the `grid` layout manager.

## GUI Components and Logic

The following sections detail the specific widgets used, explaining their configuration and role within the application, following the principles outlined above.

### 1. Input Panel (`input_frame`)

This `CTkFrame` acts as a container, positioned using `grid` in the left column (column 0) and configured with `weight=1` for resizing. It houses the interactive elements for controlling the analysis:

*   **File Selection (`file_combobox`)**:
    *   A `CTkComboBox` widget, populated by scanning the `data_dir` (`get_xlxs_files`).
    *   Its `command` parameter is set to `on_combobox_selected`, triggering autofill logic when a new file is chosen.
    *   Positioned within the `input_frame` using `grid`.
*   **Parameter Input (`d_cm_entry`, `L_cm_entry`, `qN2_mlmin_entry`)**:
    *   Standard `CTkEntry` widgets for essential experimental parameters. Their appearance (e.g., width) is set during instantiation.
    *   Default values are provided for convenience.
    *   Positioned using `grid`.
*   **Stabilisation Time Configuration**:
    *   A `CTkCheckBox` (`use_custom_stab_time_checkbox`) allows switching between automatic detection (default) and manual input. Its `command` parameter links to `toggle_custom_stab_time_entries`.
    *   The `toggle_custom_stab_time_entries` method enables/disables the 'Start time' and 'End time' `CTkEntry` widgets (contained within a separate `CTkFrame`) based on the checkbox state, modifying their `state` configuration. Visual cues (graying out) indicate the disabled state.
    *   A `CTkLabel` (`help_label`) provides a tooltip (`show_tooltip`) explaining the auto-detection logic, using event binding (`bind`) for hover detection.
    *   All elements are positioned using `grid`.
*   **Execution (`run_button`)**:
    *   A `CTkButton` whose `command` parameter is linked to the main `run_analysis` method.
    *   Positioned using `grid`.
*   **Results Display (`result_text`)**:
    *   A `CTkTextbox` used to display formatted numerical results. Its content is updated programmatically within `perform_calculations`.
    *   Positioned using `grid`.
*   **Scaling Controls (`scaling_combobox`, `label_scaling_combobox`)**:
    *   `CTkComboBox` widgets allowing users to adjust UI and plot label scaling.
    *   Their `command` parameters link to `change_scaling` and `change_label_scaling` respectively.
    *   Positioned using `grid`.

### 2. Plot Panel (`plot_frame`)

This `CTkFrame` displays the graphical results, positioned using `grid` in the right column (column 1) and configured with `weight=4`. This higher weight (compared to the Input Panel with `weight=1`) ensures it expands more significantly than the input panel during horizontal resizing:

*   **Plot Integration**: `matplotlib` figures are embedded within individual `CTkFrame` widgets using `FigureCanvasTkAgg`. The canvas widget obtained from `FigureCanvasTkAgg` is then positioned using `grid` within its container frame.
*   **Layout**: The container frames for each plot are arranged in a 2x2 layout within the main `plot_frame` using `grid`.
*   **Plot Generation**: Plots are created by functions in `visualisation.py` (e.g., `plot_time_lag_analysis`) using data stored in `self.calculation_results`. The `update_plots` method handles embedding these figures.
*   **Interactivity**: Each plot's container frame includes a 'Save' `CTkButton`. Its `command` is configured (using a `lambda` function to pass the specific figure) to open a file dialog (`ctk.filedialog.asksaveasfilename`) for exporting the corresponding figure.

### 3. Core Interaction Workflow (`run_analysis`)

The `run_analysis` method orchestrates the main application flow, triggered by the `run_button`:

1.  **Trigger**: Initiated by the "Run Analysis" button's `command`.
2.  **Calculation (`perform_calculations`)**:
    *   Retrieves input values (file path, parameters, stabilisation time choice) from the UI widgets using their `.get()` methods.
    *   Performs basic validation.
    *   Calls the backend `time_lag_analysis_workflow` function from `time_lag_analysis.py` (detailed in [`08-Application-Workflow`](08-Application-Workflow.md)).
    *   Stores the returned results in `self.calculation_results`.
    *   Formats and displays numerical results in the `result_text` box by configuring its content.
3.  **Plotting (`update_plots`)**:
    *   Called after `perform_calculations` or when plot label scaling changes (via `label_scaling_combobox` command).
    *   Clears any existing plots from the `plot_frame`.
    *   Generates the four plots using data from `self.calculation_results`.
    *   Applies the current label scaling factor.
    *   Embeds each plot figure and its associated 'Save' button into the `plot_frame` using `grid`.

This structure ensures that calculations are performed first, and the results are then used to update both the numerical display and the graphical plots by configuring the relevant widgets.

## Data Flow within the Application

The GUI facilitates a clear flow of data from user input to final results:

1.  **User Input Collection**: When `run_analysis` is triggered, values are read directly from UI widgets:
    *   `self.file_combobox.get()` -> Selected data file path.
    *   `self.d_cm_entry.get()`, `self.L_cm_entry.get()`, `self.qN2_mlmin_entry.get()` -> Experimental parameters (converted to floats).
    *   `self.checkbox_var.get()` -> Determines stabilisation time mode (auto/manual).
    *   `self.stab_time_start_entry.get()`, `self.stab_time_end_entry.get()` -> Custom time range (if manual mode).
2.  **Backend Processing (`perform_calculations`)**:
    *   The collected inputs are passed to `time_lag_analysis_workflow` (from `time_lag_analysis.py`).
    *   This function performs the core scientific calculations (data loading, processing, regression, parameter calculation).
    *   It returns a dictionary (`results_dict`) containing numerical results and potentially pandas DataFrames.
3.  **Result Storage**: The returned `results_dict` is stored in the application's state variable `self.calculation_results`.
4.  **Output Display**:
    *   **Numerical**: `perform_calculations` formats key values from `self.calculation_results` into a string and updates the `self.result_text` widget.
    *   **Graphical (`update_plots`)**: The `update_plots` function accesses `self.calculation_results` (specifically the DataFrames and calculated parameters) and passes them to the plotting functions in `visualisation.py`. The generated `matplotlib` figures are then displayed in the `plot_frame`.

This flow ensures separation between the UI layer and the calculation logic, with `self.calculation_results` acting as the bridge.
