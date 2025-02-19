"""
calculations.py
--------------------
Module for performing time-lag analysis on permeation data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import figsize_dict, set_plot_style, update_ticks

def time_lag_analysis(df: pd.DataFrame, stabilisation_time_s: float, thickness: float) -> tuple:
    """
    Perform time-lag analysis on the permeation data.

    Parameters:
    df (pd.DataFrame): Preprocessed data.
    stabilisation_time (float): Time after which the flux has stabilised.
    thickness (float): Thickness of the polymer in cm.

    Returns:
    tuple: Calculated time lag (s), diffusion coefficient (cm^2 s^-1), permeability (cm^3 cm^-2 s^-1 bar^-1), and solubility coefficient (cm^3 cm^-3).
    """
    # Raise an error if the data is not preprocessed
    if 'cumulative flux / cm^3(STP) cm^-2' not in df.columns:
        raise ValueError("cumulative flux / cm^3 cm^-2' does not exist. Please preprocess the data first.")
    if 't / s' not in df.columns:
        raise ValueError("'t / s' does not exist. Please preprocess the data first.")
    
    # Fitting straight line to the data
    df_ss = df[df['t / s'] > stabilisation_time_s]
    slope, intercept = np.polyfit(df_ss['t / s'], df_ss['cumulative flux / cm^3(STP) cm^-2'], 1)
    
    # Calculate time_lag
    time_lag = -intercept / slope   # [s]
    
    # Steady state flux
    steady_state_flux = slope   # [cm^3 cm^-2 s^-1]
    
    # Calculate diffusion coefficient
    diffusion_coefficient = thickness**2 / (6 * time_lag)   # [cm^2 s^-1]
    
    # Get pressure
    pressure = df_ss['P_cell / bar'].mean()   # [bar]
    
    # Calculate permeability
    permeability = thickness * steady_state_flux / pressure   # [cm^3(STP) cm^-1 s^-1 bar^-1]
    
    # Solubility
    solubility = slope * thickness / diffusion_coefficient  # [cm^3(STP) cm^-3]
    
    # Calculate solubility coefficient
    solubility_coefficient = permeability / diffusion_coefficient   # [cm^3(STP) cm^-3 bar^-1]    
    
    return time_lag, diffusion_coefficient, permeability, solubility_coefficient, pressure, solubility, slope, intercept

def flux_pde_const_D(D, C_eq, L, T, dt, dx):
    """
    Solve the 2nd order differential equation of the mass diffusion problem with 2 boundary conditions and 1 initial condition.

    Parameters:
    D (float): Diffusion coefficient.
    C_eq (float): Equilibrium concentration.
    L (float): Thickness of the polymer.
    T (float): Total time.
    dt (float): Time step size.
    dx (float): Spatial step size.

    Returns:
    tuple: Concentration profile as a function of position x and time t, and flux values at the given time points.
    """
    # Calculate number of spatial and time steps
    Nx = int(L / dx) + 1
    Nt = int(T / dt) + 1
    
    # Stability condition (Von Neumann stability analysis)
    assert dt <= dx**2 / (2 * D), "Stability condition not met, reduce dt or increase dx"
    
    # Store flux results
    flux_values = []
    
    # Surface plot of C(x, t)
    time = np.linspace(0, T, Nt)
    C_surface = np.zeros((Nt, Nx))  # Initialise surface array

    # Initial condition
    C = np.zeros(Nx)
    
    # Boundary conditions
    C[0] = C_eq
    
    for n in range(0, Nt):
        C_new = C.copy()
        if n > 0:
            for i in range(1, Nx - 1):  # Skip the boundaries
                C_new[i] = C[i] + dt * D * (C[i + 1] - 2 * C[i] + C[i - 1]) / dx**2
        C_new[0] = C_eq
        C_new[-1] = 0
        C = C_new
        C_surface[n, :] = C.copy()

        # Calculate flux at x = L
        flux_L = -D * (C[-1] - C[-2]) / dx  # Flux at x=L using finite difference
        flux_values.append(flux_L)  # Store the flux value
    
    # Convert results to pandas DataFrame
    df_C_surface = pd.DataFrame(C_surface, columns=[f"x = {x:.3g}" for x in np.linspace(0, L, Nx)])
    df_C_surface['Time'] = np.linspace(0, T, Nt)
    df_C_surface = df_C_surface[['Time'] + [col for col in df_C_surface.columns if col != 'Time']]
    df_flux_values = pd.DataFrame(flux_values, columns=['Flux'])
    df_flux_values['Time'] = np.linspace(0, T, Nt)
    df_flux_values = df_flux_values[['Time', 'Flux']]

    return C_surface, flux_values, df_C_surface, df_flux_values

# def flux_pde_fvt_adim(Dt_Tp0)