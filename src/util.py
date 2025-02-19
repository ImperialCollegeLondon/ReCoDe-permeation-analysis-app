"""
util.py
-------
Module for defining plot styling information.
"""

import matplotlib.pyplot as plt
from datetime import datetime

figsize_dict = {'default': (5, 4), 'side-by-side': (10, 4),}

thickness_dict = {
    'RUN_H_25C-50bar': 0.1, 'RUN_H_25C-100bar_7': 0.1, 'RUN_H_25C-100bar_8': 0.1, 'RUN_H_25C-100bar_9': 0.1, 'RUN_H_25C-200bar_2': 0.1,
    'RUN_H_50C-50bar': 0.1, 'RUN_H_50C-100bar_2': 0.1, 'RUN_H_50C-200bar': 0.1, 
    'RUN_H_75C-50bar': 0.1, 'RUN_H_75C-100bar': 0.1,
    'S3R1': 0.1, 'S3R2': 0.1, 'S3R3': 0.1, 'S3R4': 0.1,
    'S4R3': 0.025, 'S4R4': 0.025, 'S4R5': 0.025, 'S4R6': 0.025,
} # [cm]

qN2_dict = {
    'RUN_H_25C-50bar': 8.0, 'RUN_H_25C-100bar_7': 8.0, 'RUN_H_25C-100bar_8': 8.0, 'RUN_H_25C-100bar_9': 8.0, 'RUN_H_25C-200bar_2': 8.0,
    'RUN_H_50C-50bar': 8.0, 'RUN_H_50C-100bar_2': 8.0, 'RUN_H_50C-200bar': 8.0, 
    'RUN_H_75C-50bar': 8.0, 'RUN_H_75C-100bar': 8.0,
    'S3R1': 4.17, 'S3R2': 4.046, 'S3R3': 4.027, 'S3R4': 4.0454, 
    'S4R3': 9.83, 'S4R4': 9.84, 'S4R5': 9.92, 'S4R6': 10,
}  # [ml min^-1]

def set_plot_style():
    """
    Set the style for plots.
    """
    # Common properties
    plt.rcParams['font.size'] = 10
    plt.rcParams['font.family'] = 'sans-serif'
    # plt.rcParams['mathtext.fontset'] = 'cm'  # Computer Modern font
    plt.rcParams["mathtext.default"] = "regular"  # same as regular text
    # plt.rcParams['font.serif'] = ['Times']
    # plt.rcParams['text.usetex'] = True  # Disable LaTeX rendering
    plt.rcParams["axes.titlesize"] = "small"  # relative to font.size
    plt.rcParams["axes.labelsize"] = "small"  # relative to font.size
    plt.rcParams["xtick.labelsize"] = "small"  # relative to font.size
    plt.rcParams["ytick.labelsize"] = "small"  # relative to font.size
    plt.rcParams["legend.fontsize"] = "small"  # relative to font.size
    plt.rcParams['axes.grid'] = False
    plt.rcParams['grid.alpha'] = 0.7
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.color'] = 'gray'
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'    
    plt.rcParams['xtick.major.pad'] = 5
    plt.rcParams['ytick.major.pad'] = 5
    
def update_ticks(ax, x_lo=None, y_lo=None, x_up=None, y_up=None):
    """Update x and y ticks of subplot ax to cover all data. Put ticks to inside.

    Args:
        ax: plot object.
    """
    # Adjust lower x and y ticks to start from 0
    if x_lo != None:
        ax.set_xlim(left=x_lo)
    if y_lo != None:
        ax.set_ylim(bottom=y_lo)
    if x_up != None:
        ax.set_xlim(right=x_up)
    if y_up != None:
        ax.set_ylim(top=y_up)
    
    # Get axis limits
    max_x_lim = ax.get_xlim()[1]
    min_x_lim = ax.get_xlim()[0]
    max_y_lim = ax.get_ylim()[1]
    min_y_lim = ax.get_ylim()[0]
    
    # Get the largest and smallest x ticks and y ticks
    # max_x_tick = max(ax.get_xticks())
    # min_x_tick = min(ax.get_xticks())
    # max_y_tick = max(ax.get_yticks())
    # min_y_tick = min(ax.get_yticks())
    max_x_tick = ax.get_xticks()[-2]    # last tick is not visible
    min_x_tick = ax.get_xticks()[-2]
    max_y_tick = ax.get_yticks()[-2]
    min_y_tick = ax.get_yticks()[-2]
    
    # Get the length of major ticks on the x-axis
    ax_x_major_tick_length = ax.get_xticks()[1] - ax.get_xticks()[0]
    ax_y_major_tick_length = ax.get_yticks()[1] - ax.get_yticks()[0]
    
    # Adjust upper x and y ticks to cover all data
    if x_up == None: 
        if max_x_lim > max_x_tick:
            ax.set_xlim(right=max_x_tick + 1.*ax_x_major_tick_length)
    if y_up == None:
        if max_y_lim > max_y_tick:
            ax.set_ylim(top=max_y_tick + 1.*ax_y_major_tick_length)
    if x_lo == None:
        if min_x_lim < min_x_tick:
            ax.set_xlim(left=min_x_tick - 1.*ax_x_major_tick_length)
    if y_lo == None:
        if min_y_lim < min_y_tick:
            ax.set_ylim(bottom=min_y_tick - 1.*ax_y_major_tick_length)
    
    # Use scientific notation for both axis
    ax.ticklabel_format(style='sci', axis='both', scilimits=(-3, 3))
    
    # Display ticks on both sides
    ax.tick_params(axis='both', direction='in', which='both')
    
    return ax.get_xlim(), ax.get_ylim()

def get_time_id():
    """
    Generate a unique time-based identifier.
    
    Returns:
        str: A string representing the current date and time in the format YYYYMMDD_HHMMSS.
    """
    return datetime.now().strftime('%y%m%d-%H%M%S')