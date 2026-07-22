# DeepPath Lab Tasks

This file gives Cursor Cloud Agent a concrete execution queue.

Every module in the queue should be treated as a standalone learning project, not just a chapter summary.

## Priority Order

1. Finish `01_preliminaries_autograd`
2. Finish `02_linear_models`
3. Finish `03_mlp`
4. Finish `04_cnn`
5. Create later modules only after the first four have meaningful content

## Definition Of Meaningful Progress

A module has meaningful progress when it contains at least:

- original notes with specific concepts explained,
- one runnable baseline reproduction artifact,
- one runnable or partially runnable from-scratch artifact,
- one experiment, visualization, or diagnostic,
- a report with concrete observations.

## Module Lifecycle

Only the current module gets the full working layout (`notes.md`,
`reproduce/`, `from_scratch/`, `experiments/`, and `report.md`). Later modules
keep a `README.md` scope card until the previous module meets the meaningful
progress criteria. This is intentional: an empty folder is not progress, and
the next module should be opened by a concrete implementation task.

## Active Queue

### Module 01: Preliminaries & Autograd

Immediate next tasks:

- write initial original notes for autograd basics
- implement a minimal scalar autograd engine
- add a simple gradient check script
- write a short report with lessons and limitations

Practical project outcome:

- a mini autograd engine that can power simple scalar graph backpropagation

Suggested artifact targets:

- `modules/01_preliminaries_autograd/from_scratch/value.py`
- `modules/01_preliminaries_autograd/experiments/gradient_check.py`
- `modules/01_preliminaries_autograd/report.md`

### Module 02: Linear Models

Immediate next tasks:

- write notes for linear regression and softmax regression
- implement linear regression from scratch
- add a small framework baseline for comparison
- write an experiment note about optimization behavior

Practical project outcome:

- a compact linear-model playground for regression and softmax classification

Suggested artifact targets:

- `modules/02_linear_models/from_scratch/linear_regression.py`
- `modules/02_linear_models/reproduce/baseline.py`
- `modules/02_linear_models/experiments/optimization_notes.md`

### Module 03: MLP

Immediate next tasks:

- write original notes on hidden layers, activations, and backpropagation
- implement a minimal MLP training script
- compare at least two activations or optimizers
- summarize failure cases in the report

Practical project outcome:

- a tiny MLP trainer with training diagnostics and comparison experiments

Suggested artifact targets:

- `modules/03_mlp/from_scratch/mlp.py`
- `modules/03_mlp/experiments/activation_comparison.md`
- `modules/03_mlp/report.md`

### Module 04: CNN

Immediate next tasks:

- write original notes on convolution, padding, stride, and pooling
- implement a minimal convolution or pooling routine from scratch
- reproduce LeNet on a small image dataset
- add an error analysis section to the report

Practical project outcome:

- a LeNet-style image classification project with visual diagnostics

Suggested artifact targets:

- `modules/04_cnn/from_scratch/conv2d.py`
- `modules/04_cnn/reproduce/lenet_baseline.py`
- `modules/04_cnn/experiments/error_analysis.md`

## Planned Later Queue

- `05_modern_cnn`: image benchmark project
- `06_rnn`: character-level text generator
- `07_lstm_gru`: gated sequence modeling project
- `08_attention_transformer`: mini transformer and attention visualization
- `11_nlp_pretraining`: embedding or masked language modeling project
- `12_nlp_applications`: text classification, retrieval, or sequence labeling project

## Agent Stop Rule

If unsure what to do next, pick the highest-priority module that lacks runnable code and add the smallest original artifact that moves it forward.
