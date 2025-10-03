--[[
render.lua

Automates rendering of Quarto documents for the FA Grants project.
Switches Quarto config files to render different outputs (docx, full report, standalone files),
and runs post-processing scripts for table formatting. Intended for batch document generation.
]]

-- Step 1: Render the DOCX version using the docx-specific Quarto config
quarto_docx_file = io.open("_quarto_docx.yml", "r") -- Open the DOCX config file
quarto_docx_yaml = quarto_docx_file:read("*a") -- Read entire config
quarto_docx_file:close() -- Close file handle

quarto_yaml = io.open("_quarto.yml", "w") -- Overwrite main config with DOCX config
quarto_yaml:write(quarto_docx_yaml)
quarto_yaml:close()

os.execute("quarto render") -- Render using DOCX config

-- Step 2: Render the full document using the full Quarto config
quarto_full_file = io.open("_quarto_full.yml", "r") -- Open the full config file
quarto_full_yaml = quarto_full_file:read("*a") -- Read entire config
quarto_full_file:close()

quarto_yaml = io.open("_quarto.yml", "w") -- Overwrite main config with full config
quarto_yaml:write(quarto_full_yaml)
quarto_yaml:close()

os.execute("quarto render") -- Render using full config

-- Step 3: Render standalone reference files by temporarily editing the config
-- This disables certain files in the config to allow rendering individual outputs
quarto_file = io.open("_quarto.yml", "w") -- Prepare to edit config for standalone rendering
quarto_full_yaml_edit = string.gsub(quarto_full_yaml, "    - modelling_outcomes_binned.ipynb", "#    - modelling_outcomes_binned.ipynb") -- Comment out binned outcomes notebook
quarto_full_yaml_edit = string.gsub(quarto_full_yaml_edit, "    - aclg_note.qmd", "#    - aclg_note.qmd") -- Comment out ACLG note
quarto_file:write(quarto_full_yaml_edit)

os.execute("quarto render modelling_outcomes_binned.ipynb") -- Render only the binned outcomes notebook
os.execute("quarto render aclg_note.qmd") -- Render only the ACLG note
os.execute("python meta/table_formatter.py") -- Post-process tables in the output

-- Restore the full Quarto config after standalone renders
quarto_yaml = io.open("_quarto.yml", "w") -- Restore main config to full config
quarto_yaml:write(quarto_full_yaml)
quarto_yaml:close()


