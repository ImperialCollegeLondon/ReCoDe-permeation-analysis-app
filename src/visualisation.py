"""
visualisation.py
----------------
Module for visualising permeation data and analysis results.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import figsize_dict, set_plot_style, update_ticks

def plot_time_lag_analysis(df: pd.DataFrame, stabilisation_time_s: float, slope: float, intercept: float, fig=None, ax=None):
    """
    Plot the results of the time-lag analysis.

    Parameters:
    df (pd.DataFrame): Preprocessed data.
    stabilisation_time (float): Time after which the flux has stabilised.
    slope (float): Slope of the fitted line.
    intercept (float): Intercept of the fitted line.
    fig (matplotlib.figure.Figure, optional): Figure object to draw the plot onto, otherwise creates a new figure.
    ax (matplotlib.axes.Axes, optional): Axes object to draw the plot onto, otherwise uses current Axes.
    """
    set_plot_style()
    df_ss = df[df['t / s'] > stabilisation_time_s]
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize_dict['default'])
    ax.plot(df['t / s'], df['cumulative flux / cm^3(STP) cm^-2'], color='black', linestyle='-', label='Data')
    ax.plot(df_ss['t / s'], slope*df_ss['t / s'] + intercept, color='red', linestyle='--', label='Fit (steady-state)')
    ax.plot(df.loc[df['t / s'] <= stabilisation_time_s, 't / s'], slope*df.loc[df['t / s'] <= stabilisation_time_s, 't / s'] + intercept, color='red', linestyle=':', label='Fit (extrapolated)')
    ax.set_xlabel(r'Time / $s$')
    ax.set_ylabel(r'Cumulative Flux / $cm^{3}(STP) \; cm^{-2}$')
    ax.legend()
    (x_lo, x_up), (y_lo, y_up) = update_ticks(ax, x_lo=0, y_lo=0)
    ax.set_xlim(x_lo, x_up)
    ax.set_ylim(y_lo, y_up)
    plt.tight_layout()

def plot_concentration_location_profile(C_profile, L, T, fig=None, ax=None):
    """
    Plot the concentration-location profile at different times.

    Parameters:
    C_profile (ndarray): Concentration profile as a function of position x and time t.
    L (float): Thickness of the polymer.
    T (float): Total time.
    fig (matplotlib.figure.Figure, optional): Figure object to draw the plot onto, otherwise creates a new figure.
    ax (matplotlib.axes.Axes, optional): Axes object to draw the plot onto, otherwise uses current Axes.
    """
    set_plot_style()
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize_dict['default'])
    time_points = np.concatenate(([0], np.logspace(np.log10(T/100), np.log10(T), 5)))
    for t in time_points:
        ax.plot(np.linspace(0, L, C_profile.shape[1]), C_profile[int(t / T * (C_profile.shape[0] - 1)), :], label=f't = {t:.0f} s')
    ax.set_xlabel(r'Position / $cm$')
    ax.set_ylabel(r'Concentration / $cm^{3}(STP) \; cm^{-3}$')
    ax.legend()
    (x_lo, x_up), (y_lo, y_up) = update_ticks(ax, x_lo=0, x_up=L, y_lo=0)
    ax.set_xlim(x_lo, x_up)
    ax.set_ylim(y_lo, y_up)
    plt.tight_layout()

def plot_flux_over_time(flux, preprocessed_df, T_final, fig=None, ax=None):
    """
    Plot the flux over time from the model and the preprocessed data.

    Parameters:
    flux (ndarray): Flux values from the model.
    preprocessed_df (pd.DataFrame): Preprocessed data.
    T_final (float): Total time.
    fig (matplotlib.figure.Figure, optional): Figure object to draw the plot onto, otherwise creates a new figure.
    ax (matplotlib.axes.Axes, optional): Axes object to draw the plot onto, otherwise uses current Axes.
    """
    set_plot_style()
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize_dict['default'])
    ax.plot(np.linspace(0, T_final, len(flux)), flux, label='Model')
    ax.plot(preprocessed_df['t / s'], preprocessed_df['flux / cm^3(STP) cm^-2 s^-1'], linestyle='--', label='Measurement')
    ax.set_xlabel(r'Time / $s$')
    ax.set_ylabel(r'Flux / $cm^{3}(STP) \; cm^{-2} \; s^{-1}$')
    (x_lo, x_up), (y_lo, y_up) = update_ticks(ax, x_lo=0, y_lo=0)
    ax.legend()
    ax.set_xlim(x_lo, x_up)
    ax.set_ylim(y_lo, y_up)
    plt.tight_layout()

def plot_concentration_profile(C_profile, L, T, fig=None, ax=None):
    """
    Plot the concentration profile as a function of position x and time t.

    Parameters:
    C_profile (ndarray): Concentration profile as a function of position x and time t.
    L (float): Thickness of the polymer.
    T (float): Total time.
    fig (matplotlib.figure.Figure, optional): Figure object to draw the plot onto, otherwise creates a new figure.
    ax (matplotlib.axes.Axes, optional): Axes object to draw the plot onto, otherwise uses current Axes.
    """
    set_plot_style()
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize_dict['default'])
    cax = ax.imshow(C_profile, extent=[0, L, 0, T], aspect='auto', origin='lower', cmap='coolwarm')
    cbar = fig.colorbar(cax, ax=ax)
    cbar.set_label(r'Concentration / $cm^{3}(STP) \; cm^{-3}$', size=ax.xaxis.label.get_fontsize())
    ax.set_xlabel(r'Position / $cm$')
    ax.set_ylabel(r'Time / $s$')
    (x_lo, x_up), (y_lo, y_up) = update_ticks(ax, x_lo=0, x_up=L, y_lo=0, y_up=T)
    ax.set_xlim(x_lo, x_up)
    ax.set_ylim(y_lo, y_up)
    plt.tight_layout()