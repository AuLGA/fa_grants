from glob import glob
import json
import os

for file in glob("*.qmd"):
    if os.path.exists(file):
        with open(file, "r") as f:
            content = f.read()
        
        if "{{< pagebreak >}}" not in content:
            with open(file, "w") as f:
                # Add page break at the end of the file
                f.write(content + "\n{{< pagebreak >}}")

for file in glob("*.ipynb"):
    if os.path.exists(file):
        with open(file, "r") as f:
            content = f.read()
        
        if "{{< pagebreak >}}" not in content:
            nb = json.loads(content)

            nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "{{< pagebreak >}}"
            ]
        })
            
        with open(file, "w") as f:
            json.dump(nb, f)