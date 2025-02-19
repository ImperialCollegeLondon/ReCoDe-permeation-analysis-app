import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from calculations import *
from data_processing import *
from visualisation import *
from util import thickness_dict, qN2_dict, get_time_id
import os

def time_lag_analysis_workflow(datapath: str, L_cm: float, d_cm: float, qN2_mlmin: float = None, stablisation_time_range: tuple = (None, None), display_plot: bool = False, save_plot: bool = False, save_data: bool = False, output_dir: str = '.'):
    """
    Perform the entire time-lag analysis workflow.

    Parameters:
    datapath (pd.DataFrame): Path of raw data.
    L_cm (float): Thickness of the polymer in cm.
    d_cm (float): Diameter of the polymer in cm.
    qN2_mlmin (float): Flow rate of N2 in ml/min. If None, use the column 'qN2 / ml min^-1' from the DataFrame.
    stablisation_time_range (tuple): Tuple containing the start and end times for the stabilisation period.
    display_plot (bool): Whether to display the plots.
    save_plot (bool): Whether to save the plots.
    save_data (bool): Whether to save the results data.
    output_dir (str): Directory to save the plots and data.

    Returns:
    dict: Results of the time-lag analysis including time lag, diffusion coefficient, permeability, solubility coefficient, slope, and intercept.
    """
    # Create directory if not exist
    if save_data or save_plot:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    # Get base name of the file without extension
    base_name = os.path.splitext(os.path.basename(datapath))[0]
    
    # Import data
    df = load_data(datapath)
    
    # Preprocess data
    preprocessed_df = preprocess_data(df, d_cm=d_cm, qN2_mlmin=qN2_mlmin)

    # Checking values in stabilisation_time_range
    if stablisation_time_range[0] is not None and stablisation_time_range[1] is not None:
        if stablisation_time_range[0] >= stablisation_time_range[1]:
            raise ValueError("The first element of stablisation_time_range should be less than the second element.")
    
    # Get stabilisation time
    if stablisation_time_range[0] is not None:
        stabilisation_time = stablisation_time_range[0]
    else:
        stabilisation_time = identify_stabilisation_time(df=preprocessed_df, column='cumulative flux / cm^3(STP) cm^-2', window=70, threshold=0.003)
    
    # Get max time
    if stablisation_time_range[1] is not None:
        max_time = stablisation_time_range[1]
    else:
        max_time = preprocessed_df['t / s'].max()

    # Print the first few rows of the preprocessed data to verify
    stabilisation_index = preprocessed_df.loc[preprocessed_df['t / s'] >= stabilisation_time].index[0]
    print(f'Stabilisation time: {stabilisation_time} s → {max_time} s')
    print('Max time: ', max_time, ' s')
    
    # Capping the upper limit
    preprocessed_df = preprocessed_df.loc[preprocessed_df['t / s'] <= max_time]
    
    # Filter steady-state data
    df_ss = preprocessed_df.loc[(preprocessed_df['t / s'] > stabilisation_time) & (preprocessed_df['t / s'] < max_time)]
    
    # Calculate steady-state flux
    flux_ss = df_ss.loc[:, 'flux / cm^3(STP) cm^-2 s^-1'].mean()
    
    # Calculate normalised flux
    preprocessed_df['normalised flux'] = preprocessed_df['flux / cm^3(STP) cm^-2 s^-1'] / flux_ss
    
    # Perform time-lag analysis
    time_lag, diffusion_coefficient, permeability, solubility_coefficient, pressure, solubility, slope, intercept = time_lag_analysis(preprocessed_df, stabilisation_time, L_cm)

    # Get average temperature
    temperature = preprocessed_df.loc[preprocessed_df.index > stabilisation_index, 'T / °C'].mean()
    
    # Plot the results
    if display_plot or save_plot:
        plot_time_lag_analysis(preprocessed_df, stabilisation_time, slope, intercept)
        if save_plot:
            plt.savefig(f"{output_dir}/{base_name}_time_lag_analysis.svg")

    # Print the results
    print(f'Temperature: {temperature:.0f} °C')
    print(f'Pressure: {pressure:.0f} bar')
    print(f'Time Lag: {time_lag:.3g} s')
    print(f'Slope: {slope:.3g} cm^3(STP) cm^-2 s^-1')
    print(f'Intercept: {intercept:.3g} cm^3(STP) cm^-2')
    print(f'Diffusion Coefficient: {diffusion_coefficient:.3g} cm^2 s^-1')
    print(f'Permeability: {permeability:.3g} cm^3(STP) cm^-1 s^-1 bar^-1')
    print(f'Solubility Coefficient: {solubility_coefficient:.3g} cm^3(STP) cm^-3 bar^-1')
    print(f'Pressure: {pressure:.3g} bar')
    print(f'Solubility: {solubility:.3g} cm^3(STP) cm^-3')    

    # Save diffusivity, solubility, and permeability in dataframe
    results_df = pd.DataFrame({
        'experiment': [base_name],
        'thickness / cm': [L_cm],
        'temperature / °C': [temperature],
        'pressure / bar': [pressure],
        'slope / cm^3(STP) cm^-2 s^-1': [slope],
        'intercept / cm^3(STP) cm^-2': [intercept],
        'time lag / s': [time_lag],
        'diffusion coefficient / cm^2 s^-1': [diffusion_coefficient],
        'solubility coefficient / cm^3(STP) cm^-3 bar^-1': [solubility_coefficient],
        'permeability / cm^3(STP) cm^-1 s^-1 bar^-1': [permeability],
        'solubility / cm^3(STP) cm^-3': [solubility],        
    })

    # Test flux_pde_const_D function
    # pressure = preprocessed_df.loc[preprocessed_df.index > stabilisation_index, 'P_cell / bar'].mean()
    L = L_cm
    T = preprocessed_df.loc[stabilisation_index, 't / s']
    T_final = preprocessed_df['t / s'].iloc[-1]
    C_eq = solubility_coefficient * pressure
    C_profile, flux, df_C, df_flux = flux_pde_const_D(D=diffusion_coefficient, C_eq=C_eq, L=L, T=T_final, dt=1, dx=L/50)
    
    # Export data to .csv
    if save_data:
        try:
            preprocessed_df.to_csv(f"{output_dir}/{base_name}_preprocessed_data.csv", index=False)
            results_df.to_csv(f"{output_dir}/{base_name}_time_lag_analysis.csv", index=False)
            df_C.to_csv(f"{output_dir}/{base_name}_concentration_profile.csv", index=False)
            df_flux.to_csv(f"{output_dir}/{base_name}_flux_profile.csv", index=False)
        except Exception as e:
            print(f"An error occurred while exporting to .csv file: {e}")

    # Plot the flux over time
    if display_plot or save_plot:
        plot_flux_over_time(flux, preprocessed_df, T_final)
        if save_plot:
            plt.savefig(f"{output_dir}/{base_name}_flux_over_time.svg")
        
    # Plot the concentration-location profile
    if display_plot or save_plot:
        plot_concentration_location_profile(C_profile, L, T)
        if save_plot:
            plt.savefig(f"{output_dir}/{base_name}_concentration_location_profile.svg")

    # Plot the concentration profile
    if display_plot or save_plot:
        plot_concentration_profile(C_profile, L, T)
        if save_plot:
            plt.savefig(f"{output_dir}/{base_name}_concentration_profile.svg")
    
    if display_plot:
        plt.show()
    
    return {
        'experiment': base_name,
        'thickness': L_cm,
        'temperature': temperature,
        'pressure': pressure,
        'stabilisation_time': stabilisation_time,
        'slope': slope,
        'intercept': intercept,
        'time_lag': time_lag,
        'diffusion_coefficient': diffusion_coefficient,
        'permeability': permeability,
        'solubility_coefficient': solubility_coefficient,
        'solubility': solubility,
    }, preprocessed_df, C_profile, flux, df_C, df_flux

# Example usage
if __name__ == "__main__":
    # Get the absolute path of the current folder
    current_file_path = os.path.abspath(__file__)   # file
    base_dir = os.path.dirname(current_file_path)   # directory
    
    # Load data
    # exp_names = list(thickness_dict.keys())
    exp_names = list(thickness_dict.keys())[0:1]
    # exp_names = ['S3R1', 'S3R2', 'S3R3', 'S3R4', 'S4R3', 'S4R4', 'S4R5', 'S4R6']
    # location = exp_names.index('RUN_H_75C-100bar')
    # exp_names = exp_names[location:]
    # exp_names = ['RUN_H_25C-50bar', 'RUN_H_25C-100bar_7', 'RUN_H_25C-100bar_8', 'RUN_H_25C-100bar_9', 'RUN_H_25C-200bar_2',
    #              'RUN_H_50C-50bar', 'RUN_H_50C-100bar_2', 'RUN_H_50C-200bar',
    #              'RUN_H_75C-50bar', 'RUN_H_75C-100bar',]
    # exp_names = ['RUN_H_75C-50bar']
    
    # Data file name in the data folder
    excel_abs_paths = [os.path.abspath(os.path.join(base_dir, '../data', f'{exp_name}.xlsx')) for exp_name in exp_names]

    # Save path
    save_folder = os.path.abspath(os.path.join(base_dir, '../output', get_time_id()))
    
    for i, excel_abs_path in enumerate(excel_abs_paths):
        print('Performing time lag analysis for ', exp_names[i])
        print('')
        results = time_lag_analysis_workflow(datapath=excel_abs_path, L_cm=thickness_dict[exp_names[i]], d_cm=1.0, qN2_mlmin=qN2_dict[exp_names[i]], 
                                             stablisation_time_range=(2e4, 3e4),
                                             display_plot=True, save_plot=False, save_data=False, output_dir=save_folder)
        print('')
        print('Time lag analysis done for ', exp_names[i])
        print('_' * 20)
        print('')

