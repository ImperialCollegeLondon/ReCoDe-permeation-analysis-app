# PDE Solver Implementation for Gas Diffusion

This document explains the implementation of the partial differential equation (PDE) solver used to model gas diffusion through polymer membranes. The implementation uses the Method of Lines approach with SciPy's `solve_ivp` function to solve Fick's Second Law of Diffusion.

## Overview

Gas diffusion through a polymer membrane is governed by Fick's Second Law:

$$\frac{\partial C}{\partial t} = D \frac{\partial^2 C}{\partial x^2}$$

Where:
- $C(x,t)$ is the concentration of gas at position $x$ and time $t$
- $D$ is the diffusion coefficient
- $\frac{\partial C}{\partial t}$ is the rate of change of concentration with time
- $\frac{\partial^2 C}{\partial x^2}$ is the second spatial derivative of concentration

The `flux_pde_const_D` function implements a numerical solution to this equation for specific boundary and initial conditions to simulate gas permeation experiments.

## Implementation Structure

The implementation is divided into five main sections:

1. Setup
2. ODE System Definition
3. PDE Solution
4. Flux Calculation
5. Post-processing

Let's examine each section in detail:

## 1. Setup

```python
def flux_pde_const_D(D, C_eq, L, T, dt, dx):
    """Solve the 2nd order differential equation of the mass diffusion problem.
    
    Args:
        D (float): Diffusion coefficient.
        C_eq (float): Equilibrium concentration.
        L (float): Thickness of the polymer.
        T (float): Total time.
        dt (float): Time step size (used for output points).
        dx (float): Spatial step size.
    """
    # Calculate number of spatial and time points for output
    Nx = int(L / dx) + 1      # Number of grid points in space
    Nt = int(T / dt) + 1      # Number of time points for output
    
    # Create spatial and time grids
    x_grid = np.linspace(0, L, Nx)     # Spatial grid [0, L]
    t_grid = np.linspace(0, T, Nt)     # Time grid [0, T]
```

This section:
- Calculates the number of spatial grid points (`Nx`) and output time points (`Nt`) based on the domain dimensions and step sizes
- Creates uniform spatial and time grids for the simulation
- Sets up the discretization for both space and time domains

## 2. ODE System Definition

```python
    # Initial condition: C(x,0) = 0 for all x except at x=0
    def initial_condition():
        """Create the initial concentration profile."""
        C_init = np.zeros(Nx)
        C_init[0] = C_eq      # Apply boundary condition at x=0 (feed side)
        return C_init
    
    def diffusion_ode(t, C):
        """ODE function for the diffusion equation using method of lines."""
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
```

This section:
- Defines the initial condition function that creates a concentration profile where C(x,0) = 0 everywhere except at the feed side (x=0) where C(0,0) = C_eq
- Implements the core ODE function for the Method of Lines approach:
  - Uses central difference approximation to calculate the second spatial derivative: $\frac{\partial^2 C}{\partial x^2} \approx \frac{C_{i+1} - 2C_i + C_{i-1}}{\Delta x^2}$
  - Defines boundary conditions: constant concentration at the feed side (x=0) and zero concentration at the permeate side (x=L)
  - Returns the rate of change of concentration (dC/dt) at each spatial point

## 3. PDE Solution Using Method of Lines

```python
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
```

This section:
- Solves the PDE using SciPy's `solve_ivp` function with the Method of Lines approach
- Uses the BDF (Backward Differentiation Formula) method, which is well-suited for stiff problems (where different time scales are involved)
- Specifies tolerances to control integration accuracy
- Extracts the solution and reshapes it to have dimensions (time, position)
- Enforces the boundary conditions explicitly to ensure they're satisfied exactly, addressing any numerical drift

## 4. Flux Calculation

```python
    # Calculate flux at x=L using Fick's first law: J = -D·(∂C/∂x)
    # Approximated with backward difference: ∂C/∂x ≈ (C(L) - C(L-dx))/dx
    flux_values = np.zeros(len(sol.t))
    for i in range(len(sol.t)):
        flux_values[i] = -D * (C_surface[i, -1] - C_surface[i, -2]) / dx
```

This section:
- Calculates the gas flux at the downstream face (x=L) using Fick's First Law: $J = -D \frac{\partial C}{\partial x}$
- Approximates the concentration gradient $\frac{\partial C}{\partial x}$ using backward difference: $\frac{\partial C}{\partial x} \approx \frac{C(L) - C(L-\Delta x)}{\Delta x}$
- Stores the flux values for each time point in the simulation

## 5. Post-processing

```python
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
```

This section:
- Converts the numerical results into pandas DataFrames for easier data manipulation and analysis
- Creates a concentration profile DataFrame with position columns and time as a row index
- Creates a flux values DataFrame with time and flux columns
- Calculates the theoretical steady-state flux for reference `(D * C_eq / L)`
- Returns the raw concentration profiles, flux values, and formatted DataFrames

## Mathematical Background

### The Method of Lines

The Method of Lines (MOL) is a technique for solving PDEs by:
1. Discretizing the spatial derivatives to convert the PDE into a system of ODEs
2. Solving the resulting ODE system using standard ODE solvers

For Fick's Second Law:
1. We discretize the spatial domain into Nx points
2. At each point i, we approximate $\frac{\partial^2 C}{\partial x^2}$ using finite differences
3. This yields a system of Nx ODEs of the form $\frac{dC_i}{dt} = f(C_{i-1}, C_i, C_{i+1})$
4. We solve this system using SciPy's `solve_ivp`

### Boundary and Initial Conditions

The simulation uses:
- Initial condition: C(x,0) = 0 for all x except at x=0 where C(0,0) = C_eq
- Boundary conditions:
  - C(0,t) = C_eq (constant concentration at feed side)
  - C(L,t) = 0 (zero concentration at permeate side)

These conditions correspond to a standard time-lag experiment where:
- The membrane is initially free of penetrant gas
- A constant gas pressure is applied at the upstream face
- The downstream face is maintained at zero concentration

## Usage Example

```python
# Example parameters
D = 1e-6  # cm²/s - Diffusion coefficient
C_eq = 1.0  # Equilibrium concentration
L = 0.01  # cm - Membrane thickness
T = 1000  # s - Total simulation time
dt = 1.0  # s - Time step for output
dx = 0.0001  # cm - Spatial step size

# Run the simulation
C_profile, flux, df_C, df_flux = flux_pde_const_D(D, C_eq, L, T, dt, dx)

```

## Advantages of This Implementation

1. **Accuracy**: Uses advanced ODE solvers with adaptive time stepping
2. **Stability**: BDF method is well-suited for stiff diffusion problems
3. **Flexibility**: Can easily modify boundary conditions or diffusion model
4. **Efficiency**: Method of Lines is computationally efficient for 1D problems
5. **Validation**: Provides a theoretical check against steady-state solutions

This implementation allows accurate comparison between experimental time-lag data and theoretical predictions, helping validate the calculated diffusion coefficients.