import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from typing import Any

# =============================================================================
# TIME LAG ANALYSIS
# =============================================================================

def time_lag_analysis(df: pd.DataFrame, stabilisation_time_s: float, thickness: float) -> tuple:
    """Perform time-lag analysis on the permeation data.
    
    Args:
        df: Preprocessed data containing time and flux measurements.
        stabilisation_time_s: Time after which the flux has stabilized (seconds).
        thickness: Thickness of the polymer membrane (cm).
        
    Returns:
        tuple: A tuple containing:
            time_lag: Calculated time lag (seconds).
            diffusion_coefficient: Diffusion coefficient (cm²/s).
            permeability: Permeability coefficient (cm³(STP) cm⁻² s⁻¹ bar⁻¹).
            solubility_coefficient: Solubility coefficient (cm³(STP) cm⁻³ bar⁻¹).
            pressure: Average pressure used in the measurement (bar).
            solubility: Direct solubility measurement (cm³(STP) cm⁻³).
            slope: Slope of the steady-state region (cm³(STP) cm⁻² s⁻¹).
            intercept: y-intercept of the steady-state fit (cm³(STP) cm⁻²).
            
    Raises:
        ValueError: If the data hasn't been preprocessed correctly.
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

# =============================================================================
# DIFFUSION EQUATION SOLVER
# =============================================================================

def solve_constant_diffusivity_model(diffusion_coeff: float, C_eq: float, L: float, T: float, dt: float, dx: float, debug: bool = False) -> tuple:
    """Solve the diffusion PDE with constant diffusion coefficient.

    Solves the transient diffusion equation (Fick's second law) for a membrane:
    ∂C/∂t = D·∂²C/∂x² 
    
    Args:
        diffusion_coeff: Diffusion coefficient (length²/time).
        C_eq: Equilibrium concentration at upstream boundary (amount/volume).
        L: Thickness of the membrane (length).
        T: Total simulation time (time).
        dt: Time step for output points (time).
        dx: Spatial discretization step (length).
        debug: Whether to print additional debugging information. Defaults to False.

    Returns:
        tuple: A tuple containing:
            C_surface: Concentration profile as function of position and time.
            flux_values: Flux values at the downstream boundary over time.
            df_C_surface: Concentration profile data organized in a DataFrame.
            df_flux_values: Flux profile data organized in a DataFrame.
            
    Note:
        Boundary conditions:
        - C(0,t) = C_eq (upstream/feed side)
        - C(L,t) = 0 (downstream/permeate side)
        
        Initial condition:
        - C(x,0) = 0 for all x > 0
    """
    # Solve the PDE and get basic parameters
    sol, x_grid, Nx = _solve_diffusion_pde(diffusion_coeff, C_eq, L, T, dx, dt)
    
    # Prepare the concentration profile
    C_surface = _prepare_concentration_profile(sol)
    
    # Calculate flux values
    flux_values = _calculate_flux(diffusion_coeff, C_surface, dx)
    
    # Create DataFrames for the results
    df_C_surface, df_flux_values = _create_dataframes(C_surface, flux_values, sol, x_grid)
    
    # Calculate theoretical steady-state flux
    if debug:
        steady_state_flux = diffusion_coeff * C_eq / L
        print(f"Theoretical steady-state flux: {steady_state_flux:.3e}")
    
    return C_surface, flux_values, df_C_surface, df_flux_values

# =============================================================================
# HELPER FUNCTIONS FOR DIFFUSION SOLVER
# =============================================================================

def _solve_diffusion_pde(diffusion_coeff: float, C_eq: float, L: float, T: float, dx: float, dt: float) -> tuple:
    """Solve the diffusion PDE using the method of lines.
    
    Args:
        diffusion_coeff: Diffusion coefficient.
        C_eq: Equilibrium concentration.
        L: Thickness of the polymer.
        T: Total time.
        dx: Spatial step size.
        dt: Time step size.
        
    Returns:
        tuple: A tuple containing:
            sol: Solution object from solve_ivp.
            x_grid: Spatial grid points.
            Nx: Number of spatial points.
    """
    x_grid, t_grid, Nx, Nt = _setup_grid(L, T, dx, dt)
    
    # Ensure dx and dt are consistent with L, Nx and T, Nt
    dx = L / (Nx - 1)
    dt = T / (Nt - 1)
    
    # Create initial condition
    initial_condition = _create_initial_condition(Nx, C_eq)
    
    # Solve the PDE using solve_ivp
    print("Solving diffusion equation...")
    sol = solve_ivp(
        _diffusion_ode,
        (0, T),
        initial_condition,
        method='BDF',
        t_eval=t_grid,
        args=(diffusion_coeff, dx),
        rtol=1e-4,
        atol=1e-6
    )
    
    print(f"Diffusion equation solved ({len(sol.t)} time points, {Nx} spatial points)")
    
    return sol, x_grid, Nx

def _setup_grid(L: float, T: float, dx: float, dt: float) -> tuple:
    """Set up spatial and time grids for PDE solution.
    
    Args:
        L: Thickness of the polymer.
        T: Total time.
        dx: Spatial step size.
        dt: Time step size.
        
    Returns:
        tuple: A tuple containing:
            x_grid: Spatial grid points.
            t_grid: Time grid points.
            Nx: Number of spatial points.
            Nt: Number of time points.
    """
    # Calculate number of points
    Nx = round(L / dx) + 1
    Nt = round(T / dt) + 1
    
    # Create grids
    x_grid = np.linspace(0, L, Nx)
    t_grid = np.linspace(0, T, Nt)
    
    return x_grid, t_grid, Nx, Nt

def _create_initial_condition(Nx: int, C_eq: float) -> np.ndarray:
    """Create the initial concentration profile.
    
    Args:
        Nx: Number of spatial points.
        C_eq: Equilibrium concentration.
        
    Returns:
        ndarray: Initial concentration values at each spatial point.
    """
    C_init = np.zeros(Nx)
    C_init[0] = C_eq  # Apply boundary condition at x=0 (feed side)
    return C_init

def _diffusion_ode(t: float, C: np.ndarray, diffusion_coeff: float, dx: float) -> np.ndarray:
    """Calculate concentration changes for the diffusion equation.
    
    Implements the right-hand side of the ODE system resulting from
    discretizing the diffusion PDE using the method of lines.
    
    Args:
        t: Current time point (not used, but required by solve_ivp).
        C: Current concentration values at each spatial point.
        diffusion_coeff: Diffusion coefficient.
        dx: Spatial step size.
        
    Returns:
        ndarray: Rate of change of concentration at each spatial point.
    """
    dCdt = np.zeros_like(C)
    
    # Calculate second derivative using central difference for interior points
    # Vector operation for interior points (1 to Nx-2)
    dCdt[1:-1] = diffusion_coeff * (C[2:] - 2*C[1:-1] + C[:-2]) / (dx**2)
    
    return dCdt

def _prepare_concentration_profile(sol: Any) -> np.ndarray:
    """Process the solution into a concentration profile.
    
    Args:
        sol: Solution from solve_ivp.
        
    Returns:
        ndarray: Concentration profile as a function of position x and time t.
    """
    # Extract solution and transpose to get more intuitive (time, position) shape for plotting and exporting
    C_surface = sol.y.T
    
    return C_surface

def _calculate_flux(diffusion_coeff: float, C_surface: np.ndarray, dx: float) -> np.ndarray:
    """Calculate flux using Fick's first law.
    
    Args:
        diffusion_coeff: Diffusion coefficient.
        C_surface: Concentration profile.
        dx: Spatial step size.
        
    Returns:
        ndarray: Flux values at each time point.
    """
    # Calculate flux at x=L using Fick's first law: J = -D·(∂C/∂x)
    flux_values = -diffusion_coeff * (C_surface[:, -1] - C_surface[:, -2]) / dx
    
    return flux_values

def _create_dataframes(C_surface: np.ndarray, flux_values: np.ndarray, sol: Any, x_grid: np.ndarray) -> tuple:
    """Create DataFrames for the concentration profile and flux values.
    
    Args:
        C_surface: Concentration profile.
        flux_values: Flux values.
        sol: Solution from solve_ivp.
        x_grid: Spatial grid.
        
    Returns:
        tuple: A tuple containing:
            df_C_surface: Concentration profile data organized by position and time.
            df_flux_values: Flux profile data organized by time.
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