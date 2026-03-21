# Grounded Conversational NLP Design

**Date:** 2026-03-21

**Goal:** Replace the current keyword and fuzzy-match chatbot backend with a small trainable NLP/ML pipeline that can support grounded, conversational responses over the UMaT staff and campus dataset and later accept voice-transcribed input.

## Current State

The existing backend is a single-turn retrieval system centered on:

- text normalization in `backend/app/nlp/normalize.py`
- rule-like entity detection in `backend/app/nlp/entity_ruler.py`
- keyword intent detection in `backend/app/nlp/intents.py`
- RapidFuzz scoring in `backend/app/nlp/retrieval.py`
- response templates in `backend/app/nlp/response_builder.py`

This stack is useful as a baseline, but it behaves more like matching than learned language understanding. It is not designed for conversational follow-ups, semantic retrieval, or trainable response generation.

## Product Boundary

The assistant will remain domain-bounded. It will not be an open-domain chatbot.

Version 1 will support:

- greetings and short social turns that stay within the assistant domain
- staff, faculty, and department lookup
- specialization lookup
- office and location guidance
- clarification turns
- follow-up turns using recent conversational context

Version 1 will not support:

- unrestricted open-domain chat
- unsupported factual invention
- long-term memory beyond a short dialogue window
- voice processing itself

Voice is treated as a future input layer. The conversational NLP pipeline should accept plain text so that speech-to-text can be connected later without changing the core model flow.

## Recommended Architecture

The recommended architecture is a grounded neural retrieval plus grounded response generation pipeline.

### 1. Dialogue Context Builder

This component converts the current user message and a short history window into a structured training and inference example.

Responsibilities:

- normalize the current user utterance
- preserve recent turns for follow-up questions
- track the latest referenced entity where possible
- prepare model-ready inputs for retrieval and response generation

This is what allows queries such as "where is his office?" after a prior staff lookup.

### 2. Grounded Neural Retriever

This component replaces keyword-heavy matching with a trainable semantic retrieval model.

Responsibilities:

- encode user utterances and dialogue-aware queries
- rank staff, department, faculty, and location records
- return top-k candidate records with confidence scores

Recommended first version:

- sentence-embedding or dual-encoder ranking model
- trained on real plus synthetic user utterances
- evaluated with retrieval metrics such as top-1 accuracy and recall@k

### 3. Fact Pack Builder

This component converts the top retrieved records into a compact factual context for the generator.

Responsibilities:

- collect fields needed for answering
- assemble staff, department, faculty, campus, office guidance, and specialization facts
- provide a stable grounded representation for generation

This layer is the main protection against hallucination. The generator should answer from this fact pack, not from unconstrained latent memory.

### 4. Conversational Response Generator

This component produces natural-language answers from:

- current user message
- short dialogue history
- grounded fact pack

Recommended first version:

- a small seq2seq model
- trained on grounded dialogue-response pairs
- designed to produce short, accurate, conversational domain answers

The generator should remain domain-bounded and grounded by construction.

## Training And Runtime Strategy

Training and runtime should be split across local development and Google Colab.

### Local Responsibilities

- inspect and validate source data
- generate synthetic dialogue data
- preprocess and split datasets
- run smoke-test training jobs on small subsets
- verify exported artifacts can be loaded by the backend
- compare the new pipeline against the current baseline

### Google Colab Responsibilities

- full training runs
- validation and metrics tracking
- artifact export
- report-ready experiment logging
- end-to-end conversational evaluation

### Google Drive Layout

The Colab workflow should assume a single project folder in Google Drive, for example:

- `MyDrive/umat_nlp_project/data/raw/`
- `MyDrive/umat_nlp_project/data/processed/`
- `MyDrive/umat_nlp_project/data/synthetic/`
- `MyDrive/umat_nlp_project/models/retriever/`
- `MyDrive/umat_nlp_project/models/generator/`
- `MyDrive/umat_nlp_project/metrics/`
- `MyDrive/umat_nlp_project/notebooks/`

This layout keeps datasets, checkpoints, metrics, and exported models organized for academic reporting.

## Dataset Design

The current structured dataset is the factual source of truth, but not sufficient by itself for conversational training. The project should create a grounded dialogue corpus with three layers.

### 1. Canonical Knowledge Records

Normalize the structured UMaT records into a consistent knowledge format for:

- staff members
- departments
- faculties
- location guides

Each record should expose fields such as:

- names and aliases
- role
- department
- faculty
- campus
- office guidance
- specializations
- optional bio or source notes

### 2. Supervised Retrieval Dataset

Create training pairs where the input is a user utterance and the label is the correct record or records.

This dataset should include:

- direct questions
- paraphrased questions
- polite conversational variants
- ambiguous questions
- correction turns
- follow-up turns

### 3. Grounded Dialogue Generation Dataset

Each example should contain:

- conversation history
- current user message
- retrieved fact pack
- target response

The target response should be conversational but strictly bounded by the retrieved facts.

## Synthetic Data Strategy

Synthetic data is necessary because the real dataset is structured and small. However, diversity matters more than raw volume.

Synthetic data should be generated from controlled programs and templates that vary:

- wording
- tone
- sentence order
- dialogue length
- ambiguity
- follow-up style
- correction behavior

Dialogue families should include:

- greeting plus task transition
- direct lookup
- role lookup
- specialization lookup
- location lookup
- ambiguous reference
- clarification
- pronoun follow-up
- correction
- polite closing

Anti-memorization principles:

- multiple paraphrase families for the same semantic goal
- held-out phrasing templates in validation and test
- held-out dialogue structures in test
- challenge examples with noisy conversational wording
- negative examples and confusing near-matches

Every synthetic target answer must be derivable from the supporting record. Unsupported facts must not be invented for the sake of conversational variety.

## Evaluation

The evaluation design should measure generalization, factuality, and conversational usefulness.

### Data Splits

- `train`: majority of synthetic and transformed examples
- `validation`: held-out phrasing families
- `test`: held-out phrasing styles and dialogue structures
- `challenge_test`: optionally messy or ambiguous conversational examples

### Retriever Metrics

- top-1 accuracy
- top-3 accuracy
- recall@k
- MRR
- performance by query family

### Generator Metrics

- factual correctness against the fact pack
- field coverage when specific facts are requested
- response fluency and readability
- dialogue consistency across turns

Standard text-generation metrics such as BLEU or ROUGE may be logged, but they should not be the primary success criteria.

### Practical Success Criteria

The first usable version should demonstrate that:

- the retriever outperforms the current fuzzy baseline on held-out examples
- the generator produces grounded answers from retrieved facts
- the system handles paraphrased and follow-up inputs it did not see in the same surface form during training

## Implementation Scope

The first implementation pass should create the data and experimentation path before fully replacing the backend.

Phase 1 should deliver:

- dataset builder from current UMaT structured data
- synthetic dialogue generator
- local smoke-test training pipeline
- Colab-ready notebook
- retrieval and generation evaluation scripts
- backend adapter for experimental inference

The backend integration should begin as an experimental mode so that the current rule-based pipeline remains available as a baseline during testing.

## Risks And Mitigations

### Risk: Generator Hallucination

Mitigation:

- use grounded fact packs
- keep answers short
- bound the domain
- evaluate factuality explicitly

### Risk: Synthetic Data Memorization

Mitigation:

- diversify templates and dialogue structures
- hold out template families
- evaluate on challenge sets

### Risk: Small Real Dataset

Mitigation:

- use the structured dataset as source truth
- generate broad synthetic conversational coverage
- keep the domain narrow

### Risk: Local Resource Limits

Mitigation:

- use local smoke runs only
- use Colab for full training
- export compact artifacts for backend use

## Deliverables

The approved implementation should create:

- reproducible dataset generation code
- synthetic dialogue generation code
- local smoke-test training code
- Google Colab notebook and Drive-compatible paths
- evaluation scripts and saved metrics
- backend integration hooks for experimental inference

## Decision Summary

The project will use a hybrid in-house NLP architecture:

- learned neural retrieval for grounding
- learned response generation for conversational style
- structured fact packs for accuracy
- Google Colab for main training
- local environment for validation and integration

This provides a defendable academic ML/NLP project while still producing a practically useful conversational assistant for the UMaT domain.
