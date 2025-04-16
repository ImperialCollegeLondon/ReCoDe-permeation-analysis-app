"""
calculations.py
--------------------
Module for performing time-lag analysis on permeation data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
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

def _setup_grid(L, T, dx, dt):
    """Set up spatial and time grids for PDE solution.
    
    Args:
        L (float): Thickness of the polymer.
        T (float): Total time.
        dx (float): Spatial step size.
        dt (float): Time step size.
        
    Returns:
        tuple: Spatial grid, time grid, number of spatial points, number of time points.
    """
    # Calculate number of points
    Nx = round(L / dx) + 1
    Nt = round(T / dt) + 1
    
    # Create grids
    x_grid = np.linspace(0, L, Nx)
    t_grid = np.linspace(0, T, Nt)
    
    return x_grid, t_grid, Nx, Nt

def _create_initial_condition(Nx, C_eq):
    """Helper function to create the initial concentration profile.
    
    Args:
        Nx (int): Number of spatial points.
        C_eq (float): Equilibrium concentration.
        
    Returns:
        ndarray: Initial concentration values at each spatial point.
    """
    C_init = np.zeros(Nx)
    C_init[0] = C_eq  # Apply boundary condition at x=0 (feed side)
    return C_init

def _create_diffusion_ode(diffusion_coeff, dx, Nx, C_eq):
    """Helper function to create the ODE function for the diffusion equation.
    
    Args:
        diffusion_coeff (float): Diffusion coefficient.
        dx (float): Spatial step size.
        Nx (int): Number of spatial points.
        C_eq (float): Equilibrium concentration for boundary condition.
        
    Returns:
        function: ODE function for solve_ivp.
    """
    def diffusion_ode(t, C):
        """ODE function for the diffusion equation using method of lines."""
        dCdt = np.zeros_like(C)
        
        # Calculate second derivative using central difference for interior points
        # Vector operation for interior points (1 to Nx-2)
        dCdt[1:-1] = diffusion_coeff * (C[2:] - 2*C[1:-1] + C[:-2]) / (dx**2)
        
        # Apply boundary conditions
        dCdt[0] = 0      # Fixed concentration at x=0 (feed side)
        dCdt[-1] = 0     # Fixed concentration at x=L (permeate side)
        
        return dCdt
    
    return diffusion_ode

def _solve_diffusion_pde(diffusion_coeff, C_eq, L, T, dx, dt):
    """Solve the diffusion PDE using the method of lines.
    
    Args:
        diffusion_coeff (float): Diffusion coefficient.
        C_eq (float): Equilibrium concentration.
        L (float): Thickness of the polymer.
        T (float): Total time.
        dx (float): Spatial step size.
        dt (float): Time step size.
        
    Returns:
        tuple: Solution object, spatial grid, number of spatial points.
    """
    x_grid, t_grid, Nx, Nt = _setup_grid(L, T, dx, dt)
    
    # Ensure dx and dt are consistent with L, Nx and T, Nt
    dx = L / (Nx - 1)
    dt = T / (Nt - 1)
    
    # Create initial condition and ODE function
    initial_condition = _create_initial_condition(Nx, C_eq)
    diffusion_ode = _create_diffusion_ode(diffusion_coeff, dx, Nx, C_eq)
    
    # Solve the PDE using solve_ivp
    print("Solving diffusion equation...")
    sol = solve_ivp(
        diffusion_ode,
        (0, T),
        initial_condition,
        method='BDF',
        t_eval=t_grid,
        rtol=1e-4,
        atol=1e-6
    )
    
    print(f"Diffusion equation solved ({len(sol.t)} time points, {Nx} spatial points)")
    
    return sol, x_grid, Nx

def _prepare_concentration_profile(sol, C_eq):
    """Prepare the concentration profile from the solution.
    
    Args:
        sol: Solution from solve_ivp.
        C_eq (float): Equilibrium concentration.
        
    Returns:
        ndarray: Concentration profile as a function of position x and time t.
    """
    # Extract solution and transpose to get (time, position) shape
    C_surface = sol.y.T
    
    # Ensure boundary conditions are exactly enforced
    C_surface[:, 0] = C_eq  # x=0 boundary
    C_surface[:, -1] = 0    # x=L boundary
    
    return C_surface

def _calculate_flux(diffusion_coeff, C_surface, dx, sol):
    """Calculate flux using Fick's first law.
    
    Args:
        diffusion_coeff (float): Diffusion coefficient.
        C_surface (ndarray): Concentration profile.
        dx (float): Spatial step size.
        sol: Solution from solve_ivp.
        
    Returns:
        ndarray: Flux values at each time point.
    """
    # Calculate flux at x=L using Fick's first law: J = -D·(∂C/∂x)
    flux_values = np.zeros(len(sol.t))
    for i in range(len(sol.t)):
        flux_values[i] = -diffusion_coeff * (C_surface[i, -1] - C_surface[i, -2]) / dx
    
    return flux_values

def _create_dataframes(C_surface, flux_values, sol, x_grid):
    """Create DataFrames for the concentration profile and flux values.
    
    Args:
        C_surface (ndarray): Concentration profile.
        flux_values (ndarray): Flux values.
        sol: Solution from solve_ivp.
        x_grid (ndarray): Spatial grid.
        
    Returns:
        tuple: DataFrames for concentration profile and flux values.
    """
    # Concentration profile DataFrame
    df_C_surface = pd.DataFrame(C_surface, columns=[f"x = {x:.3g}" for x in x_grid])
    df_C_surface['Time'] = sol.t
    df_C_surface = df_C_surface[['Time'] + [col for col in df_C_surface.columns if col != 'Time']]
    
    # Flux values DataFrame
    df_flux_values = pd.DataFrame({
        'Time': sol.t,
        'Flux': flux_values
    })
    
    return df_C_surface, df_flux_values

def solve_constant_diffusivity_model(diffusion_coeff, C_eq, L, T, dt, dx):
    """Solve the 2nd order differential equation of the mass diffusion problem.

    Solves with 2 boundary conditions and 1 initial condition using scipy's solve_ivp.
    The diffusion equation ∂C/∂t = D·∂²C/∂x² is solved using the method of lines.

    Args:
        diffusion_coeff (float): Diffusion coefficient.
        C_eq (float): Equilibrium concentration.
        L (float): Thickness of the polymer.
        T (float): Total time.
        dt (float): Time step size (used for output points).
        dx (float): Spatial step size.

    Returns:
        tuple: A tuple containing:
            - C_surface (ndarray): Concentration profile as a function of position x and time t
            - flux_values (list): Flux values at the given time points
            - df_C_surface (pd.DataFrame): Concentration profile data
            - df_flux_values (pd.DataFrame): Flux profile data
    """
    # Solve the PDE and get basic parameters
    sol, x_grid, Nx = _solve_diffusion_pde(diffusion_coeff, C_eq, L, T, dx, dt)
    
    # Prepare the concentration profile
    C_surface = _prepare_concentration_profile(sol, C_eq)
    
    # Calculate flux values
    flux_values = _calculate_flux(diffusion_coeff, C_surface, dx, sol)
    
    # Create DataFrames for the results
    df_C_surface, df_flux_values = _create_dataframes(C_surface, flux_values, sol, x_grid)
    
    # Calculate theoretical steady-state flux
    steady_state_flux = diffusion_coeff * C_eq / L
    print(f"Theoretical steady-state flux: {steady_state_flux:.3e}")
    
    return C_surface, flux_values, df_C_surface, df_flux_values