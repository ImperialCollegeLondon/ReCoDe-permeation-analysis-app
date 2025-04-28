# Scientific Visualisation Implementation

This document explains how the scientific visualisations are implemented in the application. The `visualisation.py` module provides specialized plotting functions to help researchers interpret time lag analysis results effectively.

## Overview

Scientific visualisation is a crucial component of the time lag analysis workflow, helping researchers:

- Visualise the time lag determination process
- Examine concentration profiles within the membrane
- Compare experimental and theoretical flux profiles
- Validate results through visual inspection
- Create publication-quality figures

The visualisations in this application are implemented using Matplotlib, a powerful Python plotting library that provides fine control over figure aesthetics and layout.

## Core Visualisation Functions

### 1. Time Lag Analysis Plot

```python
def plot_time_lag_analysis(df: pd.DataFrame, stabilisation_time_s: float, slope: float, intercept: float, fig=None, ax=None):
    """
    Plot the results of the time-lag analysis.
    
    Parameters:
    df (pd.DataFrame): Processed data with time and cumulative flux columns
    stabilisation_time_s (float): Time after which the flux has stabilized
    slope (float): Slope of the steady-state line
    intercept (float): Intercept of the steady-state line
    fig, ax: Optional figure and axes objects
    
    Returns:
    tuple: Figure and axes objects
    """
    # Create figure and axes if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot experimental data
    ax.plot(df['t / s'], df['cumulative flux / cm^3(STP) cm^-2'], 
            color='black', linestyle='-', linewidth=1.5, marker='o', 
            markersize=3, label='Experimental data')
    
    # Highlight steady-state region
    df_ss = df[df['t / s'] > stabilisation_time_s]
    ax.plot(df_ss['t / s'], slope*df_ss['t / s'] + intercept, 
            color='red', linestyle='--', linewidth=2, label='Steady-state fit')
    
    # Show extrapolation to time axis
    df_early = df.loc[df['t / s'] <= stabilisation_time_s]
    ax.plot(df_early['t / s'], slope*df_early['t / s'] + intercept, 
            color='red', linestyle=':', linewidth=1.5, label='Extrapolation')
    
    # Mark time lag point
    time_lag = -intercept / slope
    ax.axvline(x=time_lag, color='blue', linestyle='--', linewidth=1.5, 
               label=f'Time lag: {time_lag:.1f} s')
    
    # Mark stabilization time
    ax.axvline(x=stabilisation_time_s, color='green', linestyle=':', linewidth=1.5,
               label=f'Stabilization: {stabilisation_time_s:.1f} s')
    
    # Add annotations
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Cumulative Flux (cm$^3$(STP) cm$^{-2}$)', fontsize=12)
    ax.set_title('Time Lag Analysis', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Apply formatting
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    return fig, ax
```

This function creates the central visualisation of the time lag analysis method:

- **Experimental Data**: The raw cumulative flux data is plotted as a function of time
- **Steady-State Fit**: A linear fit to the steady-state portion of the curve
- **Extrapolation**: An extension of the steady-state line to earlier times
- **Time Lag Marker**: A vertical line marking the time lag (x-intercept of steady-state line)
- **Stabilization Time**: A vertical line showing when steady-state is reached

The resulting plot provides a clear visual representation of how the time lag is determined from experimental data, which is crucial for validating the analysis.

### 2. Concentration Profile Visualisation

```python
def plot_concentration_profile(C_profile, L, t_points=None, fig=None, ax=None):
    """
    Plot the concentration profile within the membrane at different times.
    
    Parameters:
    C_profile (np.ndarray): Concentration profile from PDE solver (dimensions: time, position)
    L (float): Membrane thickness in cm
    t_points (list): List of time indices to plot, or None for automatic selection
    fig, ax: Optional figure and axes objects
    
    Returns:
    tuple: Figure and axes objects
    """
    Nt, Nx = C_profile.shape
    
    # Create figure and axes if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    # Select time points to display
    if t_points is None:
        # Select initial, few early points, middle and final
        t_points = [0, int(Nt*0.05), int(Nt*0.1), int(Nt*0.25), int(Nt*0.5), Nt-1]
    
    # Create position array
    x = np.linspace(0, L, Nx)
    
    # Color map for time evolution
    colors = plt.cm.viridis(np.linspace(0, 1, len(t_points)))
    
    # Plot concentration profiles
    for i, t_idx in enumerate(t_points):
        if t_idx < Nt:
            label = f"t = {int(t_idx/(Nt-1)*100)}% of total time"
            ax.plot(x, C_profile[t_idx, :], color=colors[i], linewidth=2, label=label)
    
    # Add annotations
    ax.set_xlabel('Position in Membrane (cm)', fontsize=12)
    ax.set_ylabel('Concentration (normalized)', fontsize=12)
    ax.set_title('Gas Concentration Profile Evolution', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Apply formatting
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    return fig, ax
```

This function visualises the spatial distribution of gas concentration within the membrane at different times:

- **Multiple Time Points**: Shows several snapshots of the concentration profile during the diffusion process
- **Color Gradient**: Uses a color gradient to indicate time progression
- **Boundary Conditions**: Clearly shows the fixed boundary conditions (C = C₀ at x = 0, C = 0 at x = L)
- **Spatial Dimension**: Displays concentration as a function of position within the membrane

This visualisation helps researchers understand the gas diffusion process within the membrane and validate that the PDE solver is correctly implementing the physical model.

### 3. Flux Comparison Visualisation

```python
def plot_flux_comparison(df_exp, flux_theo, t_theo=None, fig=None, ax=None):
    """
    Plot comparison between experimental and theoretical flux.
    
    Parameters:
    df_exp (pd.DataFrame): DataFrame containing experimental data
    flux_theo (np.ndarray): Theoretical flux values
    t_theo (np.ndarray): Time points for theoretical flux, or None if same as experimental
    fig, ax: Optional figure and axes objects
    
    Returns:
    tuple: Figure and axes objects
    """
    # Create figure and axes if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot experimental flux
    ax.plot(df_exp['t / s'], df_exp['flux / cm^3(STP) cm^-2 s^-1'], 
            'o', color='black', markersize=3, alpha=0.5, label='Experimental')
    
    # Plot theoretical flux
    if t_theo is None:
        t_theo = df_exp['t / s']
    
    ax.plot(t_theo, flux_theo, 
            '-', color='red', linewidth=2, label='Theoretical (PDE)')
    
    # Add annotations
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Flux (cm$^3$(STP) cm$^{-2}$ s$^{-1}$)', fontsize=12)
    ax.set_title('Flux Comparison: Experimental vs. Theoretical', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Apply formatting
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    return fig, ax
```

This function compares the experimental flux data with theoretical predictions from the PDE solver:

- **Experimental Data**: Plotted as points to show the raw measurements
- **Theoretical Curve**: Displayed as a continuous line to represent the model prediction
- **Visual Validation**: Allows researchers to assess how well the model fits the experimental data
- **Transient Behavior**: Highlights the approach to steady-state flux

This visualisation is crucial for validating the calculated diffusion coefficient by showing how well the theoretical model reproduces the experimental measurements.


## Consistent Styling with `set_plot_style()`

The `set_plot_style()` function plays a crucial role in maintaining visual consistency across all plots generated by the application. It is typically called at the begining of each plot functions to set consistent plot styling.

```python
def set_plot_style():
    """Set the default plot style for consistent visualization."""
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Define consistent plot aesthetics
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 16
    
    # Define color schemes
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[
        '#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', 
        '#CA9161', '#FBAFE4', '#949494', '#ECE133', '#56B4E9'
    ])
```

### Key Functions of `set_plot_style()`

1. **Base Style Setting**: Establishes a clean, professional base style using `seaborn-v0_8-whitegrid`, which provides a good foundation for scientific visualisation

2. **Font Configuration**: 
   - Sets sans-serif fonts for better readability on screens and in printed publications
   - Establishes a font fallback hierarchy to ensure consistent appearance across platforms

3. **Size Hierarchy**:
   - Creates a clear visual hierarchy with different sizes for titles, axes labels, and tick labels
   - Optimizes font sizes for readability while maintaining professional appearance

4. **Color Scheme**:
   - Implements a colorblind-friendly, visually distinct palette
   - Uses colors that reproduce well in print and remain distinguishable in grayscale

### Benefits of Centralized Style Management

By centralizing styling decisions in a single function, the implementation achieves several important goals:

1. **Consistency**: All plots share the same visual language, creating a cohesive look and feel
2. **Maintainability**: Style changes can be made in one location rather than throughout the codebase
3. **Professionalism**: Ensures all visualisations meet publication standards
4. **Accessibility**: The chosen color scheme and font sizes improve readability for users with visual impairments

### Customizing Predefined Styles

The application also provides a dictionary of standard figure sizes for different plot types, complementing the `set_plot_style()` function:

```python
figsize_dict = {
    'default': (8, 6),    # Standard figure size
    'wide': (12, 6),      # Wide format for time series
    'square': (8, 8),     # Square format for correlation plots
    'tall': (6, 8),       # Tall format for vertical data
    'arrhenius': (12, 5), # Special format for Arrhenius plots
    'comparison': (10, 8) # Format for multi-panel comparison plots
}
```

This dictionary works in conjunction with `set_plot_style()` to provide both consistent styling and appropriate dimensions:

```python
# Apply style and use a predefined figure size
set_plot_style()
fig, ax = plt.subplots(figsize=figsize_dict['wide'])
```

By combining these elements, the application ensures that all visualisations maintain a professional, consistent appearance regardless of which function generates them or which part of the application displays them.

## Visualisation Customization and Style

The module includes functions for setting consistent visualisation styles:

```python
def set_plot_style():
    """Set the default plot style for consistent visualization."""
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Define consistent plot aesthetics
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 16
    
    # Define color schemes
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[
        '#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', 
        '#CA9161', '#FBAFE4', '#949494', '#ECE133', '#56B4E9'
    ])
```

These style settings ensure that all visualisations have a consistent and professional appearance, which is important for:
- Creating publication-quality figures
- Maintaining visual consistency across different analyses
- Optimizing readability and clarity of scientific data presentation

## Usage Example

```python
# Set consistent style for all plots
set_plot_style()

# Create and customize a time lag analysis plot
fig, ax = plt.subplots(figsize=figsize_dict['default'])
plot_time_lag_analysis(data_df, 500, 0.00025, -0.12, fig, ax)

# Add custom elements if needed
ax.set_xlim(0, 2000)
ax.set_ylim(-0.05, 0.4)
ax.annotate('Steady-state region', xy=(1200, 0.2), xytext=(1000, 0.3),
            arrowprops=dict(arrowstyle='->'))

# Save the figure
plt.savefig('custom_timelag_plot.png', dpi=300, bbox_inches='tight')
```

This example demonstrates how to:
1. Apply consistent styling
2. Create a basic visualisation
3. Customize it with additional elements
4. Save the result to a file

## Advantages of this Implementation

The visualisation implementation in this application offers several advantages:

1. **Separation of Concerns**: Visualisation logic is separated from analysis code
2. **Consistent Styling**: All plots have a consistent, professional appearance
3. **Customizability**: Functions accept optional figure and axes objects for further customization
4. **Scientific Focus**: Visualisations are optimized for scientific interpretation
5. **Integration**: Seamlessly integrates with the analysis workflow