# Grounded Conversational NLP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a reproducible local-to-Colab training pipeline for a grounded conversational UMaT assistant, replace the current rule-like matching baseline with trainable retrieval and response-generation components, and expose an experimental backend inference path.

**Architecture:** The implementation keeps the current structured UMaT data as the source of truth, generates synthetic multi-turn dialogue data, trains a semantic retriever and a grounded response generator, evaluates both models, and loads exported artifacts through an experimental backend pipeline. The current fuzzy-matching chatbot remains available as a baseline while the ML path is developed and tested.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, pytest, pandas, scikit-learn, sentence-transformers, transformers, torch, Google Colab, Google Drive

---

### Task 1: Create experiment scaffolding

**Files:**
- Create: `docs/plans/README.md`
- Create: `backend/app/ml/__init__.py`
- Create: `backend/app/ml/README.md`
- Create: `backend/app/ml/config.py`
- Create: `backend/scripts/`
- Create: `backend/notebooks/`

**Step 1: Write the failing test**

Create `backend/tests/test_ml_config.py` with:

```python
from app.ml.config import MLSettings


def test_ml_settings_defaults() -> None:
    settings = MLSettings()
    assert settings.project_name == "umat_nlp_project"
    assert settings.drive_root.endswith("umat_nlp_project")
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_ml_config.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `MLSettings`

**Step 3: Write minimal implementation**

Add a small `MLSettings` dataclass or pydantic settings model with:

- project name
- local experiment root
- Google Drive root
- default artifact directories

Create `backend/app/ml/README.md` describing the training/inference folders.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_ml_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_ml_config.py backend/app/ml backend/notebooks docs/plans/README.md
git commit -m "chore: add ml experiment scaffolding"
```

### Task 2: Build canonical knowledge export

**Files:**
- Create: `backend/app/ml/dataset_builder.py`
- Create: `backend/scripts/export_canonical_dataset.py`
- Test: `backend/tests/test_dataset_builder.py`
- Modify: `backend/app/db/models.py`

**Step 1: Write the failing test**

Create `backend/tests/test_dataset_builder.py` with a test that exports canonical records and asserts each staff record includes:

- `entity_id`
- `entity_type`
- `display_name`
- `aliases`
- `facts`

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_dataset_builder.py -v`
Expected: FAIL because the builder module does not exist

**Step 3: Write minimal implementation**

Implement a builder that reads the existing SQLAlchemy models and emits normalized JSON-ready records for:

- staff
- departments
- faculties
- location guides

Prefer adding helper methods or serializers outside the ORM models unless a small utility on the models is clearly cleaner.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_dataset_builder.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_dataset_builder.py backend/app/ml/dataset_builder.py backend/scripts/export_canonical_dataset.py
git commit -m "feat: add canonical dataset export"
```

### Task 3: Add synthetic dialogue schema and generators

**Files:**
- Create: `backend/app/ml/synthetic_data.py`
- Create: `backend/app/ml/templates.py`
- Create: `backend/scripts/generate_synthetic_dialogues.py`
- Test: `backend/tests/test_synthetic_data.py`

**Step 1: Write the failing test**

Create `backend/tests/test_synthetic_data.py` with tests that assert:

- generated examples contain `history`, `user_message`, `target_entity_ids`, `fact_pack`, and `response`
- generated examples cover at least direct lookup and follow-up dialogue families
- responses only include known fact values for the chosen entity

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_synthetic_data.py -v`
Expected: FAIL because synthetic generator modules do not exist

**Step 3: Write minimal implementation**

Implement:

- synthetic example dataclasses or dictionaries
- template families for lookup, location, clarification, correction, greeting, and follow-up turns
- deterministic seeding for reproducibility
- controlled variation for anti-memorization

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_synthetic_data.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_synthetic_data.py backend/app/ml/synthetic_data.py backend/app/ml/templates.py backend/scripts/generate_synthetic_dialogues.py
git commit -m "feat: add synthetic dialogue generation"
```

### Task 4: Create dataset split and leakage checks

**Files:**
- Create: `backend/app/ml/splits.py`
- Create: `backend/scripts/build_training_splits.py`
- Test: `backend/tests/test_splits.py`

**Step 1: Write the failing test**

Create `backend/tests/test_splits.py` with assertions that:

- train, validation, and test all contain data
- held-out template families are excluded from training
- duplicate conversation keys do not appear across splits

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_splits.py -v`
Expected: FAIL because split utilities do not exist

**Step 3: Write minimal implementation**

Implement split helpers that:

- partition by dialogue family or template family
- keep reproducible random seeds
- emit summary counts per split

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_splits.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_splits.py backend/app/ml/splits.py backend/scripts/build_training_splits.py
git commit -m "feat: add dataset split validation"
```

### Task 5: Add a retrieval baseline and benchmark harness

**Files:**
- Create: `backend/app/ml/retriever_baseline.py`
- Create: `backend/app/ml/eval_retriever.py`
- Test: `backend/tests/test_retriever_baseline.py`
- Modify: `backend/app/nlp/retrieval.py`

**Step 1: Write the failing test**

Create `backend/tests/test_retriever_baseline.py` with tests that compare:

- current fuzzy baseline top-1 prediction
- new benchmark wrapper output format
- metric aggregation for top-1 and top-3 accuracy

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_retriever_baseline.py -v`
Expected: FAIL because benchmark helpers do not exist

**Step 3: Write minimal implementation**

Extract or wrap the current fuzzy retrieval logic so it can be evaluated as a baseline against held-out synthetic examples.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_retriever_baseline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_retriever_baseline.py backend/app/ml/retriever_baseline.py backend/app/ml/eval_retriever.py backend/app/nlp/retrieval.py
git commit -m "feat: add retrieval baseline benchmark"
```

### Task 6: Implement trainable neural retriever pipeline

**Files:**
- Create: `backend/app/ml/train_retriever.py`
- Create: `backend/app/ml/retriever_model.py`
- Create: `backend/scripts/train_retriever.py`
- Test: `backend/tests/test_train_retriever.py`
- Modify: `backend/pyproject.toml`

**Step 1: Write the failing test**

Create `backend/tests/test_train_retriever.py` with tests that assert:

- training config parses
- a tiny dataset can be tokenized or embedded
- the trainer produces a metrics dictionary with top-1 and top-3 keys

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_train_retriever.py -v`
Expected: FAIL because the training pipeline does not exist

**Step 3: Write minimal implementation**

Add dependencies for:

- `pandas`
- `scikit-learn`
- `sentence-transformers`
- `torch`

Implement a small retriever training flow that can:

- load processed examples
- build candidate representations
- train or fine-tune a semantic retrieval model
- evaluate on validation data
- export artifacts

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_train_retriever.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_train_retriever.py backend/app/ml/train_retriever.py backend/app/ml/retriever_model.py backend/scripts/train_retriever.py backend/pyproject.toml
git commit -m "feat: add neural retriever training pipeline"
```

### Task 7: Implement grounded response generation pipeline

**Files:**
- Create: `backend/app/ml/train_generator.py`
- Create: `backend/app/ml/generator_model.py`
- Create: `backend/scripts/train_generator.py`
- Test: `backend/tests/test_train_generator.py`
- Modify: `backend/pyproject.toml`

**Step 1: Write the failing test**

Create `backend/tests/test_train_generator.py` with tests that assert:

- grounded dialogue examples can be transformed into model inputs
- generator training config parses
- a tiny training loop returns loss and evaluation metrics

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_train_generator.py -v`
Expected: FAIL because generator training code does not exist

**Step 3: Write minimal implementation**

Add dependencies for:

- `transformers`
- `datasets`
- `evaluate`

Implement a small grounded seq2seq training pipeline that uses:

- dialogue history
- current user message
- fact pack
- target response

Export model weights and tokenizer artifacts.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_train_generator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_train_generator.py backend/app/ml/train_generator.py backend/app/ml/generator_model.py backend/scripts/train_generator.py backend/pyproject.toml
git commit -m "feat: add grounded generator training pipeline"
```

### Task 8: Add evaluation for factuality and dialogue quality

**Files:**
- Create: `backend/app/ml/eval_generator.py`
- Create: `backend/scripts/evaluate_models.py`
- Test: `backend/tests/test_eval_generator.py`

**Step 1: Write the failing test**

Create `backend/tests/test_eval_generator.py` with tests asserting:

- factual field coverage is scored
- generated text can be checked against fact pack values
- evaluation summaries include retrieval and generation sections

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_eval_generator.py -v`
Expected: FAIL because evaluation helpers do not exist

**Step 3: Write minimal implementation**

Implement metrics helpers for:

- factual correctness
- field coverage
- response length sanity checks
- optional BLEU and ROUGE logging

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_eval_generator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_eval_generator.py backend/app/ml/eval_generator.py backend/scripts/evaluate_models.py
git commit -m "feat: add grounded dialogue evaluation"
```

### Task 9: Create Colab-ready training notebook

**Files:**
- Create: `backend/notebooks/grounded_conversational_nlp_colab.ipynb`
- Create: `backend/notebooks/README.md`
- Test: `backend/tests/test_notebook_manifest.py`

**Step 1: Write the failing test**

Create `backend/tests/test_notebook_manifest.py` with tests that assert the notebook:

- exists
- contains Google Drive mount steps
- references the expected `umat_nlp_project` folder layout
- runs the dataset, retriever, generator, and evaluation stages in order

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_notebook_manifest.py -v`
Expected: FAIL because the notebook does not exist

**Step 3: Write minimal implementation**

Create a Colab notebook that:

- mounts Google Drive
- installs project dependencies
- reads raw and synthetic data from Drive
- trains retriever and generator
- logs metrics to files
- exports artifacts to Drive
- runs a few sample conversations

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_notebook_manifest.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_notebook_manifest.py backend/notebooks/grounded_conversational_nlp_colab.ipynb backend/notebooks/README.md
git commit -m "docs: add colab training notebook"
```

### Task 10: Add backend experimental inference path

**Files:**
- Create: `backend/app/ml/inference.py`
- Create: `backend/app/ml/fact_pack.py`
- Test: `backend/tests/test_ml_inference.py`
- Modify: `backend/app/api/chat.py`
- Modify: `backend/app/schemas/chat.py`
- Modify: `backend/app/core/config.py`

**Step 1: Write the failing test**

Create `backend/tests/test_ml_inference.py` with tests asserting:

- experimental mode can be enabled by config
- a mocked retriever and generator can answer a simple staff query
- responses include the chosen mode and top grounded matches

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_ml_inference.py -v`
Expected: FAIL because experimental inference path does not exist

**Step 3: Write minimal implementation**

Add an experimental inference pipeline that:

- loads exported retriever and generator artifacts
- builds fact packs from top-ranked records
- generates grounded responses
- falls back cleanly if artifacts are unavailable

Expose mode metadata in the chat response so experiments are easy to compare.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_ml_inference.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_ml_inference.py backend/app/ml/inference.py backend/app/ml/fact_pack.py backend/app/api/chat.py backend/app/schemas/chat.py backend/app/core/config.py
git commit -m "feat: add experimental ml chat inference"
```

### Task 11: Add end-to-end smoke script and documentation

**Files:**
- Create: `backend/scripts/run_ml_smoke_test.py`
- Create: `backend/tests/test_smoke_pipeline.py`
- Modify: `backend/app/ml/README.md`
- Modify: `frontend/README.md`

**Step 1: Write the failing test**

Create `backend/tests/test_smoke_pipeline.py` with tests that assert the smoke script can:

- load sample data
- run a tiny retriever training pass
- run a tiny generator training pass
- print saved artifact locations

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_smoke_pipeline.py -v`
Expected: FAIL because the smoke pipeline script does not exist

**Step 3: Write minimal implementation**

Implement a reproducible smoke script and document:

- local quick-start
- Colab workflow
- Drive folder expectations
- artifact export/import flow

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_smoke_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests/test_smoke_pipeline.py backend/scripts/run_ml_smoke_test.py backend/app/ml/README.md frontend/README.md
git commit -m "docs: add ml smoke test workflow"
```

### Task 12: Run full verification

**Files:**
- Modify: `docs/plans/2026-03-21-grounded-conversational-nlp-implementation.md`

**Step 1: Run targeted tests**

Run:

```bash
pytest backend/tests/test_ml_config.py -v
pytest backend/tests/test_dataset_builder.py -v
pytest backend/tests/test_synthetic_data.py -v
pytest backend/tests/test_splits.py -v
pytest backend/tests/test_retriever_baseline.py -v
pytest backend/tests/test_train_retriever.py -v
pytest backend/tests/test_train_generator.py -v
pytest backend/tests/test_eval_generator.py -v
pytest backend/tests/test_notebook_manifest.py -v
pytest backend/tests/test_ml_inference.py -v
pytest backend/tests/test_smoke_pipeline.py -v
```

Expected: PASS

**Step 2: Run broader backend regression tests**

Run:

```bash
pytest backend/tests -v
```

Expected: PASS with the legacy and experimental chat paths both covered

**Step 3: Record outcomes**

Update this plan with the final commands that were run, the metrics files that were generated, and any deviations from the original plan.

**Step 4: Commit**

```bash
git add docs/plans/2026-03-21-grounded-conversational-nlp-implementation.md
git commit -m "chore: record ml pipeline verification"
```

## Verification Record

Completed on 2026-03-21 in branch `feature/grounded-conversational-nlp-local`.

Commands run:

```bash
pytest backend/tests/test_ml_config.py -v
pytest backend/tests/test_dataset_builder.py -v
pytest backend/tests/test_synthetic_data.py -v
pytest backend/tests/test_splits.py -v
pytest backend/tests/test_retriever_baseline.py -v
pytest backend/tests/test_train_retriever.py -v
pytest backend/tests/test_train_generator.py -v
pytest backend/tests/test_eval_generator.py -v
pytest backend/tests/test_notebook_manifest.py -v
pytest backend/tests/test_ml_inference.py -v
pytest backend/tests/test_smoke_pipeline.py -v
pytest backend/tests -v
```

Observed result:

- all targeted ML workflow tests passed
- broader backend regression suite passed
- final backend suite result: `16 passed`

Artifacts and workflow created:

- canonical dataset export script
- synthetic dialogue generation script
- training split builder
- local retriever and generator training pipeline
- evaluation script
- Colab notebook scaffold
- experimental ML inference path in the chat API
- local smoke-test script for end-to-end validation

Implementation deviations from the ideal plan:

- per-task git commits were not created because the repository started with only a `.gitignore` root commit and the rest of the project existed as untracked files
- the first runnable local training pipeline uses lightweight in-repo implementations so the workflow can execute immediately before heavier Colab dependencies are installed
