# Jupyter Setup for LIHTC Financial Analysis

## Quick Start

1. **Install Jupyter and dependencies:**
   ```bash
   python3 setup_jupyter.py
   ```

2. **Start Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```

3. **Open the sample notebook:**
   - Click on `LIHTC_Analysis_Sample.ipynb` in the browser
   - Run cells with `Shift+Enter`

## What This Provides

- **Interactive Parameter Testing**: Sliders for credit pricing, construction costs, interest rates
- **Real-time Visualizations**: Charts that update as you adjust parameters
- **Financial Modeling**: LIHTC-specific calculations and feasibility analysis
- **Export Capabilities**: Save your analysis in multiple formats

## Manual Installation (if script doesn't work)

```bash
# Install Jupyter
python3 -m pip install jupyter

# Install required packages
python3 -m pip install notebook ipywidgets plotly seaborn pandas numpy matplotlib openpyxl

# Enable extensions
jupyter nbextension enable --py widgetsnbextension

# Start Jupyter
jupyter notebook
```

## Directory Structure

```
Jupyter/
├── README.md                    # This file
├── setup_jupyter.py            # Automated setup script
├── setup_jupyter.sh            # Alternative bash setup script
├── LIHTC_Analysis_Sample.ipynb # Sample interactive notebook
├── notebooks/                  # Your notebook files
└── data/                      # Data files for analysis
```

## Next Steps

1. Run the setup script to install Jupyter
2. Start Jupyter Notebook
3. Open the sample notebook to see interactive features
4. Create your own notebooks for specific LIHTC analyses

## Troubleshooting

- **Import errors**: Run `python3 setup_jupyter.py` again to ensure all packages are installed
- **Widgets not showing**: Restart the kernel (Kernel → Restart) and run cells again
- **Port already in use**: Jupyter will automatically try the next available port

## Benefits for LIHTC Analysis

- **Interactive sliders** for testing different financial scenarios
- **Real-time charts** showing feasibility and funding gaps
- **Scenario comparison** side-by-side
- **Professional reports** exportable to HTML/PDF
- **Shareable analyses** with embedded interactivity