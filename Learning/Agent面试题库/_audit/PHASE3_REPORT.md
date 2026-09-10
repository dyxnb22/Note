# Phase 3 — Question → Atom Map Freeze

本阶段完成 736 道正式题的 Question → Atom 映射，并完成 Phase 2 Gate 后的语义收尾。现有题库正文未修改；所有新增或更新内容均位于 `_audit`。

## Phase 2 Gate 结论

Phase 2 历史注册表保持不变，通过迁移覆盖层形成 Phase 3 effective registry：

- 历史注册表：318 个原子；
- effective registry：320 个条目；
- effective active：319；
- pending：0；
- `PROMPT-006` 判定为组合场景而非独立最小知识原子，已 deprecated，并由 `EVAL-001`、`DATA-001`、`EVAL-013`、`EVAL-022` 组合表达；
- `Reward Model` / `Value Model` 不再作为 PPO 别名，新增 `LLM-027` 与 `LLM-028` 独立表达；
- `OPS-006` canonical owner 调整到 `external:Backend/Architecture`。

Phase 3 只使用 effective registry，不覆写 Phase 2 历史文件。

## Phase 3 结果

| 项目 | 结果 |
| --- | ---: |
| Inventory questions | 736 |
| Mapped questions | 736 |
| Question coverage | 100% |
| Effective active atoms | 319 |
| Covered active atoms | 319 |
| Uncovered active atoms | 0 |
| Unknown atom refs | 0 |
| Pending semantic reviews | 0 |
| Explicit/manual reviewed mappings | 354 |
| Phase 2 source-evidence mappings | 382 |
| Unreviewed semantic candidates | 0 |

`phase3_validation.json` 当前为 `structural_status: passed`，错误列表为空。

## 映射方法

证据优先级保持为：

1. `_audit/phase3_maps/*.json` 中的显式语义裁决；
2. Phase 2 `source_question_ids` 形成的直接来源证据；
3. 语义相似度仅生成待审候选，不能自动升级为最终映射。

原先 216 道 similarity-only pending 中，有 11 道实际已经存在于 `04_Tool与协议.json` 的 manual shard，只是总表未在该 shard 提交后重建；剩余 205 道逐项建立显式映射后重新执行 `phase3_build.py`。最终总表为 354 manual + 382 source evidence，未留下 similarity-only 结果。

## 语义审查原则

Question → Atom Map 采用“主答案合同优先”的保守映射，不把答案里顺带出现的每个概念都挂成 Atom。

例如跨主题系统设计题可能同时提到限流、幂等、Trace、权限和 Provider，但只有构成该题稳定考察合同的知识才进入映射。这样可以避免综合题因原子集合无限膨胀，在下一阶段被错误判成与大量基础题高度重复。

重点复核了以下高风险区域：

- Tool / MCP / Skill / 权限边界；
- Durable / Checkpoint / Lease / unknown side effect；
- Eval / Trace / Replay / 发布门禁；
- RAG / GraphRAG / 摄取与权限；
- 模型推理、Tool Executor 与手撕题；
- `13_跨主题综合题` 的组合知识表达。

Phase 3 只回答“这道题主要覆盖哪些稳定知识原子、考察意图是什么”，不提前执行重复关系裁决。

## 验证

通过 GitHub Actions 在独立分支重建并执行冻结门禁，要求同时满足：

- `inventory_questions == 736`
- `mapped_questions == 736`
- `question_coverage == 1.0`
- `pending_semantic_reviews == 0`
- `unknown_atom_refs == []`
- `uncovered_active_atoms == []`
- `unreviewed_semantic_candidates == 0`

全部通过。

## 正文保护

本阶段没有修改 25 个正式题目 Markdown，也没有修改 review / navigation Markdown。相对于 `agent-kb-dedup-v1` 的变化仅为 `_audit` 资产；临时 CI 配置已恢复到原状态。

## Phase 3 Freeze

**状态：PASS / FROZEN**

现在可以进入 Phase 4：Duplicate Candidate Clustering。

Phase 4 仍不得直接改正文。候选生成应基于：

`Atom overlap + Interview Intent + Answer Contract + Canonical Ownership`

相似度只能用来召回候选；真正的 `KEEP / MERGE / CONVERT_TO_FOLLOWUP / MOVE_OR_BRIDGE / SPLIT / DELETE` 决策留到后续 adjudication。
