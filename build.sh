mamba init
mamba activate fagrants

quarto render

git add .
git commit -m "Update book metadata and add new content"
git push origin main