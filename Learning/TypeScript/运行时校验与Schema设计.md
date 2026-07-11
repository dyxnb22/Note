# 运行时校验与 Schema 设计

类型在运行时消失，外部数据必须校验。使用 Zod、Valibot、JSON Schema 等将 `unknown` parse 为领域类型；parse 失败返回可定位的字段错误，而不是让 undefined 在深处爆炸。

Schema 应复用基本字段但避免“一套 schema 到处 optional”。区分 create、update、response、internal 模型；版本演进优先新增可选字段，删除/改语义需迁移策略。

`#typescript #schema #validation #zod`
