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

def flux_pde_const_D(D, C_eq, L, T, dt, dx):
    """Solve the 2nd order differential equation of the mass diffusion problem.

    Solves with 2 boundary conditions and 1 initial condition using scipy's solve_ivp.
    The diffusion equation ∂C/∂t = D·∂²C/∂x² is solved using the method of lines,
    where the spatial derivatives are discretized and the resulting system of ODEs
    is solved using an ODE solver.

    Args:
        D (float): Diffusion coefficient.
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
    # ==================================================================
    # SECTION 1: SETUP
    # ==================================================================
    
    # Calculate number of spatial and time points for output
    Nx = int(L / dx) + 1      # Number of grid points in space
    Nt = int(T / dt) + 1      # Number of time points for output
    
    # Create spatial and time grids
    x_grid = np.linspace(0, L, Nx)     # Spatial grid [0, L]
    t_grid = np.linspace(0, T, Nt)     # Time grid [0, T]
    
    # ==================================================================
    # SECTION 2: DEFINE THE ODE SYSTEM
    # ==================================================================
    
    # Initial condition: C(x,0) = 0 for all x except at x=0
    def initial_condition():
        """Create the initial concentration profile.
        
        Returns:
            ndarray: Initial concentration values at each spatial point
        """
        C_init = np.zeros(Nx)
        C_init[0] = C_eq      # Apply boundary condition at x=0 (feed side)
        return C_init
    
    def diffusion_ode(t, C):
        """ODE function for the diffusion equation using method of lines.
        
        This function calculates dC/dt at each spatial point based on the 
        discretized diffusion equation: dC/dt = D·∂²C/∂x²
        
        Args:
            t (float): Current time (not used directly but required by solve_ivp)
            C (ndarray): Current concentration profile
        
        Returns:
            ndarray: Rate of change of concentration (dC/dt) at each spatial point
        """
        # Create array to store rate of change at each point
        dCdt = np.zeros_like(C)
        
        # Calculate second derivative using central difference for interior points
        # ∂²C/∂x² ≈ (C[i+1] - 2·C[i] + C[i-1])/dx²
        for i in range(1, Nx-1):
            dCdt[i] = D * (C[i+1] - 2*C[i] + C[i-1]) / (dx**2)
        
        # Apply boundary conditions
        dCdt[0] = 0      # Fixed concentration at x=0 (feed side)
        dCdt[-1] = 0     # Fixed concentration at x=L (permeate side)
        
        return dCdt
    
    # ==================================================================
    # SECTION 3: SOLVE THE PDE USING solve_ivp
    # ==================================================================
    
    # Solve the PDE using solve_ivp
    print("Solving diffusion equation...")
    sol = solve_ivp(
        diffusion_ode,                     # ODE function
        (0, T),                            # Time span
        initial_condition(),               # Initial condition
        method='BDF',                      # Backward Differentiation Formula (good for stiff problems)
        t_eval=t_grid,                     # Times to output solution
        rtol=1e-4,                         # Relative tolerance
        atol=1e-6                          # Absolute tolerance
    )
    
    # Extract solution at requested time points
    C_surface = sol.y.T  # Transpose to get (time, position) shape
    
    # Ensure boundary conditions are exactly enforced in the solution
    C_surface[:, 0] = C_eq  # x=0 boundary
    C_surface[:, -1] = 0    # x=L boundary
    
    # ==================================================================
    # SECTION 4: CALCULATE FLUX
    # ==================================================================
    
    # Calculate flux at x=L using Fick's first law: J = -D·(∂C/∂x)
    # Approximated with backward difference: ∂C/∂x ≈ (C(L) - C(L-dx))/dx
    flux_values = np.zeros(len(sol.t))
    for i in range(len(sol.t)):
        flux_values[i] = -D * (C_surface[i, -1] - C_surface[i, -2]) / dx
    
    # ==================================================================
    # SECTION 5: POST-PROCESSING
    # ==================================================================
    
    # Convert results to pandas DataFrames for easier data handling
    
    # Concentration profile DataFrame
    df_C_surface = pd.DataFrame(C_surface, columns=[f"x = {x:.3g}" for x in x_grid])
    df_C_surface['Time'] = sol.t
    df_C_surface = df_C_surface[['Time'] + [col for col in df_C_surface.columns if col != 'Time']]
    
    # Flux values DataFrame
    df_flux_values = pd.DataFrame({
        'Time': sol.t,
        'Flux': flux_values
    })
    
    # Theoretical steady-state flux for reference (not used in the calculation)
    steady_state_flux = D * C_eq / L
    print(f"Diffusion equation solved ({len(sol.t)} time points, {Nx} spatial points)")
    print(f"Theoretical steady-state flux: {steady_state_flux:.3e}")
    
    return C_surface, flux_values, df_C_surface, df_flux_values