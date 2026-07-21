# Agent Execution Rules

This repository is designed to be workable by cloud agents without embedding external textbook content.

The high-level objective is to move from deep learning fundamentals toward practical NLP capability, with one concrete mini-project per module.

## Source Policy

- Treat D2L, CS231n, CS224N, and similar resources as references only.
- Link to external chapters instead of copying their text, images, or code.
- Write only original notes, code, experiments, and reports inside this repository.

## Per-Module Workflow

1. Read the mapped external references in [d2l-mapping.md](./d2l-mapping.md).
2. Update the module `README.md` if the scope becomes clearer.
3. Write or refine `notes.md` in original language.
4. Add one minimal reproduction artifact under `reproduce/`.
5. Add one minimal from-scratch artifact under `from_scratch/`.
6. Add one experiment, ablation, or diagnostic under `experiments/`.
7. Update `report.md` with results, limitations, and next steps.

## Delivery Standard

A module should not be considered done just because code runs once.

Minimum expected outputs:

- original notes
- a clearly identifiable project outcome
- a reproducible baseline
- a from-scratch implementation or core mechanism
- at least one experiment or diagnostic
- a written report

## Default Biases For Agents

- Prefer small, reviewable commits over large speculative scaffolds.
- Prefer clarity over framework cleverness.
- Prefer scripts and plain Markdown over notebook-only work.
- Prefer adding tests or numerical sanity checks when implementation correctness matters.
- Prefer documenting failure cases, not just successful runs.

## Stop Conditions

Pause and ask for direction if:

- a task would require copying external material,
- the module scope expands beyond the mapped references,
- the implementation depends on unavailable datasets, credentials, or paid services,
- there is a major ambiguity about whether to prioritize notes, code, or experiments.
