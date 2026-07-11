# TypeScript 类型系统基础

TypeScript 在 JavaScript 上增加静态检查，编译后类型会擦除。优先使用 `unknown` 而不是 `any`：unknown 强迫你在使用前验证，any 会让错误穿透整条调用链。

理解 primitive、object、array、tuple、union、literal type、interface 和 type alias。interface 适合可声明合并的对象契约；type 擅长 union、映射和组合。类型应表达业务不变量，而不是为每个局部变量写冗长注解。

`#typescript #types #unknown`
