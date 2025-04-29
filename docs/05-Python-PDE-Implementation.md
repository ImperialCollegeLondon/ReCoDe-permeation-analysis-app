# PDE Solver Implementation for Gas Diffusion

## Overview

This document details the implementation of `solve_constant_diffusivity_model` in `calculations.py`, which numerically solves the gas diffusion equation for polymer membranes under specific boundary conditions. The implementation uses the Method of Lines approach with SciPy's `solve_ivp` function to solve Fick's Second Law of Diffusion. For the governing equations (Fick's Second Law) and boundary conditions, please refer to the explanation and visualisations in [`02-Theoretical-Background`](02-Theoretical-Background.md).

## Implementation Structure

The `solve_constant_diffusivity_model` function is implemented through a series of helper functions.The implementation is divided into five main sections:

1. PDE Solution
4. Flux Calculation
5. Post-processing

### 1. PDE Solution

The PDE solving logic is encapsulated inside the `_solve_diffusion_pde` helper function. This includes three main stages:

1. **Setup**

    The discretisation setup is performed using `_setup_grid` helper function.
    ```python
    x_grid, t_grid, Nx, Nt = _setup_grid(L, T, dx, dt)
    ```
    
    The `_setup_grid` function performs the following:

    - Calculates the number of spatial grid points (`Nx`) and output time points (`Nt`) based on the domain dimensions and step sizes.
        ```python
        # Calculate number of points
        Nx = round(L / dx) + 1
        Nt = round(T / dt) + 1
        ```

    - Creates discretisation for both space and time domains.
        ```python
        # Create grids
        x_grid = np.linspace(0, L, Nx)
        t_grid = np.linspace(0, T, Nt)    
        ```


2. **ODE System Definition**

    The PDE initial conditions are created using `_create_initial_condition` helper functions to achieve the following:
        ```python
        # Create initial condition
        initial_condition = _create_initial_condition(Nx, C_eq)
        ```

    The `_create_initial_condition` function performs the following:

    - Creates a concentration profile where C(x,0) = 0 everywhere.
        ```python
        C_init = np.zeros(Nx)
        ```

    - An exception of the initial condition above is at the feed side (x=0) where C(0,0) = C_eq.
        ```python
        C_init[0] = C_eq  # Apply boundary condition at x=0 (feed side)
        ```

3. **PDE Solution**
    
    The Method of Lines is a technique for solving PDEs by:
    1. Discretising the spatial derivatives to convert the PDE into a system of ODEs.
    2. Solving the resulting ODE system using standard ODE solvers.
    
    The PDE is solved using SciPy's [`solve_ivp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) function with the Method of Lines approach.

    ```python
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
    ```

    The arguments passed to `solve_ivp` are:
    - `_diffusion_ode`: Corresponds to the `_diffusion_ode` function that defines the system of Ordinary Differential Equations (ODEs) for `solve_ivp` by calculating the concentration's rate of change (dC/dt) at each spatial point based on the Method of Lines (using discretised PDE). The rate change provided by `_diffusion_ode` is used to step forward in time and determine the concentration profile.
    - `(0, T)`: Specifies the time interval over which the ODE system should be solved (starts at time t=0 and ends at time t=T).
    - `initial_condition`: Corresponds to the previously calculated variable that represents the state of the system (i.e., concentration at each spatial grid point) at the beginning of the time interval (t=0).
    - `method='BDF'`: Uses the Backward Differentiation Formula (BDF), which is suitable for solving stiff ODE systems.
    - `t_eval=t_grid`: Specifies time points (`t_grid`) at which the solver should store and return the solution. Without this, the solver might choose its own internal time steps.
    - `args=(diffusion_coeff, dx)`: Passes additional arguments required by the `_diffusion_ode` function beyond the `t` (time) and `y` (concentration). In this case, it passes the `diffusion_coeff` (diffusion coefficient) and `dx` (spatial step size) needed to calculate the concentration derivatives.
    - `rtol=1e-4` and `atol=1e-6`: Specifies the relative tolerance (`rtol`) and absolute tolerance (`atol`) to control integration accuracy.


### 2. Flux Calculation

The gas flux at the downstream face (x=L) using Fick's First Law is calculated using `_calculate_flux` helper function.


```python
# Calculate flux values
flux_values = _calculate_flux(diffusion_coeff, C_surface, dx)
```

The `_calculate_flux` function approximates the concentration gradient $\frac{\partial C}{\partial x}$ using backward difference: $\frac{\partial C}{\partial x} \approx \frac{C(L) - C(L-\Delta x)}{\Delta x}$.

```python
# Calculate flux at x=L using Fick's first law: J = -D·(∂C/∂x)
flux_values = -diffusion_coeff * (C_surface[:, -1] - C_surface[:, -2]) / dx
```

### 3. Post-processing

After the PDE solution is obtained amd the flux profile is calculated, the following is performed:

1. Creates a concentration profile DataFrame with position columns and time as a row index.
    ```python
    # Transpose the solution array to get more common dimensions (time, position) instead of (position, time)
    # for easier visualisation and data processing in downstream functions
    C_surface = _prepare_concentration_profile(sol)
    ```

2. Converts the numerical results into pandas DataFrames for easier data manipulation and analysis.
    ```python
    # Calculate flux values
    flux_values = _calculate_flux(diffusion_coeff, C_surface, dx)
    ```

## Benefits of This Approach

Using `solve_ivp` offers the many benefits, including:
1. **Accuracy**: Uses advanced ODE solvers with adaptive time stepping.
2. **Stability**: BDF method is well-suited for stiff diffusion problems.
3. **Efficiency**: Method of Lines is computationally efficient for 1D problems.
4.  **Speed**: Utilises a pre-built, tested solver, reduces development time and potential errors compared to implementing a custom solver.

The concentration profile and flux calculated in this implementation enable a direct comparison with experimental flux (detailed in  [`06-Scientific-Visualisation`](06-Scientific-Visualiation.md)). This comparison validates the diffusion coefficient used in the model. Within the full application workflow (detailed in [`08-Application-Workflow`](08-Application-Workflow.md)), this validation step helps to verify the diffusion coefficient derived from the graphical time lag analysis.