"""
data_processing.py
--------------
Module for loading and preprocessing permeation data.
"""

import pandas as pd
import math

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

def correct_baseline(df: pd.DataFrame, baseline: float = 0) -> pd.DataFrame:
    """
    Correct the baseline of the raw data.

    Parameters:
    df (pd.DataFrame): Raw data.
    baseline (float): Baseline value to subtract from the column.

    Returns:
    pd.DataFrame: Baseline-corrected data.
    """
    df = df.copy()
    df['y_CO2_bl / ppm'] = df['y_CO2 / ppm'] - baseline
    return df['y_CO2_bl / ppm']

def calculate_pressure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the pressure in the desired units.

    Parameters:
    df (pd.DataFrame): Data with 'P_cell / barg'.
    conversion_factor (float): Conversion factor from barg to desired pressure units.

    Returns:
    pd.DataFrame: Data with converted pressure units.
    """
    df = df.copy()
    df['P_cell / bar'] = df['P_cell / barg'] + 1.01325  # Convert barg to bar
    return df['P_cell / bar']

def calculate_flux(df: pd.DataFrame, d_cm: float, qN2_mlmin: float = None, unit: str='cm^3 cm^-2 s^-1') -> pd.DataFrame:
    """
    Convert 'y_CO2 / ppm' to 'flux / cm^3(STP) cm^-2 s^-1'.

    Parameters:
    df (pd.DataFrame): Data with 'y_CO2 / ppm'.
    d_cm (float): Thickness of the polymer in cm.
    qN2_mlmin (float): Flow rate of N2 in ml/min. If None, use the column 'qN2 / ml min^-1' from the DataFrame.
    unit (str): Unit of the flux.

    Returns:
    pd.DataFrame: Data with converted flux units.
    """
    df = df.copy()
    
    # Raise an error if the column does not exist
    if 'y_CO2_bl / ppm' not in df.columns:
        raise ValueError("Column 'y_CO2_bl / ppm' does not exist in the DataFrame.")
    
    # Calculate Area of disc
    A_cm2 = (math.pi * d_cm**2) / 4 # [cm^2]
    
    # Specify mass flow rate of N2 in [ml/min]
    if qN2_mlmin is not None:
        df['qN2 / ml min^-1'] = qN2_mlmin
    elif 'qN2 / ml min^-1' not in df.columns:
        raise ValueError("Column 'qN2 / ml min^-1' does not exist in the DataFrame.")
    
    # Calculate flux
    if unit == 'cm^3 cm^-2 s^-1' or unit == 'None':
        df['flux / cm^3(STP) cm^-2 s^-1'] = (df['qN2 / ml min^-1'] / 60) * (df['y_CO2_bl / ppm'] * 1e-6) / A_cm2
    
    return df['flux / cm^3(STP) cm^-2 s^-1']

def calculate_cumulative_flux(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the cumulative flux based on 't / s' and 'y_CO2 / ppm'.

    Parameters:
    df (pd.DataFrame): Preprocessed data.

    Returns:
    pd.DataFrame: Data with cumulative flux.
    """
    df['cumulative flux / cm^3(STP) cm^-2'] = (df['flux / cm^3(STP) cm^-2 s^-1'] * df['t / s'].diff().fillna(0)).cumsum()
    return df['cumulative flux / cm^3(STP) cm^-2']

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
    df = df.copy()
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    if 't / s' not in df.columns:
        raise ValueError("Column 't / s' does not exist in the DataFrame.")
    
    df['gradient'] = (df[column].diff() / df['t / s'].diff())
    df['pct_change_mean'] = (df[column].diff() / df['t / s'].diff()).pct_change().abs().rolling(window=window).mean()
    df['pct_change_min'] = (df[column].diff() / df['t / s'].diff()).pct_change().abs().rolling(window=window).min()
    df['pct_change_max'] = (df[column].diff() / df['t / s'].diff()).pct_change().abs().rolling(window=window).max()
    df['pct_change_median'] = (df[column].diff() / df['t / s'].diff()).pct_change().abs().rolling(window=window).median()
    # stabilisation_index = df[((df['pct_change_mean'] <= threshold)) & (df['pct_change_max'] <= threshold)].index[0]
    stabilisation_index = df[((df['pct_change_mean'] <= threshold))].index[0]
    stabilisation_time = df.loc[stabilisation_index, 't / s']
    return stabilisation_time

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
    df = df.copy()
    
    # Raise an error if the column does not exist
    if 'y_CO2 / ppm' not in df.columns:
        raise ValueError("Column 'y_CO2 / ppm' does not exist in the DataFrame.")
    
    # Baseline correction
    baseline_yCO2 = df.loc[:10, 'y_CO2 / ppm'].mean() # Baseline is the average of the first 10 data points
    df['y_CO2_bl / ppm'] = correct_baseline(df, baseline_yCO2)
    
    # Calculate pressure
    df['P_cell / bar'] = calculate_pressure(df)  
    
    # Calculate flux
    df['flux / cm^3(STP) cm^-2 s^-1'] = calculate_flux(df, d_cm=d_cm, qN2_mlmin=qN2_mlmin, unit='cm^3 cm^-2 s^-1')  # Example conversion factor, thickness, and flow rate
    
    # Calculate cumulative flux
    df['cumulative flux / cm^3(STP) cm^-2'] = calculate_cumulative_flux(df)
    
    # Retain main columns only
    main_cols = ['t / s', 'P_cell / bar', 'T / °C', 'y_CO2 / ppm', 'y_CO2_bl / ppm', 'flux / cm^3(STP) cm^-2 s^-1', 'cumulative flux / cm^3(STP) cm^-2']
    df = df[main_cols]
    
    return df