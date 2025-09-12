-- Render the docx file
quarto_docx_file = io.open("_quarto_docx.yml", "r")
quarto_docx_yaml = quarto_docx_file:read("*a")
quarto_docx_file:close()

quarto_yaml = io.open("_quarto.yml", "w")
quarto_yaml:write(quarto_docx_yaml)
quarto_yaml:close()

os.execute("quarto render")

-- Render the whole document

quarto_full_file = io.open("_quarto_full.yml", "r")
quarto_full_yaml = quarto_full_file:read("*a")
quarto_full_file:close()

quarto_yaml = io.open("_quarto.yml", "w")
quarto_yaml:write(quarto_full_yaml)
quarto_yaml:close()

os.execute("quarto render")
