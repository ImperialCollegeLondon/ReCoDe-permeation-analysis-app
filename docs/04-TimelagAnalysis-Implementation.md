# Time Lag Analysis Core Calculation Implementation

This document explains how the core calculation steps of time lag analysis are implemented in the `time_lag_analysis` function within the application code. This function handles the central analytical calculations that convert experimental permeation data into gas transport parameters.

## Core Calculation Steps

The `time_lag_analysis` function implements four key computational steps:

1. Linear Regression of Steady-State Data
2. Time Lag Calculation
3. Diffusion Coefficient Determination
4. Permeability and Solubility Calculation

These steps constitute the analytical core of the time lag method, following data preprocessing and stabilization time detection (which are covered in separate documentation).

## Implementation in the `time_lag_analysis` Function

The `time_lag_analysis` function in `time_lag_analysis.py` implements all four core calculation steps:

```python
def time_lag_analysis(df: pd.DataFrame, stabilisation_time_s: float, thickness: float) -> tuple:
    """
    Perform time-lag analysis on the permeation data.

    Parameters:
    df (pd.DataFrame): Preprocessed data.
    stabilisation_time_s (float): Time after which the flux has stabilised.
    thickness (float): Thickness of the polymer in cm.

    Returns:
    tuple: Calculated time lag (s), diffusion coefficient (cm^2 s^-1), permeability, and solubility coefficient.
    """
    # Filter to steady-state data
    df_ss = df[df['t / s'] > stabilisation_time_s]
    
    # Fitting straight line to the steady-state data
    slope, intercept = np.polyfit(df_ss['t / s'], df_ss['cumulative flux / cm^3(STP) cm^-2'], 1)
    
    # Calculate time lag
    time_lag = -intercept / slope   # [s]
    
    # Calculate diffusion coefficient
    diffusion_coefficient = thickness**2 / (6 * time_lag)   # [cm^2 s^-1]
    
    # Get pressure
    pressure = df_ss['P_cell / bar'].mean()   # [bar]
    
    # Calculate permeability
    permeability = thickness * slope / pressure   # [cm^3(STP) cm cm^-2 s^-1 bar^-1]
    
    # Calculate solubility coefficient
    solubility_coefficient = permeability / diffusion_coefficient   # [cm^3(STP) cm^-3 bar^-1]
    
    # Calculate solubility (concentration)
    solubility = solubility_coefficient * pressure
    
    return time_lag, diffusion_coefficient, permeability, solubility_coefficient, pressure, solubility, slope, intercept
```

Let's examine each step of this implementation:

### 1. Linear Regression of Steady-State Data

The function begins by isolating the steady-state region and performing linear regression:

```python
# Filter to steady-state data
df_ss = df[df['t / s'] > stabilisation_time_s]

# Fitting straight line to the steady-state data
slope, intercept = np.polyfit(df_ss['t / s'], df_ss['cumulative flux / cm^3(STP) cm^-2'], 1)
```

The core calculation uses NumPy's `polyfit` function to perform linear regression on the steady-state portion of the cumulative flux curve. This produces two critical parameters:

- `slope`: Represents the steady-state permeation rate through the membrane
- `intercept`: Used to determine the time lag

The implementation isolates the steady-state region by filtering the DataFrame to include only data points collected after the stabilization time.

### 2. Time Lag Calculation

The time lag (θ) is calculated by finding the x-intercept of the steady-state line:

```python
# Calculate time lag
time_lag = -intercept / slope   # [s]
```

Mathematically, the x-intercept is found by setting y = 0 in the equation y = mx + b:
0 = slope × time_lag + intercept
time_lag = -intercept / slope

This calculation provides the time lag (θ), which represents the delay between applying a concentration gradient across the membrane and reaching steady-state permeation.

### 3. Diffusion Coefficient Determination

The diffusion coefficient (D) is calculated using the fundamental relationship derived from Fick's second law:

```python
# Calculate diffusion coefficient
diffusion_coefficient = thickness**2 / (6 * time_lag)   # [cm^2 s^-1]
```

This equation (D = L²/6θ) is derived from the analytical solution to Fick's second law for the specific boundary conditions of the time lag experiment:
- Initially gas-free membrane (C(x,0) = 0)
- Constant upstream concentration (C(0,t) = C₀)
- Zero downstream concentration (C(L,t) = 0)

The coefficient value of 6 in the denominator results from this specific analytical solution. The calculation provides the diffusion coefficient in cm²/s, which quantifies how quickly gas molecules move through the polymer matrix.

### 4. Permeability and Solubility Calculation

Permeability (P) and solubility (S) are calculated based on the steady-state flux and diffusion coefficient:

```python
# Get pressure
pressure = df_ss['P_cell / bar'].mean()   # [bar]

# Calculate permeability
permeability = thickness * slope / pressure   # [cm^3(STP) cm cm^-2 s^-1 bar^-1]

# Calculate solubility coefficient
solubility_coefficient = permeability / diffusion_coefficient   # [cm^3(STP) cm^-3 bar^-1]

# Calculate solubility (concentration)
solubility = solubility_coefficient * pressure
```

These calculations follow the solution-diffusion model, which relates the three key transport parameters:

1. **Permeability Calculation**: P = (steady-state flux × thickness) / pressure difference
   - The slope from the linear fit represents the steady-state flux
   - The pressure is averaged from the steady-state region measurements
   - Units: cm³(STP)·cm/(cm²·s·bar) (often converted to Barrer: 10⁻¹⁰ cm³(STP)·cm/(cm²·s·cmHg))

2. **Solubility Coefficient Calculation**: S = P / D
   - This follows directly from the solution-diffusion model: P = D × S
   - Units: cm³(STP)/(cm³·bar)

3. **Solubility (Concentration) Calculation**: C = S × p
   - Applies Henry's law to calculate the equilibrium concentration
   - Units: cm³(STP)/cm³

These calculations complete the core analysis, providing a comprehensive characterization of the membrane's gas transport properties.