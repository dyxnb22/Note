# Hard Dedup v2 — Git Diff Review

- Review base: `master...agent-kb-hard-dedup-v2`
- Source files reviewed: **20/20**
- Planned formal-question removals: **33**
- Actual formal-question removals: **33**
- Unplanned title removals: **0**
- Retained-title mapping: **703/703**
- Section/preamble changes outside adjudicated questions: **0**
- Numbering or numeric-anchor errors: **0**

## Corrections made

Full old-answer versus survivor/follow-up comparisons found seven places where the first rewrite preserved the Atom but compressed a useful implementation qualifier. The review restored:

- task-level lock/serial-writer and deterministic merge choices for shared State;
- cancellation propagation, shared-State merge rules, dependency Trace and replay order for parallel tools;
- Token/time budgets for Multi-Agent loop control;
- discoverable/loadable/versioned semantics in the Skill differential answer;
- explicit recovery-report states and human-confirmation handoff;
- hidden/time-split/new-sample evaluation isolation;
- layer/head/batch/materialization factors in the Attention complexity follow-up.

No deleted formal question was restored because no unplanned deletion or independent interview intent loss was found. Phase 7B and Phase 8B were regenerated after these corrections and remain passed at 703 questions and 319/319 active Atom coverage.
