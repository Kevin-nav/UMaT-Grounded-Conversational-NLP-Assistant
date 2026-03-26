# Colab Setup Checklist

Use this when preparing the notebook run and Google Drive output structure for the grounded conversational NLP pipeline.

## What You Need Before Running

- A Google account with access to Google Colab and Google Drive.
- A Drive folder at `MyDrive/umat_nlp_project/`.
- Access to the repo at `https://github.com/Kevin-nav/UMaT-Grounded-Conversational-NLP-Assistant.git`.
- The notebook file: `backend/notebooks/grounded_conversational_nlp_colab.ipynb`.

## What You Do Not Need To Upload First

Do not pre-upload these items to Drive:

- raw markdown source
- seed JSON files
- processed datasets
- synthetic dialogues
- trained model artifacts
- metrics files

The notebook pipeline creates them automatically.

## Exact Colab Flow

Run the notebook cells in order. The notebook:

1. mounts Google Drive
2. clones the repo into `/content/NLP_Project`
3. installs backend dependencies
4. runs:

```bash
python -m scripts.run_full_ml_pipeline --output-root /content/drive/MyDrive/umat_nlp_project
```

## Expected Drive Layout After Training

After a successful run, Drive should contain:

```text
MyDrive/umat_nlp_project/
  data/
    raw/
      UMaT Lecturer Information Gathering.md
      seed/
        *.json
    processed/
      canonical_dataset.json
    synthetic/
      synthetic_dialogues.json
  models/
    retriever/
      retriever_artifact.json
    generator/
      generator_artifact.json
  metrics/
    retriever_metrics.json
    generator_metrics.json
    evaluation_summary.json
    run_summary.json
```

## What To Upload For Submission

If your instructor asks for notebook evidence and trained outputs, the safest upload set is:

- the completed notebook file
- the `metrics/` folder
- the `models/` folder
- optionally `data/processed/canonical_dataset.json`
- optionally `data/synthetic/synthetic_dialogues.json`

If the submission instructions only ask for proof of training, `metrics/run_summary.json` and the notebook are the minimum high-signal artifacts.

## Quick Validation

The repo currently passes:

- notebook manifest test
- smoke pipeline test

Local commands used:

```powershell
cd backend
python -m pytest tests/test_notebook_manifest.py -v
python -m pytest tests/test_smoke_pipeline.py -v
```
