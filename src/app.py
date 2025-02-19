import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from visualisation import *
from time_lag_analysis import *
from util import thickness_dict, qN2_dict


class App(ctk.CTk):
    def __init__(self, data_dir):
        super().__init__()

        self.data_dir = data_dir
        self.calculation_results = None
        self.L_cm = None
        self.d_cm = None
        self.qN2_mlmin = None
        self.left_time = None
        self.right_time = None
        self.stabilisation_time_range = None

        # Create main window
        self.geometry('1200x800')
        self.title('Time Lag Analysis')

        # Bind the Escape key to close the window
        self.bind('<Escape>', lambda e: e.widget.quit())

        # Configure main grid
        self.grid_columnconfigure(0, weight=1)  # Input column
        self.grid_columnconfigure(1, weight=4)  # Plot column
        self.grid_rowconfigure(0, weight=1)    # Inputs and plots
        self.grid_rowconfigure(1, weight=1)    # Textbox
        self.grid_rowconfigure(2, weight=0)    # Footer

        # Input column
        self.input_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.input_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Dropdown list to select experiment
        file_label = ctk.CTkLabel(self.input_frame, text='Select file:', font=ctk.CTkFont(weight='bold'))
        file_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.file_combobox = ctk.CTkComboBox(self.input_frame, values=self.get_xlxs_files(), width=200, command=self.on_combobox_selected)
        self.file_combobox.set('')  # Empty default value
        self.file_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Diameter input
        self.d_cm_label = ctk.CTkLabel(self.input_frame, text='Diameter / cm:', font=ctk.CTkFont(weight='bold') )
        self.d_cm_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.d_cm_entry = ctk.CTkEntry(self.input_frame, width=75)
        self.d_cm_entry.insert(0, '1.0')  # Set default value
        self.d_cm_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Thickness input
        self.L_cm_label = ctk.CTkLabel(self.input_frame, text='Thickness / cm:', font=ctk.CTkFont(weight='bold'))
        self.L_cm_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        self.L_cm_entry = ctk.CTkEntry(self.input_frame, width=75)
        self.L_cm_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Flow rate input
        self.qN2_mlmin_label = ctk.CTkLabel(self.input_frame, text='Flow rate / ml min^-1:', font=ctk.CTkFont(weight='bold'))
        self.qN2_mlmin_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        self.qN2_mlmin_entry = ctk.CTkEntry(self.input_frame, width=75)
        self.qN2_mlmin_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Label for stabilisation time
        self.stab_time_label = ctk.CTkLabel(self.input_frame, text='Stabilisation time / s:', font=ctk.CTkFont(weight='bold'))
        self.stab_time_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        
        # Checkbox to use Auto or Custom stability time range
        # Create frame for auto detect checkbox and help label
        self.auto_detect_frame = ctk.CTkFrame(self.input_frame, fg_color='transparent')
        self.auto_detect_frame.grid(row=4, column=1, columnspan=4, padx=5, pady=5, sticky='w')

        self.checkbox_var = ctk.IntVar(value=1)  # Set the default value to 1 (checked)
        self.use_custom_stab_time_checkbox = ctk.CTkCheckBox(self.auto_detect_frame, text='Auto detect', variable=self.checkbox_var, command=self.toggle_custom_stab_time_entries)
        self.use_custom_stab_time_checkbox.pack(side='left', padx=(0,5))
        
        # Question mark symbol with tooltip
        self.help_label = ctk.CTkLabel(self.auto_detect_frame, text='?', width=20)
        self.help_label.pack(side='left')

        # Create tooltip window but don't show it yet
        self.tooltip = ctk.CTkToplevel()
        self.tooltip.withdraw() # Hide initially
        self.tooltip.overrideredirect(True) # Hide window decorations to look like pop-up
        self.tooltip_label = ctk.CTkLabel(self.tooltip, text='Auto detection finds stabilisation time when signal variations fall below threshold.', wraplength=200)
        self.tooltip_label.pack(padx=5, pady=5)

        # Bind hover events
        self.help_label.bind('<Enter>', self.show_tooltip)
        self.help_label.bind('<Leave>', lambda event: self.tooltip.withdraw())

        # Custom time input
        self.custom_stab_time_frame = ctk.CTkFrame(self.input_frame, fg_color='transparent')
        self.custom_stab_time_frame.grid(row=5, column=1, columnspan=4, padx=5, pady=5, sticky='w')

        self.custom_stab_time_label = ctk.CTkLabel(self.custom_stab_time_frame, text='Custom range:')
        self.custom_stab_time_label.pack(side='left', padx=5)

        self.stab_time_start_entry = ctk.CTkEntry(self.custom_stab_time_frame, placeholder_text='Start time / s', width=100)
        self.stab_time_start_entry.pack(side='left', padx=5)

        self.custom_stab_time_text = ctk.CTkLabel(self.custom_stab_time_frame, text=' → ')
        self.custom_stab_time_text.pack(side='left', padx=5)

        self.stab_time_end_entry = ctk.CTkEntry(self.custom_stab_time_frame, placeholder_text='End time / s', width=100)
        self.stab_time_end_entry.pack(side='left', padx=5)

        # Call the function to apply the initial checkbox state
        self.toggle_custom_stab_time_entries()
        
        # Run analysis button
        self.run_button = ctk.CTkButton(self.input_frame, text='Run Analysis', command=self.run_analysis)
        self.run_button.grid(row=6, column=0, columnspan=6, padx=10, pady=10, sticky='n')

        # Text result display
        self.result_text = ctk.CTkTextbox(self.input_frame)
        self.result_text.grid(row=7, column=0, columnspan=6, sticky='nsew', padx=10, pady=10)
        self.input_frame.grid_rowconfigure(7, weight=1)  # Adjust row input_frame grid to make textbox expandable
        self.input_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)  # Make all columns expandable

        # UI scaling dropdown
        scaling_label = ctk.CTkLabel(self.input_frame, text='UI Scaling:')
        scaling_label.grid(row=8, column=0, padx=5, pady=5, sticky='w')

        self.scaling_combobox = ctk.CTkComboBox(self.input_frame, values=['80%', '90%', '100%', '110%', '120%', ], width=100, command=self.change_scaling)
        self.scaling_combobox.set('100%')  # Default value
        self.scaling_combobox.grid(row=8, column=1, padx=5, pady=5, sticky='w')

        # Plot label size scaling dropdown
        label_scaling_label = ctk.CTkLabel(self.input_frame, text='Plot Label Size:')
        label_scaling_label.grid(row=9, column=0, padx=5, pady=5, sticky='w')

        self.label_scaling_combobox = ctk.CTkComboBox(self.input_frame, values=['80%', '90%', '100%', '110%', '120%', '130%', '140%'], width=100, command=self.change_label_scaling)
        self.label_scaling_combobox.set('100%')  # Default value
        self.label_scaling_factor = int(self.label_scaling_combobox.get().replace('%', '')) / 100
        self.label_scaling_combobox.grid(row=9, column=1, padx=5, pady=5, sticky='w')

        # Plot column
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=10, pady=10)

        # Configure plot grid
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(1, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(1, weight=1)

        # Footer frame
        self.footer_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.footer_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

        author_label = ctk.CTkLabel(self.footer_frame, text='Author: Louis Nguyen')
        author_label.pack(side='left', padx=5)

        version_label = ctk.CTkLabel(self.footer_frame, text='Version: 1.0.0')
        version_label.pack(side='right', padx=5)
        
    def get_xlxs_files(self):
        return [f for f in os.listdir(self.data_dir) if f.endswith('.xlsx')]
    
    def autofill_thickness_flowrate(self, event):
        exp = str(self.file_combobox.get()).split('.')[0]
        if exp in thickness_dict:
            self.L_cm_entry.delete(0, ctk.END)
            self.L_cm_entry.insert(0, thickness_dict[exp])
            self.qN2_mlmin_entry.delete(0, ctk.END)
            self.qN2_mlmin_entry.insert(0, qN2_dict[exp])
    
    def on_combobox_selected(self, event):
        exp_name = str(self.file_combobox.get()).split('.')[0]
        self.autofill_thickness(exp_name)
        self.autofill_flowrate(exp_name)
    
    def autofill_thickness(self, file_name):
        if file_name in thickness_dict:
            self.L_cm_entry.delete(0, ctk.END)
            self.L_cm_entry.insert(0, str(thickness_dict[file_name]))

    def autofill_flowrate(self, file_name):
        if file_name in qN2_dict:
            self.qN2_mlmin_entry.delete(0, ctk.END)
            self.qN2_mlmin_entry.insert(0, str(qN2_dict[file_name]))

    # Method to show tooltip at fixed position
    def show_tooltip(self, event):
        x = self.help_label.winfo_rootx() + 20
        y = self.help_label.winfo_rooty() + 20
        self.tooltip.geometry(f'+{x}+{y}')
        self.tooltip.configure(fg_color='gray')  # Configure rounded corners
        self.tooltip.deiconify()
    
    # Function to toggle state based on checkbox
    def toggle_custom_stab_time_entries(self):
        # Retrieve default theme colors
        default_fg_color = ctk.ThemeManager.theme['CTkEntry']['fg_color']
        default_text_color = ctk.ThemeManager.theme['CTkEntry']['text_color']

        if self.checkbox_var.get() == 1: # ticked, Auto enabled
            self.stab_time_start_entry.configure(state='disabled', fg_color='gray', text_color='gray')
            self.stab_time_end_entry.configure(state='disabled', fg_color='grey', text_color='grey')
            self.custom_stab_time_label.configure(state='disabled', text_color='grey')
            self.custom_stab_time_text.configure(state='disabled', text_color='grey')
        elif self.checkbox_var.get() == 0:  # unticked, Auto disabled
            self.stab_time_start_entry.configure(state='normal', fg_color=default_fg_color, text_color=default_text_color)
            self.stab_time_end_entry.configure(state='normal', fg_color=default_fg_color, text_color=default_text_color)
            self.custom_stab_time_label.configure(state='normal', text_color=default_text_color)
            self.custom_stab_time_text.configure(state='normal', text_color=default_text_color)

    def change_scaling(self, event):
        scaling_percentage = self.scaling_combobox.get().replace('%', '')
        scaling_factor = int(scaling_percentage) / 100
        ctk.set_widget_scaling(scaling_factor)

    def change_label_scaling(self, event):
        label_scaling_percentage = self.label_scaling_combobox.get().replace('%', '')
        self.label_scaling_factor = int(label_scaling_percentage) / 100
        self.update_plots()  # Only update plots, no need to recalculate

    def perform_calculations(self):
        """Perform all calculations and store results"""
        file_path = os.path.join(self.data_dir, self.file_combobox.get())
        
        # Store all parameters as class variables
        # Check if file is selected
        if not self.file_combobox.get():
            self.result_text.delete(1.0, ctk.END)
            self.result_text.insert(ctk.END, "Please select a file first")
            return

        # Get and validate required inputs
        try:
            self.d_cm = float(self.d_cm_entry.get())
            self.L_cm = float(self.L_cm_entry.get())
            self.qN2_mlmin = float(self.qN2_mlmin_entry.get())
        except ValueError:
            self.result_text.delete(1.0, ctk.END)
            self.result_text.insert(ctk.END, "Please enter valid numbers for diameter, thickness and flow rate")
            return

        # Get optional time range inputs if auto detect is disabled
        if self.checkbox_var.get() == 0:
            try:
                self.left_time = float(self.stab_time_start_entry.get()) if self.stab_time_start_entry.get() else None
                self.right_time = float(self.stab_time_end_entry.get()) if self.stab_time_end_entry.get() else None
            except ValueError:
                self.result_text.delete(1.0, ctk.END)
                self.result_text.insert(ctk.END, "Please enter valid numbers for time range")
                return
            self.stabilisation_time_range = (self.left_time, self.right_time)
        else:
            self.stabilisation_time_range = (None, None)

        self.calculation_results = time_lag_analysis_workflow(
            file_path, self.L_cm, self.d_cm, self.qN2_mlmin, self.stabilisation_time_range, 
            display_plot=False, save_plot=False, save_data=False
        )
        
        # Update results text
        self.result_text.delete(1.0, ctk.END)
        result_dict = self.calculation_results[0]
        formatted_result = (
            f'Experiment = {result_dict['experiment']}\n'
            f'Temperature = {result_dict['temperature']:.2f} °C\n'
            f'Pressure = {result_dict['pressure']:.2f} bar\n'
            f'Time lag = {result_dict['time_lag']:.2f} s\n'
            f'Slope = {result_dict['slope']:.2e} cm^3(STP) cm^-2 s^-1\n'
            f'Intercept = {result_dict['intercept']:.2e} cm^3(STP) cm^-2\n'
            f'Diffusion coefficient = {result_dict['diffusion_coefficient']:.2e} cm^2 s^-1\n'
            f'Permeability = {result_dict['permeability']:.2e} cm^3(STP) cm^-1 s^-1 bar^-1\n'
            f'Solubility coefficient = {result_dict['solubility_coefficient']:.2e} cm^3(STP) cm^-3 bar^-1\n'
        )
        self.result_text.insert(ctk.END, formatted_result)

    def update_plots(self):
        """Update all plots using stored calculation results"""
        if not self.calculation_results or self.L_cm is None:
            return
            
        result_dict, preprocessed_df, C_profile, flux, df_C, df_flux = self.calculation_results

        # Clear previous plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        # Helper function to create a plot with a 'Save' button
        def create_plot_with_save_button(fig, row, column):
            frame = ctk.CTkFrame(self.plot_frame, fg_color='white')
            frame.grid(row=row, column=column, sticky='nsew', padx=0, pady=0)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

            # Create 'Save' button
            def save_plot():
                file_path = ctk.filedialog.asksaveasfilename(
                    defaultextension='.png',
                    filetypes=[
                        ('PNG files', '*.png'),
                        ('SVG files', '*.svg'), 
                        ('All files', '*.*')
                    ]
                )
                if file_path:
                    fig.savefig(file_path, dpi=1200)

            # Create transparent save button with hover effect
            save_button = ctk.CTkButton(
                frame, 
                text='Save', 
                command=save_plot, 
                width=20, 
                height=10,
                fg_color='gray80',
                hover_color=('gray80', 'gray80'),  # Color when hovering
                text_color=('black', 'black'),  # Normal text color
                border_color='gray100',  # Border color
                border_width=1,  # Border width
                font=('', 8, 'normal')  # Normal font
                )
            
            # Bind hover events to change font weight
            save_button.bind('<Enter>', lambda e: save_button.configure(font=('', 8, 'bold')))
            save_button.bind('<Leave>', lambda e: save_button.configure(font=('', 8, 'normal')))
            
            save_button.place(relx=0.995, rely=0.005, anchor='ne')

        # Plot 1
        fig1 = plt.figure(figsize=(5, 4))
        ax1 = fig1.add_subplot(111)
        plot_time_lag_analysis(preprocessed_df, result_dict['stabilisation_time'], result_dict['slope'], result_dict['intercept'], fig=fig1, ax=ax1)
        self.update_plot_labels(fig1, ax1)
        fig1.tight_layout(w_pad=2.0, h_pad=2.0)
        create_plot_with_save_button(fig1, row=0, column=0)
        plt.close(fig1)

        # Plot 2
        fig2 = plt.figure(figsize=(5, 4))
        ax2 = fig2.add_subplot(111)
        plot_flux_over_time(flux, preprocessed_df, preprocessed_df['t / s'].iloc[-1], fig=fig2, ax=ax2)
        self.update_plot_labels(fig2, ax2)
        fig2.tight_layout(w_pad=2.0, h_pad=2.0)
        create_plot_with_save_button(fig2, row=0, column=1)
        plt.close(fig2)

        # Plot 3
        fig3 = plt.figure(figsize=(5, 4))
        ax3 = fig3.add_subplot(111)
        plot_concentration_location_profile(C_profile, self.L_cm, result_dict['stabilisation_time'], fig=fig3, ax=ax3)
        self.update_plot_labels(fig3, ax3)
        fig3.tight_layout(w_pad=2.0, h_pad=2.0)
        create_plot_with_save_button(fig3, row=1, column=0)
        plt.close(fig3)

        # Plot 4
        fig4 = plt.figure(figsize=(5, 4))
        ax4 = fig4.add_subplot(111)
        plot_concentration_profile(C_profile, self.L_cm, result_dict['stabilisation_time'], fig=fig4, ax=ax4)
        self.update_plot_labels(fig4, ax4)
        fig4.tight_layout(w_pad=2.0, h_pad=2.0)
        create_plot_with_save_button(fig4, row=1, column=1)
        plt.close(fig4)

    def run_analysis(self):
        """Main analysis function that calls calculation and plotting"""
        self.perform_calculations()
        self.update_plots()

    def update_plot_labels(self, fig, ax):
        label_size = 10 * self.label_scaling_factor
        ax.title.set_size(label_size)
        ax.xaxis.label.set_size(label_size)
        ax.yaxis.label.set_size(label_size)
        ax.tick_params(axis='both', which='major', labelsize=label_size)
        if ax.get_legend() is not None:
            ax.legend(fontsize=label_size)

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(base_dir, '../data')
    app = App(dir)
    app.mainloop()
