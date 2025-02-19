"""
ReCode
----------
A package for analyzing gas permeation data using time-lag method.
"""

from .time_lag_analysis import time_lag_analysis_workflow
from .data_processing import load_data, preprocess_data
from .calculations import time_lag_analysis, flux_pde_const_D
from .visualisation import (
    plot_time_lag_analysis,
    plot_flux_over_time,
    plot_concentration_location_profile,
    plot_concentration_profile
)
from .util import set_plot_style, update_ticks, get_time_id

__version__ = '1.0.0'

__all__ = [
    'time_lag_analysis_workflow',
    'load_data',
    'preprocess_data',
    'time_lag_analysis',
    'flux_pde_const_D',
    'plot_time_lag_analysis',
    'plot_flux_over_time',
    'plot_concentration_location_profile',
    'plot_concentration_profile',
    'set_plot_style',
    'update_ticks',
    'get_time_id',
]
