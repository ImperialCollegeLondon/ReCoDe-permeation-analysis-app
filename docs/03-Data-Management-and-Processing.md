# Data Management and Processing

## Data Management in Research

### Best Practices for Experimental Data Management

Good data management is essential for reproducible research. When working with experimental data, consider these practices:

1. **Consistent file naming**: Use descriptive, consistent naming schemes (e.g., `RUN_H_25C-100bar_7.xlsx` clearly indicates temperature and pressure conditions)
2. **Data organization**: Organize data in a logical folder structure with clear separation between raw data and processed outputs
3. **Metadata recording**: Document experimental conditions, sample details, and measurement parameters
4. **Version control**: Track changes to your data processing scripts using version control systems like Git
5. **Data backup**: Regularly back up your research data to prevent loss

### Data Structure for Time-Lag Analysis

For permeation experiments specifically, data should include:

- Time measurements (seconds)
- Pressure readings (bar or barg)
- Temperature readings (°C)
- Gas concentration measurements (ppm)
- Flow rates (ml/min)
- Sample dimensions (thickness, diameter)

## Data Processing Workflow

The application implements a data processing pipeline consisting of several key steps:

### 1. Loading Data

Raw experimental data is loaded from Excel files using the [`load_data`](../src/data_processing.py) function:

```python
def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file (.csv) or Excel file (.xlsx, .xls).
    
    Parameters:
    file_path (str): Path to the file.
    
    Returns:
    pd.DataFrame: Loaded data as a DataFrame.
    """
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv, .xlxs or .xls file.")
```

### 2. Data Preprocessing

The [`preprocess_data`](../src/data_processing.py) function performs several preprocessing steps:

```python
def preprocess_data(df: pd.DataFrame, d_cm: float, qN2_mlmin: float = None) -> pd.DataFrame:
    """
    Preprocess the loaded data.
    
    Parameters:
    df (pd.DataFrame): Raw data.
    d_cm (float): Thickness of the polymer in cm.
    qN2_mlmin (float): Flow rate of N2 in ml/min. If None, use the column 'qN2 / ml min^-1' from the DataFrame.
    
    Returns:
    pd.DataFrame: Preprocessed data.
    """
    # Implementation details...
```

Key preprocessing steps include:

1. **Baseline correction**: Remove background signals from gas concentration measurements
2. **Pressure conversion**: Convert pressure readings to standard units (bar)
3. **Flux calculation**: Calculate gas flux through the membrane
4. **Cumulative flux calculation**: Compute the integrated flux over time

### 3. Stabilization Time Detection

An important aspect of time-lag analysis is determining when steady-state diffusion has been reached:

```python
def identify_stabilisation_time(df: pd.DataFrame, column: str, window: int = 5, threshold: float = 0.001) -> float:
    """
    Identify where flux has stabilised by comparing the rolling fractional changes of gradient of a specified column with respect to 't / s'.
    
    Parameters:
    df (pd.DataFrame): Preprocessed data.
    column (str): Column name to check for stabilisation.
    window (int): Window size for rolling calculation.
    threshold (float): Fractional threshold for determining stabilisation.
    
    Returns:
    stabilisation_time: Time corresponding to where the specified column has stabilised.
    """
    # Implementation details...
```

This automated approach:
- Calculates the gradient of the specified data column
- Examines changes in this gradient over a rolling window
- Identifies when changes fall below a specified threshold

## File Structure and Configuration

### Data Files

The application expects data files in the `data/` directory with experimental data organized in Excel files:

```
data/
    RUN_H_25C-100bar_7.xlsx
    RUN_H_25C-100bar_8.xlsx
    RUN_H_25C-100bar_9.xlsx
    RUN_H_25C-200bar_2.xlsx
    RUN_H_25C-50bar.xlsx
    ...
```

### Configuration Parameters

The [`util.py`](../src/util.py) file contains configuration dictionaries for experimental parameters:

```python
thickness_dict = {
    'RUN_H_25C-50bar': 0.1, 'RUN_H_25C-100bar_7': 0.1, 
    # ... other thickness values
} # [cm]

qN2_dict = {
    'RUN_H_25C-50bar': 8.0, 'RUN_H_25C-100bar_7': 8.0,
    # ... other flow rate values
}  # [ml min^-1]
```

These dictionaries provide essential metadata for each experiment:
- `thickness_dict`: Membrane thickness in cm
- `qN2_dict`: Nitrogen flow rate in ml/min

## Working with the Application

### Data Input Requirements

When using the application, ensure your data file:

1. Contains the following columns:
   - `t / s`: Time in seconds
   - `P_cell / barg`: Pressure in barg
   - `T / °C`: Temperature in degrees Celsius
   - `y_CO2 / ppm`: CO2 concentration in ppm

2. Has consistent units across measurements

3. Is in Excel (.xlsx or .xls) or CSV (.csv) format

### Output Data

The application can generate several output files:

1. **Preprocessed data**: Contains the cleaned and transformed experimental data
2. **Time lag analysis results**: Contains the calculated parameters (diffusion coefficient, permeability, etc.)
3. **Concentration profiles**: Shows how gas concentration changes with position and time
4. **Flux profiles**: Shows the calculated gas flux over time


## Data Flow Diagram

```
+----------------+     +------------------+     +---------------------+
| Raw Data Files |---->| Data Loading     |---->| Data Preprocessing  |
| (.xlsx, .csv)  |     | load_data()      |     | preprocess_data()   |
+----------------+     +------------------+     +---------------------+
                                                          |
                       +------------------+               v
                       | Membrane Data    |-----> +---------------------+
                       | thickness_dict   |       | Data Transformation |
                       | qN2_dict         |       | - Baseline correction
                       +------------------+       | - Unit conversion
                                                  | - Flux calculation
                                                  +---------------------+
                                                          |
                                                          v
                                           +-------------------------------+
                                           | Stabilization Detection       |
                                           | identify_stabilisation_time() |
                                           +-------------------------------+
                                                          |
                                                          v
                                           +-------------------------------+
                                           | Time-Lag Analysis             |
                                           | time_lag_analysis_workflow()  |
                                           +-------------------------------+
                                                          |
                       +-------------------------------------------------+
                       |                   |                             |
                       v                   v                             v
              +----------------+  +----------------+           +------------------+
              | Preprocessed   |  | Analysis       |           | Profile Data     |
              | Data (.csv)    |  | Results (.csv) |           | (.csv)           |
              +----------------+  +----------------+           +------------------+
```

## Extending the Data Processing Pipeline

To implement your own data processing steps:

1. Add new functions to [`data_processing.py`](../src/data_processing.py)
2. Integrate them into the [`preprocess_data`](../src/data_processing.py) function
3. Update the [`time_lag_analysis_workflow`](../src/time_lag_analysis.py) function to use your new processing steps