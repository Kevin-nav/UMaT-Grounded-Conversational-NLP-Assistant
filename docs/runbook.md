# Grounded Conversational NLP Runbook

## Branch Sync

Your local `master` can be behind `origin/master`. Check with:

```powershell
git fetch origin
git log --oneline --decorate master..origin/master
```

If `master` is clean, fast-forward it with:

```powershell
git switch master
git pull --ff-only origin master
```

If `git status --short` shows local changes or untracked files that would be overwritten, move or commit them first.

## Local Backend Setup

From the repo root:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Local Test Run

From `backend/`:

```powershell
pytest tests/test_smoke_pipeline.py -v
python -m scripts.run_ml_smoke_test
python -m scripts.run_full_ml_pipeline
```

Outputs are written under:

```text
backend/artifacts/umat_nlp_project/
```

## Colab Setup

You do not need to pre-upload the JSON files, models, or metrics. The pipeline generates them.

You only need:

- a Google Drive folder at `MyDrive/umat_nlp_project/`
- access to this GitHub repo: `https://github.com/Kevin-nav/UMaT-Grounded-Conversational-NLP-Assistant.git`

Notebook flow:

1. Open `backend/notebooks/grounded_conversational_nlp_colab.ipynb` in Colab.
2. Run the cells in order.
3. The notebook clones the repo into `/content/NLP_Project`, installs dependencies, and runs one script.

Direct Colab commands:

```bash
git clone https://github.com/Kevin-nav/UMaT-Grounded-Conversational-NLP-Assistant.git /content/NLP_Project
cd /content/NLP_Project/backend
python -m pip install --upgrade pip
python -m pip install -e .
python -m scripts.run_full_ml_pipeline --output-root /content/drive/MyDrive/umat_nlp_project
```

## Colab Output Layout

After the run, Drive will contain:

```text
MyDrive/umat_nlp_project/
  data/raw/UMaT Lecturer Information Gathering.md
  data/raw/seed/
  data/processed/canonical_dataset.json
  data/synthetic/synthetic_dialogues.json
  models/retriever/retriever_artifact.json
  models/generator/generator_artifact.json
  metrics/retriever_metrics.json
  metrics/generator_metrics.json
  metrics/evaluation_summary.json
  metrics/run_summary.json
```
