# ML Workspace

This package contains the trainable NLP/ML pipeline for the grounded UMaT conversational assistant.

Planned responsibilities:

- canonical dataset export from the existing database
- synthetic dialogue generation
- trainable retrieval pipeline
- grounded response generation
- evaluation and artifact loading for experimental inference

Primary local folders:

- `backend/artifacts/umat_nlp_project/`
- `backend/notebooks/`
- `backend/scripts/`

Primary Google Drive folders:

- `MyDrive/umat_nlp_project/data/raw/`
- `MyDrive/umat_nlp_project/data/processed/`
- `MyDrive/umat_nlp_project/data/synthetic/`
- `MyDrive/umat_nlp_project/models/retriever/`
- `MyDrive/umat_nlp_project/models/generator/`
- `MyDrive/umat_nlp_project/metrics/`
- `MyDrive/umat_nlp_project/notebooks/`

Primary one-command runner:

- local or Colab module: `python -m scripts.run_full_ml_pipeline`

What it writes:

- `data/raw/UMaT Lecturer Information Gathering.md`
- `data/raw/seed/*.json`
- `data/processed/canonical_dataset.json`
- `data/synthetic/synthetic_dialogues.json`
- `models/retriever/retriever_artifact.json`
- `models/generator/generator_artifact.json`
- `metrics/retriever_metrics.json`
- `metrics/generator_metrics.json`
- `metrics/evaluation_summary.json`
- `metrics/run_summary.json`
