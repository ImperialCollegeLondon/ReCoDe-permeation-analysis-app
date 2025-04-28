# Application Workflow

This document explains how the components of the Time Lag Analysis application integrate into a cohesive workflow for analyzing gas permeation through membranes.

## Integrated Workflow Overview

The application combines data processing, time lag analysis, PDE solving, and visualisation via the `time_lag_analysis_workflow` function in `src/time_lag_analysis.py`.

## Component Integration Flow

The following text-based diagram illustrates how the components work together:

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  Data Processing  │────▶│   Time Lag        │────▶│  PDE Numerical    │
│  Module           │     │   Analysis        │     │  Solution         │
└───────────────────┘     └───────────────────┘     └───────────────────┘
        │                         │                         │
        │                         │                         │
        ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Visualisation Layer                          │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Results & Output Files                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow Between Components

1. **Data Processing → Time Lag Analysis**
   - Processed experimental data with flux values, stabilisation time, and normalised measurements

2. **Time Lag Analysis → PDE Solution**
   - Calculated diffusion coefficient, equilibrium concentration, and membrane thickness

3. **All Modules → Visualisation**
   - Experimental data, transport parameters, and theoretical profiles combine for comprehensive visualisations

### Key Functions

- **Data Processing**: `load_data`, `preprocess_data`, `identify_stabilisation_time`
- **Time Lag Analysis**: `time_lag_analysis`
- **PDE Solution**: `flux_pde_const_D`
- **Visualisation**: `plot_time_lag_analysis`, `plot_flux_over_time`, `plot_concentration_profile`

## Workflow Steps

1. **Data Processing**: Import and prepare experimental data
2. **Time Lag Analysis**: Calculate transport parameters from steady-state data
3. **PDE Solution**: Simulate theoretical concentration profile
4. **Visualisation**: Create plots comparing experimental and theoretical results
5. **Results**: Store calculated parameters and processed data

## The Workflow Function

The `time_lag_analysis_workflow` function takes these key parameters:
- `datapath`: Path to experimental data file
- `L_cm`: Membrane thickness
- `d_cm`: Membrane diameter
- `stabilisation_time_range`: Optional steady-state time range
- `display_plot`/`save_plot`/`save_data`: Output options

## Benefits

- **Reproducibility**: Complete analysis with a single function call
- **Consistency**: Standardised processing pipeline
- **Validation**: Automatic comparison of theory with experiment
- **Modularity**: Easy to extend with new components