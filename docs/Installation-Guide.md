# Installation Guide

## Prerequisites

- Anaconda or Miniconda
- Git (optional)

## Installation Steps

1. Clone or download the repository:
```bash
git clone [repository URL]
cd [project directory]
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate time-lag-analysis
```

3. Run the application:
```bash
python src/app.py
```

## Troubleshooting

If you encounter any issues:
1. Ensure Anaconda/Miniconda is properly installed
2. Try updating conda: `conda update -n base conda`
3. Make sure all dependencies are installed: `conda env update -f environment.yml`
