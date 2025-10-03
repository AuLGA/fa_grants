# Financial Assistance Grants (FA Grants) Analysis

This repository contains code, data, and documentation for analyzing the Australian Financial Assistance Grants (FA Grants) system. The project explores grant allocation methodologies, simulates outcomes under different scenarios, and provides visualizations and reports for policy and research purposes.

### Some bits of wisdom from one so wise
- The files in `meta/` are reusable. 
- `custom-reference-doc.docx` might be of special interest. It is built around the current ALGA Word template. It can be used in any pandoc derived pipeline to generate ALGA themed Word documents from markdown, and Quarto and Jupyter notebook files. 

## Contents
- **Code/**: Python scripts and Jupyter notebooks for data analysis, simulation, and modeling.
- **Data/**: Source datasets, working tables, and output files used in the analysis.
- **docs/**: Rendered HTML reports and documentation generated from notebooks and Quarto files as configured in `_quarto_full.yml`.
- **docx_render/**: A smaller report rendered only as a Word file, as configured in `_quarto_docx.yml`.
- **fagrants_module/**: Custom Python modules for FA Grants calculations and data processing.
- **meta/**: Supporting scripts and style files for document formatting and reference management.

## Key Features
- Simulation of grant allocations under various minimum grant scenarios (e.g., 10%, 20%, no minimum).
- Aggregated and state-level analysis of grant distributions.
- Interactive maps and visualizations of results.
- Automated report generation using Quarto and Jupyter.

## Getting Started
1. **Clone the repository:**
   ```bash
   git clone https://github.com/spulick/fa_grants.git
   ```
2. **Install dependencies:**
   - On Windows, Windows Subsystem for Linux (WSL) is **strongly recommended**
   - Python 3.8+
   - [Lua](https://www.lua.org) 
   - [Quarto](https://quarto.org/)
   - [conda/mamba/miniforge](https://github.com/conda-forge/miniforge)
   - Install required packages:
     ```bash
     conda create --name <env name> --file requirements.txt
     ```
3. **Run analyses:**
   - Execute notebooks in the root or `Code/` directory for simulations and data exploration.
   - To create new scenarios, **duplicate** `Data/FA Grants Tables - Python.xlsx` and tweak numbers in there. Make sure to pass the right input file while creating the model instance (the function call that goes `inst = fagrants.fagrants_mode(...)`)
   > If you do tweak numbers in the Excel input file, make sure to not change the structure of the file or change row/column positions since the modelling scripts have hardcoded pointers to fetch values from the file.
   > If you're sure of what you're doing, feel free to play with the structure and alter the pointers in the scripts on a **fork or a branch**. 

4. **Render**
    - The lazy approach to rendering the whole project would be to tweak the `render.lua` script and run it using `lua render.lua` from the project root. This generates both the full report (html and docx) and the smaller report (docx only).
    - Else, `quarto render` should do the trick as long as `_quarto.yml` has the right config in it (have a look at the lua script). It contains `_quarto_full.yml` by default. 

## Documentation
- Main reports and notes are available in the `docs/` folder as HTML and DOCX files.
- Quarto source files (`*.qmd`) and Jupyter notebooks (`*.ipynb`) provide reproducible analysis workflows.

## Contributing
Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

## Contact
For questions or collaboration, contact org owner.
