# Roadmap

DeepPath Lab follows a staged learning path from deep learning fundamentals to practical NLP systems.

The intent is not just to read through topics in order. Each module should become an independent, understandable mini-project that teaches one important idea by making it concrete.

## Tracks

- Track A: Foundations
- Track B: Deep Learning Core
- Track C: Sequence Models and Transformers
- Track D: Computer Vision
- Track E: NLP and Representation Learning
- Track F: Recommender Systems and Reinforcement Learning
- Track G: Modern Extensions

## Learning Stages

| Stage | Focus | Why It Exists |
|---|---|---|
| Stage 1 | Foundations | understand tensors, gradients, losses, and optimization basics |
| Stage 2 | Core Deep Learning | learn hidden layers, nonlinear representations, and training dynamics |
| Stage 3 | Vision and Sequence Modeling | develop intuition for structure in images and sequences |
| Stage 4 | Transformers and Representation Learning | connect attention, embeddings, and scalable sequence modeling |
| Stage 5 | NLP Projects | apply the foundations to text modeling, classification, retrieval, and fine-tuning |

## Active Modules

| Module | Track | Focus | Practical Project | Expected Outputs |
|---|---|---|---|---|
| 01 Preliminaries & Autograd | Track A | tensors, gradients, computational graphs | mini autograd engine | notes, gradient checks, autograd core, short implementation report |
| 02 Linear Models | Track A | regression, classification, optimization basics | linear-model playground for regression and softmax classification | linear regression, softmax regression, baseline comparison, optimization notes |
| 03 Multilayer Perceptrons | Track B | nonlinear function approximation, backpropagation | tiny MLP trainer with activation and optimizer diagnostics | MLP implementation, training curves, activation study, training report |
| 04 Convolutional Neural Networks | Track D | convolutions, pooling, visual pattern extraction | LeNet-style image classifier with feature analysis | CNN from scratch pieces, LeNet reproduction, visual diagnostics, error analysis |

## Planned Learning Path

| Order | Module | Track | Practical Project |
|---|---|---|---|
| 05 | Modern CNN | Track D | image classification benchmark comparing classic CNN families |
| 06 | RNN | Track C | character-level text generator or simple sequence predictor |
| 07 | LSTM & GRU | Track C | gated sequence modeling project for text or time series |
| 08 | Attention & Transformer | Track C | attention visualization project and mini transformer |
| 09 | Optimization | Track B | optimizer comparison lab across earlier models |
| 10 | Computer Vision Applications | Track D | transfer learning or detection mini-project |
| 11 | NLP Pretraining | Track E | embedding or masked language modeling project |
| 12 | NLP Applications | Track E | text classification, retrieval, or sequence labeling project |
| 13 | NLP Fine-Tuning | Track E | small fine-tuning study on a downstream task |
| 14 | Recommender Systems | Track F | neural or factorization-based recommendation mini-project |
| 15 | Reinforcement Learning | Track F | compact control or policy-learning project |

## Alignment Rule

The route should stay coherent:

1. start from first principles,
2. build one real project per module,
3. reach sequence models and transformers before advanced NLP work,
4. keep NLP as a major destination rather than an afterthought.

## Working Rule

Do not treat the roadmap as a reading checklist only. Each module should end with original code, experiments, and written conclusions.
