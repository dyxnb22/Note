# DeepPath Lab Agent Guide

This repository is designed for iterative execution by Cursor Cloud Agent or similar coding agents.

## Mission

Build DeepPath Lab as an original, project-based deep learning learning repository.

Each module should gradually accumulate:

- original notes,
- a minimal reproduction baseline,
- a from-scratch implementation,
- experiments or ablations,
- a final report.

Each module should also have a recognizable project identity, such as a mini engine, trainer, classifier, generator, or retrieval system.

## Start Here

Read these files in order before making substantial changes:

1. [README.md](./README.md)
2. [docs/agent-execution.md](./docs/agent-execution.md)
3. [docs/d2l-mapping.md](./docs/d2l-mapping.md)
4. [TASKS.md](./TASKS.md)

## Core Rules

- Do not copy external textbook content into the repository.
- Use D2L and other public material as references only.
- Prefer original Markdown notes, plain scripts, and small experiments.
- Prefer minimal, reviewable progress over large speculative scaffolds.
- When implementing math-heavy logic, add numerical sanity checks when practical.
- Keep module progress visible by updating `notes.md`, `report.md`, or module `README.md`.
- Treat NLP as a major destination of the roadmap, not a side topic.

## Default Working Pattern

For the selected module:

1. Refine scope from `docs/d2l-mapping.md`.
2. Update the module `README.md` if needed.
3. Add or improve original notes.
4. Add one baseline reproduction artifact.
5. Add one from-scratch artifact.
6. Add one experiment or diagnostic artifact.
7. Summarize progress in `report.md`.
8. Make sure the module still reads as one independent learning project.

## Good Next Actions

When the repository is still early-stage, strong default actions are:

- create minimal runnable scripts rather than full frameworks,
- add a tiny dataset or synthetic example if external data is unavailable,
- record open questions instead of pretending the module is finished,
- leave concise TODOs at the module level when stopping mid-module.

## Avoid

- copying D2L prose, figures, or code,
- creating large app frameworks before the modules have substance,
- adding empty boilerplate across many future modules,
- claiming a module is complete without experiments and a report.
