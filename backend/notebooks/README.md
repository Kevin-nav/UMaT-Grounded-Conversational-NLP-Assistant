# Colab Notebook

Use `grounded_conversational_nlp_colab.ipynb` in Google Colab. The notebook now clones the repo, installs backend dependencies, and runs one script:

- `python -m scripts.run_full_ml_pipeline --output-root /content/drive/MyDrive/umat_nlp_project`

Required Drive location:

- `MyDrive/umat_nlp_project/`

You do not need to pre-upload the JSON files or models. The script creates these folders and writes all artifacts into them:

- `data/raw/`
- `data/processed/`
- `data/synthetic/`
- `models/retriever/`
- `models/generator/`
- `metrics/`
