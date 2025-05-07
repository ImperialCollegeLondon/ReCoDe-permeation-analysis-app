# Exercises and Best Practices

## Overview

This document provides exercises to reinforce the concepts covered in the previous sections and offers best practices for extending or adapting this application to your own research. The exercises assume familiarity with the core implementation details discussed in sections [`03-Data-Management-and-Processing.md`](03-Data-Management-and-Processing.md) through [`08-Application-Workflow.md`](08-Application-Workflow.md).

## Exercises

These exercises are designed to help you understand the application's components and explore its capabilities. They primarily focus on teaching best practices that are fundamental in building data pipelines, regardless of the specific domain. They are arranged from easiest to hardest, and it is recommended to work through them in order.

### 1. Flexible Data File Loading

*   **Context:** The current `load_data` function in `data_processing.py` assumes the input file is a standard comma-separated CSV with a specific header row. Real-world data often varies in delimiters (commas, tabs, semicolons) and may have different header configurations or starting rows.
*   **Goal:** Enhance the robustness of data loading to accommodate common variations in CSV file formats.
*   **Task:** Modify the `load_data` function to automatically detect or allow the user to specify the delimiter used in the input CSV file. Additionally, handle potential variations in header presence or starting row for data.
*   **Hint:** Explore the `delimiter` and `header` arguments in [`pandas.read_csv`](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html). Consider adding `try-except` blocks to attempt loading with different delimiters if the initial attempt fails.

### 2. Handling Missing Data Points

*   **Context:** The current analysis assumes complete datasets. Experimental data frequently contains missing values (NaNs), possibly due to sensor errors or data logging issues, which can cause errors in calculations.
*   **Goal:** Implement strategies for dealing with missing numerical values within the time or flux data columns.
*   **Task:** Update the data processing steps (likely within or after `load_data` in `data_processing.py`) to identify and handle rows where time or flux values might be missing. Implement at least one handling strategy (e.g., removing the row, linear interpolation).
*   **Hint:** Use [`isna`](https://pandas.pydata.org/docs/reference/api/pandas.isna.html), [`dropna`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html), or [`interpolate`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html) methods within `pandas.DataFrame`. Consider logging a warning message when missing data is detected and handled, and think about how each strategy might affect the results.

### 3. Robust Column Identification

*   **Context:** The code currently expects specific column names (`'t / s'`, `'cumulative flux / cm^3(STP) cm^-2'`). Data files from different instruments or labs often use different naming conventions (e.g., `'Time'`, `'Flux (cc/m2)'`).
*   **Goal:** Make the analysis less dependent on exact column names in the input file.
*   **Task:** Modify the data loading or processing logic in `data_processing.py` to allow for variations in column names for time and flux. Implement a way to identify the correct columns, such as  by searching for keywords or allowing the user to specify the names, and map them to the internal standard names.
*   **Hint:** You could check `df.columns` after loading and use [`df.rename`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html) to standardise them. Consider using regular expressions or simple string matching (`.str.contains()`) to find potential column names.

### 4. Input File Validation

*   **Context:** Currently, errors related to incorrect file structure (e.g., missing required columns, non-numeric data in expected numeric columns) might only appear later during calculations, leading to potentially confusing error messages.
*   **Goal:** Prevent errors later in the analysis by validating the input file structure early after loading.
*   **Task:** Add checks within `load_data` in `data_processing.py` or immediately after, to verify that the loaded DataFrame contains the necessary columns (time and flux, after handling potential name variations from Exercise 3) and that these columns contain numeric data. Raise informative errors if the validation fails.
*   **Hint:** Check [`df.columns`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.columns.html) against expected columns. Use [`df.dtypes`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html) to check data types, and consider using [`pd.to_numeric`](https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html) with `errors='coerce'` followed by `.isna().any()` to detect non-numeric entries in numeric columns.

### 5. Batch Processing with Error Reporting

*   **Context:** The current GUI workflow processes only one file at a time. It is often handy to analyse multiple experimental runs efficiently. Running them individually is time-consuming, and a single problematic file could halt the entire process if not handled correctly.
*   **Goal:** Enable efficient analysis of multiple datasets while gracefully handling problematic files.
*   **Task:** Create a new function or modify the main analysis workflow (`run_analysis` or its caller in `gui.py`) to accept a list of input file paths. Loop through the files, attempting the full analysis for each. If a file causes an error, catch the specific exception, log the error and the problematic filename, and continue with the next file. Collect and present results only for successfully processed files.
*   **Hint:** Use a `for` loop over the list of file paths. Wrap the analysis call for a single file inside a `try...except` block (e.g., `except (FileNotFoundError, ValueError, KeyError) as e:`). Store successful results in a list or dictionary, and perhaps maintain a separate list for files that caused errors.

## Best Practices for Extension and Adaptation

The following practices offer guidance for adapting this code for your research applications. They are intended as a foundation to help you build a first prototype based on this exemplar, rather than an exhaustive list.

### 1. Modularity and Code Structure

*   **Keep components separate:** Maintain the separation between data processing, core calculations, PDE solving, and the user interface. This makes the code easier to understand, test, and modify.
*   **Use functions effectively:** Break down complex tasks into smaller, reusable functions with clear purposes, as demonstrated by the helper functions (`_setup_grid`, `_calculate_flux`, etc.).
*   **Object-Oriented Programming (OOP):** For more complex applications, consider using classes to encapsulate data and related functionality (e.g., a `MembraneSimulation` class).

### 2. Numerical Methods and Validation

*   **Understand solver limitations:** Be aware of the assumptions and limitations of the chosen numerical methods (e.g., Method of Lines, BDF solver). It is best to consult the SciPy documentation for [`solve_ivp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) and other solvers, including [`ode_int`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html), to choose the best option for your applications.
*   **Grid independence study:** Verify that the numerical solution (concentration profile, flux) does not significantly change when refining the spatial (`dx`) and temporal (`dt`) discretisation.
*   **Parameter sensitivity:** Analyse how sensitive the results are to input parameters (e.g., `rtol`, `atol`, `diffusion_coeff`).
*   **Validate against known solutions:** Whenever possible, test your implementation against analytical solutions or results from literature for simplified cases.

### 3. Data Handling and Management

*   **Input validation:** Add checks to ensure input data (from files or GUI) is in the expected format and range.
*   **Clear units:** Consistently track and document units throughout the calculations, as done in the variable names and comments in `calculations.py`.
*   **Data provenance:** Keep records of the raw data, processing steps, and software versions used to generate results.

## Acknowledgements and Closing Remarks

We appreciate you taking the time to work through this exemplar. This was made possible by the relentless support of the ReCoDe team at Imperial. It was a rewarding project to create, and we hope you found the experience equally enjoyable and valuable.

Code on and never stop learning!

Best regards,

Louis and the ReCoDe team