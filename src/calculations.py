import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

# =============================================================================
# TIME LAG ANALYSIS
# =============================================================================

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

# =============================================================================
# DIFFUSION EQUATION SOLVER
# =============================================================================

def solve_constant_diffusivity_model(diffusion_coeff, C_eq, L, T, dt, dx, debug=False):
    """Solve the diffusion partial differential equation with constant diffusion coefficient.

    Solves the transient diffusion equation (Fick's second law) for a membrane system:
    ∂C/∂t = D·∂²C/∂x² 
    
    Uses the method of lines approach where spatial derivatives are discretized,
    converting the PDE into a system of ODEs that are solved using scipy's solve_ivp.
    
    Boundary conditions:
    - Fixed concentration at x=0 (upstream): C(0,t) = C_eq
    - Fixed concentration at x=L (downstream): C(L,t) = 0
    
    Initial condition:
    - Zero concentration throughout the membrane: C(x,0) = 0 for all x > 0
    
    Args:
        diffusion_coeff (float): Diffusion coefficient [length²/time].
        C_eq (float): Equilibrium concentration at the upstream boundary [amount/volume].
        L (float): Thickness of the membrane [length].
        T (float): Total simulation time [time].
        dt (float): Time step for output points [time].
        dx (float): Spatial step size [length].
        debug (bool, optional): If True, prints additional debugging information. Defaults to False.

    Returns:
        tuple: A tuple containing:
            - C_surface (ndarray): Concentration profile as a function of position x and time t
            - flux_values (list): Flux values at the downstream boundary (x=L) at each time point
            - df_C_surface (pd.DataFrame): Concentration profile data organized in a DataFrame
            - df_flux_values (pd.DataFrame): Flux profile data organized in a DataFrame
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

def _diffusion_ode(t, C, diffusion_coeff, dx):
    """ODE function for the diffusion equation using method of lines.
    
    Args:
        t (float): Current time point (not used, but required by solve_ivp).
        C (ndarray): Current concentration values at each spatial point.
        diffusion_coeff (float): Diffusion coefficient.
        dx (float): Spatial step size.
        
    Returns:
        ndarray: Rate of change of concentration at each spatial point.
    """
    dCdt = np.zeros_like(C)
    
    # Calculate second derivative using central difference for interior points
    # Vector operation for interior points (1 to Nx-2)
    dCdt[1:-1] = diffusion_coeff * (C[2:] - 2*C[1:-1] + C[:-2]) / (dx**2)
    
    return dCdt

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
    def wrapped_diffusion_ode(t, C):
        """Wrapper for the diffusion ODE function with fixed parameters."""
        return _diffusion_ode(t, C, diffusion_coeff, dx)
    
    return wrapped_diffusion_ode

def _prepare_concentration_profile(sol):
    """Prepare the concentration profile from the solution.
    
    Args:
        sol: Solution from solve_ivp.
        
    Returns:
        ndarray: Concentration profile as a function of position x and time t.
    """
    # Extract solution and transpose to get more intuitive (time, position) shape for plotting and exporting
    C_surface = sol.y.T
    
    return C_surface

def _calculate_flux(diffusion_coeff, C_surface, dx):
    """Calculate flux using Fick's first law.
    
    Args:
        diffusion_coeff (float): Diffusion coefficient.
        C_surface (ndarray): Concentration profile.
        dx (float): Spatial step size.
        
    Returns:
        ndarray: Flux values at each time point.
    """
    # Calculate flux at x=L using Fick's first law: J = -D·(∂C/∂x)
    flux_values = -diffusion_coeff * (C_surface[:, -1] - C_surface[:, -2]) / dx
    
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