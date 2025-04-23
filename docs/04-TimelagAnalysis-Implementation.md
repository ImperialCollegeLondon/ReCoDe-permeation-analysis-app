# Time Lag Analysis Core Calculation Implementation

This document details the `time_lag_analysis` function within `calculations.py`, which implements the core calculations for time lag analysis. This function converts experimental permeation data into gas transport parameters.

## Core Calculation Steps

The `time_lag_analysis` function implements four key computational steps:

1. Linear Regression of Steady-State Data
2. Time Lag Calculation
3. Diffusion Coefficient Determination
4. Permeability and Solubility Calculation

These steps form the analytical core of the time lag method (covered in [`02-Theoretical-Background`](02-Theoretical-Background.md)), following data preprocessing and stabilisation time detection (covered in [`03-Data-Management-and-Processing`](03-Data-Management-and-Processing.md)).

## Implementation in the `time_lag_analysis` Function


### 1. Linear Regression of Steady-State Data

First, the steady-state region of flux is filtered. This corresponds to a linear change of cumulative flux against time as seen in the plot in [`02-Theoretical-Background`](02-Theoretical-Background.md).
```python
# Filter to steady-state data
df_ss = df[df['t / s'] > stabilisation_time_s]
```

Next, the core calculation uses NumPy's [`polyfit`](https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html) function to perform linear regression on the filtered  portion of the cumulative flux curve. 
```python
# Fitting straight line to the steady-state data
slope, intercept = np.polyfit(df_ss['t / s'], df_ss['cumulative flux / cm^3(STP) cm^-2'], 1)
```
This fits the data to the linear equation $y = mx + c$, where:
- $y$ is the cumulative flux (`cumulative flux / cm^3(STP) cm^-2`)
- $x$ is the time (`t / s`)
- $m$ is the `slope` variable
- $c$ is the `intercept` variable

The variables returned from `polyfit` has imoprtant physical meaning:

-   `slope`: Represents the steady-state flux through the membrane.
-   `intercept`: Represents the y-intercept of the extrapolated steady-state line. This is important for calculating the time lag.

### 2. Time Lag Calculation

The time lag $(θ)$ is calculated by finding the x-intercept of the steady-state line by setting $y = 0$:

$$ 0 = \text{slope} \times \theta + \text{intercept} $$

Rearranging for $\theta$ gives:

$$ \theta = -\frac{\text{intercept}}{\text{slope}} $$

```python
# Calculate time lag
time_lag = -intercept / slope   # [s]
```

### 3. Diffusion Coefficient Determination

The diffusion coefficient $(D)$ is calculated using the formula introduced in [`02-Theoretical-Background`](02-Theoretical-Background.md):

$$D = \frac{L^2}{6\theta}$$

```python
# Calculate diffusion coefficient
diffusion_coefficient = thickness**2 / (6 * time_lag)   # [cm^2 s^-1]
```

### 4. Permeability and Solubility Calculation

The derived formulae in  [`02-Theoretical-Background`](02-Theoretical-Background.md) is used to calculate permeability $(P)$, solubility coefficient $(S)$ and solubility $(C)$.

Permeability is calculed with:
$$ P = \frac{L \times J_{\infty}}{\Delta p} $$

where $J_{\infty}$ is the steady-state flux and ${\Delta p}$ is the pressure.

```python
# Calculate permeability
permeability = thickness * slope / pressure   # [cm^3(STP) cm cm^-2 s^-1 bar^-1]

```

The solubility coefficient is calculted with:
$$S = \frac{P}{D}$$

```python
# Calculate solubility coefficient
solubility_coefficient = permeability / diffusion_coefficient   # [cm^3(STP) cm^-3 bar^-1]

# Calculate solubility (concentration)
solubility = solubility_coefficient * pressure
```

Finally, the solubility can be calculated from:
$$C = S \times {\Delta p}$$

```python
# Calculate solubility (concentration)
solubility = solubility_coefficient * pressure
```