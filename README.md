# Time Lag Analysis Application

## Description

This application provides a user-friendly interface for analyzing gas permeation data using the time lag method. Load data from Excel files, specify your experimental setup, run the analysis, and visualize the results.

## Learning Outcomes

By using this application, you will:

-   Gain an understanding of time lag analysis in gas permeation experiments.
-   Learn how to prepare and analyze your experimental data.
-   Get hands-on experience with a GUI for scientific data analysis.
-   Be able to adapt the application to your specific research interests.

| Task                                                                 | Time     |
| -------------------------------------------------------------------- | -------- |
| [Introduction](docs/01-Home.md)                                       | 20 mins  |
| [Understanding Theoretical Background](docs/02-Theoretical-Background.md)                     | 30 mins  |
| [Data Management and Processing](docs/03-Data-Management-and-Processing.md)             | 25 mins  |
| [Time Lag Analysis Implementation](docs/04-TimelagAnalysis-Implementation.md)             | 25 mins  |
| [Python PDE Implementation](docs/05-Python-PDE-Implementation.md)                  | 25 mins  |
| [Visualisation Techniques](docs/06-Visualisation.md)                              | 20 mins  |
| [GUI Implementation](docs/07-GUI-Implementation.md)                       | 15 mins  |
| [Application Workflow](docs/08-Application-Workflow.md)                       | 20 mins  |
| **Subtotal: Core Documentation**                                     | **3 hours** |
| [Exercises and Best Practices](docs/09-Exercises-and-Best-Practices.md)               | 3 hours  |
| **Total Estimated Time**                                             | **6 hours** |

## Requirements

### Academic

-   Anaconda or Miniconda installed on your system
-   Git (optional, for cloning the repository)

### System
Start by reading the theory in the reading materials in `docs` folder, in hierachial order.
Then attempt to complete exercises ....
...

## Getting Started

1.  Clone or download the repository:

    ```bash
    git clone [repository URL]
    cd [project directory]
    ```
2.  Create and activate the conda environment:

    ```bash
    conda env create -f environment.yml
    conda activate time-lag-analysis
    ```
3.  Run the application:

    ```bash
    python src/app.py
    ```

## Project Structure

```
├── data/                      # Example data files
├── src/                       # Source code
│   ├── __init__.py            # Initializes the package
│   ├── app.py                 # Main application file (GUI)
│   ├── calculations.py        # Functions for time lag calculations
│   ├── data_processing.py     # Functions for loading and preprocessing data
│   ├── time_lag_analysis.py   # Workflow for performing time lag analysis
│   ├── util.py                # Utility functions and plot styling
│   └── visualisation.py       # Functions for creating plots
├── tests/                     # Test scripts
├── environment.yml            # Conda environment file
├── README.md                  # This file
```

## License

This project is licensed under the [BSD-3-Clause license](LICENSE.md)
