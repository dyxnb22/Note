# D2L Mapping

This file maps D2L chapters to DeepPath Lab modules in an agent-friendly format.

Use it as execution context, not as source material to copy. The links below point to the official D2L references. This repository should only contain original notes, implementations, experiments, and reports.

## How To Use This File

For each active module, the expected workflow is:

1. Read the linked D2L chapter or section.
2. Write original notes in the module `notes.md`.
3. Reproduce a minimal baseline in `reproduce/`.
4. Implement the core mechanism in `from_scratch/`.
5. Run focused ablations or diagnostics in `experiments/`.
6. Summarize outcomes in `report.md`.

## Active Modules

| Module | Status | D2L Reference | Official Link | Practical Project | Required Outputs | Done Criteria |
|---|---|---|---|---|---|---|
| 01 Preliminaries & Autograd | active | 2.5. Automatic Differentiation | <https://d2l.ai/chapter_preliminaries/autograd.html> | mini autograd engine | original autograd notes, gradient sanity checks, mini autograd implementation | notes explain graph and chain rule, gradients are numerically checked on simple expressions, `from_scratch/` contains a minimal autograd core, `report.md` summarizes what worked and what was confusing |
| 02 Linear Models | active | 3. Linear Neural Networks for Regression | <https://d2l.ai/chapter_linear-regression/index.html> | linear-model playground for regression | linear regression notes, scratch implementation, baseline comparison | `from_scratch/` includes linear regression training logic, `reproduce/` contains a framework baseline, experiments compare loss behavior or generalization, report explains key findings |
| 02 Linear Models | active | 4. Linear Neural Networks for Classification | <https://d2l.ai/chapter_linear-classification/> | softmax classification mini-project | softmax regression notes, scratch implementation, classification baseline | `from_scratch/` includes softmax regression, `reproduce/` includes a concise baseline, experiments inspect accuracy or misclassifications, report explains differences from regression |
| 03 MLP | active | 5. Multilayer Perceptrons | <https://d2l.ai/chapter_multilayer-perceptrons/index.html> | tiny MLP trainer with diagnostics | MLP notes, training baseline, scratch MLP, activation or optimization experiments | notes explain hidden layers and activations, `from_scratch/` implements core MLP logic, experiments visualize training behavior, report records failure modes and fixes |
| 03 MLP | active | 5.3. Forward Propagation, Backward Propagation, and Computational Graphs | <https://d2l.ai/chapter_multilayer-perceptrons/backprop.html> | backprop analysis companion for the MLP trainer | computational graph notes, backward pass analysis, training report section | notes explain forward and backward flow in the user's own words, experiments or diagnostics inspect gradients, report connects theory to implementation |
| 04 CNN | active | 7. Convolutional Neural Networks | <https://d2l.ai/chapter_convolutional-neural-networks/> | convolution and pooling lab | convolution notes, pooling notes, scratch convolution or pooling code | `from_scratch/` includes at least one convolution-related implementation, experiments inspect kernels or feature maps, report explains why convolutions differ from fully connected layers |
| 04 CNN | active | 7.6. Convolutional Neural Networks (LeNet) | <https://d2l.ai/chapter_convolutional-neural-networks/lenet.html> | LeNet-style image classifier | LeNet reproduction on Fashion-MNIST, training curves, error analysis | `reproduce/` contains a working LeNet baseline, `experiments/` includes at least one diagnostic or error analysis, report summarizes model behavior and limitations |

## Planned Later Modules

| Planned Module | D2L Reference | Official Link | Practical Project | Expected Outputs |
|---|---|---|---|---|
| Modern CNN | 8. Modern Convolutional Neural Networks | <https://d2l.ai/chapter_convolutional-modern/index.html> | image classification benchmark comparing CNN families | architecture comparison notes, AlexNet/VGG/ResNet reproductions, design tradeoff report |
| RNN | 9. Recurrent Neural Networks | <https://d2l.ai/chapter_recurrent-neural-networks/index.html> | character-level text generator or simple sequence predictor | sequence modeling notes, minimal RNN, BPTT experiments |
| LSTM & GRU | 10. Modern Recurrent Neural Networks | <https://d2l.ai/chapter_recurrent-modern/index.html> | gated text or time-series modeling project | gated RNN comparison, long-range dependency experiments, report |
| Attention & Transformer | 11. Attention Mechanisms and Transformers | <https://d2l.ai/chapter_attention-mechanisms-and-transformers/index.html> | attention visualization and mini transformer project | attention visualizations, self-attention implementation, mini transformer |
| Optimization | 12. Optimization Algorithms | <https://d2l.ai/chapter_optimization/index.html> | optimizer comparison lab across earlier modules | optimizer comparisons, learning-rate experiments, diagnostics report |
| Computer Vision Applications | 14. Computer Vision | <https://d2l.ai/chapter_computer-vision/index.html> | transfer learning or detection mini-project | augmentation, fine-tuning, detection or segmentation experiments |
| NLP Pretraining | 15. Natural Language Processing: Pretraining | <https://d2l.ai/chapter_natural-language-processing-pretraining/index.html> | embedding or masked language modeling project | embedding or pretraining notes, word2vec/BERT-related experiments |
| NLP Applications | 16. Natural Language Processing: Applications | <https://d2l.ai/chapter_natural-language-processing-applications/index.html> | text classification, retrieval, or sequence labeling project | downstream NLP task experiments, fine-tuning report |
| Reinforcement Learning | 17. Reinforcement Learning | <https://d2l.ai/chapter_reinforcement-learning/index.html> | compact control or policy-learning project | MDP notes, value iteration or Q-learning experiments |
| Recommender Systems | 21. Recommender Systems | <https://d2l.ai/chapter_recommender-systems/index.html> | recommendation mini-project on MovieLens or similar data | MovieLens experiments, matrix factorization or ranking baseline |

## Agent Notes

- Do not copy D2L text, code, figures, or chapter summaries verbatim into this repository.
- When a module is incomplete, prefer adding the smallest original artifact that moves it forward: a note stub, a baseline script, an experiment plan, or a report skeleton.
- If a D2L chapter is broader than the module, extract only the subset needed to produce the listed outputs.
- When in doubt, bias toward original experiments and concise written conclusions over large amounts of scaffolding.
