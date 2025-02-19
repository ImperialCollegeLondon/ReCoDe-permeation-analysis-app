# User Guide

## Data File Requirements

### Excel File Format
- File type: `.xlsx`
- Required columns:
  - Time (s)
  - Pressure (bar) or Flow (ml/min)
- Example structure:
  ```
  | Time / s | Pressure / bar |
  |----------|---------------|
  | 0        | 1.013        |
  | 1        | 1.014        |
  ```

## Using the Application

1. Loading Data
   - Click 'Select file' dropdown
   - Choose your `.xlsx` file from the data directory

2. Setting Parameters
   - Enter membrane diameter (cm)
   - Enter membrane thickness (cm)
   - Enter gas flow rate (ml/min)

3. Stabilization Time
   - Auto detect: Let the program find the steady-state region
   - Manual: Input custom time range for steady-state analysis

4. Running Analysis
   - Click 'Run Analysis'
   - View results in the text box
   - Examine the generated plots

5. Saving Results
   - Use 'Save' button on each plot to export as PNG or SVG
   - Results are displayed in the textbox and can be copied

## Tips
- Ensure consistent units in your data files
- Use the UI scaling options if plots or text are too small/large
- Hover over '?' icons for additional information

## Advanced Features

1. Custom Stabilization Time
2. Plot Customization
3. Batch Processing

#TODO [Detailed usage instructions...]
