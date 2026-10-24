# 专题：Pydantic

> Pydantic 在运行时读取类型注解和校验规则，检查输入数据，并提供序列化接口。示例使用 v2。字段类型和部分业务规则由模型校验；权限、当前资源状态及外部操作结果，由应用代码判断。

## 模型的输入与输出

```python
from pydantic import BaseModel, Field, ValidationError

class Person(BaseModel):
    name: str
    age: int = Field(ge=0)

person = Person(name="小明", age=18)
assert person.age == 18
assert person.model_dump() == {"name": "小明", "age": 18}

try:
    Person(name="小明", age=-1)
except ValidationError:
    pass
else:
    raise AssertionError("年龄不能为负数")
```

`Person` 是类，`person` 是校验后的实例。字段注解给出类型，`Field` 补充约束，`BaseModel` 在构造时执行校验；普通 Python 类型提示本身不做这一步。

`model_dump()` 返回普通字典，不会保存文件或数据库；默认 `mode="python"` 保留部分 Python 类型，`mode="json"` 返回适合 JSON 编码的数据结构。`model_dump_json()` 才直接返回 JSON 字符串。

`name: str | None` 表示允许值为 `None`；加上 `= None` 才同时允许省略字段。

## 运行时校验与静态类型检查

- `dataclass` 主要省去数据类的重复定义，额外校验通常自己实现。Pydantic 在构造或显式校验时执行类型转换与约束；需要这套运行时检查时，再选 Pydantic。
- `mypy`、`pyright` 根据类型标注检查代码中的类型关系，Pydantic 在运行时检查实际输入。两者检查的对象不同，可以配合使用。

## 模型定义

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class UserIn(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[int, Field(gt=0)]
    name: Annotated[str, Field(min_length=1, max_length=64)]
    tags: list[str] = Field(default_factory=list)
    note: str | None = None

first = UserIn(id=1, name="小明")
second = UserIn(id=2, name="小红")
first.tags.append("reader")
assert second.tags == []  # default_factory 为每个模型创建独立列表。
```

- 字段写在类型注解里，可直接嵌套其他模型(`list[User]`、`dict[str, Model]`)或自引用(`parent: Node | None = None`，递归模型)。
- `Field()` 用于声明字段约束、默认值和说明信息，例如 `gt`、`min_length`、`description`、`alias`。
- 已有标准约束能够表达规则时，优先使用它们。这些约束也可以反映在 JSON Schema 中；自定义验证器更适合额外的清洗和组合规则。
- 可以把 `Annotated[int, Field(gt=0)]` 起名为 PositiveInt，让多个字段共用“正整数”这个类型和约束。
- 对不可哈希的默认值，Pydantic 会在创建实例时深拷贝，避免不同实例共享同一个列表等对象。仍建议使用 `default_factory`，明确表达“为每个实例创建默认值”的意图。

## ConfigDict 配置

```python
from pydantic import BaseModel, ConfigDict

class Model(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        validate_by_name=True,  # v2.11+
        validate_by_alias=True,
        from_attributes=True,
    )
    value: int

assert Model(value=1).value == 1
```

上例把配置选项放在一起供查阅。`frozen=True` 禁止字段赋值；要允许赋值并重新校验，就关闭冻结、启用 `validate_assignment=True`。别名配置采用 v2.11+ 写法。

- `strict` 控制是否接受部分类型转换。默认模式下，整数类型字段可以接受字符串 `"1"` 并转换为 `1`；严格模式可以拒绝这类输入。
- 接口是否接受类型转换，要结合字段和 Python／JSON 入口决定；两种入口的严格行为可能不同。
- `validate_assignment` 控制字段重新赋值时是否校验。默认情况下，模型构造后的一般赋值不会再次执行字段校验；开启后，非法赋值会报错。
- `validate_default` 则控制默认值是否接受校验。它与赋值校验解决的是两个不同阶段的问题。
- `extra` 控制声明以外的字段是丢弃、保留还是拒绝。
- `frozen` 限制模型字段的常规重新赋值，不会递归冻结字段中的列表等可变对象。
- validate_by_name 与 validate_by_alias 分别控制是否按字段本名和别名接收输入，具体用法见后文“别名”一节。
- `from_attributes=True` 允许模型从对象属性中读取输入，例如解析 ORM 对象。它不代表模型自动与数据库绑定。

### 默认转换与严格模式

默认模式可能把字符串年龄转成整数，strict=True 会拒绝下面 Python 字典中的这种转换。strict 控制是否接受相应的类型转换；长度、额外字段和默认值仍由各自配置控制。具体规则还要看字段类型，以及输入是 Python 对象还是 JSON。

```python
import json
from pydantic import BaseModel, ConfigDict, Field, ValidationError

class Person(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    age: int = Field(ge=0)
    note: str | None = None

person = Person.model_validate({"name": "小明", "age": "18"})
assert person.age == 18 and isinstance(person.age, int)
assert person.note is None
assert isinstance(person.model_dump(), dict)
assert json.loads(person.model_dump_json())["age"] == 18

for data in [
    {"name": "小明", "age": -1},
    {"name": "", "age": 18},
    {"name": "小明", "age": 18, "unknown": True},
]:
    try:
        Person.model_validate(data)
    except ValidationError:
        pass
    else:
        raise AssertionError("输入不应通过当前模型规则")

class StrictPerson(Person):
    model_config = ConfigDict(strict=True)

try:
    StrictPerson.model_validate({"name": "小明", "age": "18"})
except ValidationError:
    pass
else:
    raise AssertionError("严格模式应拒绝字符串年龄")
assert StrictPerson(name="小明", age=18).age == 18
```

`note: str | None = None` 同时声明允许空值与允许省略。`min_length=1` 只限制字符串长度，不会自动清理空白。

### Python 输入与 JSON 输入的严格性并不完全相同

```python
from datetime import date
from pydantic import TypeAdapter, ValidationError

adapter = TypeAdapter(date)
assert adapter.validate_json('"2026-10-23"', strict=True) == date(2026, 10, 23)
try:
    adapter.validate_python("2026-10-23", strict=True)
except ValidationError:
    pass
else:
    raise AssertionError("Python 严格入口需要 date 对象")
```

JSON 没有原生 date 类型，所以严格模式下，`model_validate_json` 仍可接收规定格式的日期字符串。用 `model_validate` 校验 Python 对象时，则可要求输入本身就是 date。

测试要使用真实接口采用的输入方式，在另一种方式下通过，不代表行为相同。[严格模式与输入来源](https://docs.pydantic.dev/latest/concepts/strict_mode/)

validate_assignment 主要检查字段重新赋值，不会拦截字段中 list 的每次 append。原地修改后，内容可能不再符合模型约束。共享只读快照可使用 tuple 等不可变内容，跨边界重新接收数据时再校验。

### extra 未知字段策略

- `"ignore"`(默认)静默丢弃、`"allow"` 保留成动态属性(`model.extra_field`)、`"forbid"` 报 `extra_forbidden` 错。
- ignore 会丢弃额外字段。拼写错误导致缺少必填字段时，仍然会报错；字段有默认值时，拼写错误则更容易被忽略。接口不接受额外字段时，就设置 `extra="forbid"`。

### 不可变模型

```python
from pydantic import BaseModel, ConfigDict, Field, ValidationError

class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)
    x: int = Field(ge=0)

original = FrozenModel(x=1)
try:
    original.x = 2
except ValidationError:
    pass
else:
    raise AssertionError("冻结字段应拒绝直接赋值")
assert original.x == 1

copy = original.model_copy(update={"x": 2})
assert copy is not original
assert copy.x == 2 and original.x == 1

unchecked = original.model_copy(update={"x": -1})
assert unchecked.x == -1
try:
    FrozenModel.model_validate(original.model_dump() | {"x": -1})
except ValidationError:
    pass
else:
    raise AssertionError("重新校验应拒绝负数")
```

- frozen 禁止常规字段赋值，违反时抛出 `ValidationError`，但不会冻结内部容器。字段值也可哈希时，实例才能作为 dict 的键或放进 set。
- model_copy(update=...) 不校验更新值，因此示例中的 unchecked 可以包含负数。需要校验新数据时，将合并后的字典传给 model_validate；仅把已有模型实例重新传入，默认也不保证重新校验。
- 字段全为不可变值的冻结模型，可以保存一份不易被修改的数据，或作为消息 ID 放进 set。内部字段可变、或更新时跳过校验，仍可能破坏这些约束。

## 校验入口

- v2 新代码使用 `Model.model_validate(data)` 校验已有数据，使用 `model_validate_json()` 校验 JSON 文本或字节；旧的 `validate()` 入口已弃用。
- TypeAdapter 为任意受支持的类型提供校验入口，例如 `TypeAdapter(list[int]).validate_python(["1", "2"])` 得到整数列表。它不要求先把数据包成 BaseModel 字段。
- `model_construct()` 跳过正常校验，只适用于已经可信的数据。它会处理默认值，但可能留下缺少必填字段、或字段类型不符的实例。不要仅凭“可能更快”就使用它。

## 验证器

```python
from typing import Annotated
from pydantic import (
    BaseModel,
    BeforeValidator,
    ValidationError,
    field_validator,
    model_validator,
)

Trimmed = Annotated[
    str, BeforeValidator(lambda v: v.strip() if isinstance(v, str) else v)
]

class Interval(BaseModel):
    note: Trimmed
    lower: int
    upper: int

    @field_validator("note", mode="after")
    @classmethod
    def normalize(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def check_range(self) -> "Interval":
        if self.lower > self.upper:
            raise ValueError("lower must not exceed upper")
        return self

assert Interval(note="  TEST  ", lower=1, upper=3).note == "test"
try:
    Interval(note="test", lower=5, upper=3)
except ValidationError:
    pass
else:
    raise AssertionError("倒置区间应被拒绝")
```

- 字段验证器的 `before` 模式接收类型转换前的原始输入，适合清洗；`after` 模式接收字段校验后的值，适合进一步检查。两者接收到的数据类型可能不同。
model_validator 可以做跨字段校验，不同模式接收到的内容不同：

| 模式 | 接收到什么、怎样处理 |
|---|---|
| before | 接收原始输入，不一定是 dict |
| after | 接收已构造的实例，通常返回 `self` |
| wrap | 拿到默认校验函数，可以在调用前处理输入、调用后处理结果 |
- `ValidationInfo.data` 提供当前字段之前已经校验完成的字段值。因此，读取其他字段时要考虑声明顺序。复杂的跨字段关系通常更适合模型级验证器。
- 上例的模型级 after 验证器检查整个区间，所以报错位置 `loc=()`。模型嵌套在其他字段中时，错误位置还会带上外层字段路径。错误能定位到哪里，取决于验证器放在哪里；跨字段检查也可以定位到具体字段。
- 在 Annotated 中使用 BeforeValidator / AfterValidator，可以让多个字段复用同一个带校验规则的类型。field_validator 将规则写在模型上，指定要校验的字段。两种写法都能通过相应接口读取校验上下文。
- 输入不符合规则时，验证器通常抛出 `ValueError`。错误说明不应包含原始密钥等敏感值，因为它可能被记录或返回给调用方。

## `ValidationError`

- 输入不符合模型约束时，通常会抛出 `ValidationError`，验证器里的编程错误不一定会转成这个异常。`str(exc)` 用于显示多行错误文本；程序要逐项处理错误时，使用 `exc.errors()`。
每条错误记录包含这些字段：

| 字段 | 含义或例子 |
|---|---|
| `loc` | 出错位置，如 `("items", 0, "qty")`；本例的模型级错误为空元组 |
| `type` | 错误类型码，如 `int_type`、`extra_forbidden` |
| `msg` | 错误说明 |
| `input` | 触发错误的原始值 |
| `url` | 对应的官方文档链接 |
| `ctx` | 部分错误附带的参数 |
- 对外错误用 `loc`、`type` 等字段映射成稳定格式。返回前过滤 `input`、`msg` 和 `ctx` 中的敏感值及内部信息，不直接暴露完整异常对象。
- FastAPI 的请求校验错误通常返回 422；内部或响应校验失败通常属于服务器错误，不会把任意 `ValidationError` 都自动转换为 422。自定义错误响应要自己捕获转换。

## 序列化

- `model_dump()` 默认使用 `mode="python"`：嵌套模型会转换为字典，但 `datetime`、`Decimal` 等值仍可保留其 Python 类型。
- `mode="json"` 返回适合 JSON 编码的数据结构，例如将日期时间转换为字符串。它的返回值仍是数据结构；需要 JSON 字符串时，使用 `model_dump_json()`。

序列化时，按输出目的选择参数：

| 参数 | 作用 |
|---|---|
| `exclude_none=True` | 省略值为 `None` 的字段 |
| `exclude_unset=True` | 只导出显式设置过的字段；创建模型后的赋值也算设置 |
| `exclude_defaults=True` | 省略等于默认值的字段 |
| `by_alias=True` | 使用序列化别名 |
| `include` / `exclude` | 显式选择或排除字段 |

`exclude_unset` 常用于部分更新，但是否代表业务中的“字段未修改”，仍需由接口规则确定。

```python
from pydantic import BaseModel

class Profile(BaseModel):
    name: str
    note: str | None = None

omitted = Profile(name="小明")
explicit = Profile(name="小明", note=None)
assert omitted.model_dump() == explicit.model_dump()
assert omitted.model_dump(exclude_unset=True) == {"name": "小明"}
assert explicit.model_dump(exclude_unset=True) == {"name": "小明", "note": None}
assert explicit.model_dump(exclude_none=True) == {"name": "小明"}
omitted.note = "已补充"
assert omitted.model_dump(exclude_unset=True)["note"] == "已补充"
```

两个模型刚创建时，name 都是“小明”，note 都是 None，但创建 explicit 时传入了 note，创建 omitted 时没有。exclude_unset 看字段有没有被设置过，exclude_none 看当前值是不是 None；给 omitted.note 赋值后，它也会被记为已设置。

- model_dump 返回普通 dict，要用字典方式取值，修改它也不会触发模型校验。重新接收外部修改过的数据时，应再次校验。
- 别名、自定义序列化器和计算字段可能让导出再导入后的结果发生变化，往返行为要按实际配置验证。
- 只需模型自身的 JSON 字符串时可直接用 `model_dump_json()`；需要与其他字段组合完整输出时，也可以先 model_dump(`mode="json"`) 再统一编码。

### 自定义序列化

- field_serializer 自定义指定字段的输出，model_serializer 自定义整个模型的输出。
- plain 模式由你直接返回结果；wrap 模式拿到默认序列化函数，可以在调用它之前或之后增加处理。
- when_used 的四个值分别是 always（总是）、unless-none（值非 None 时）、json（JSON 模式）、json-unless-none（JSON 模式且值非 None 时）。这里 JSON 模式也包括 model_dump(mode="json")，并不只指返回字符串。

```python
from pydantic import BaseModel, field_serializer

class Label(BaseModel):
    value: str | None = None

    @field_serializer("value", when_used="json-unless-none")
    def uppercase(self, value: str) -> str:
        return value.upper()

label = Label(value="hello")
assert label.model_dump() == {"value": "hello"}
assert label.model_dump(mode="json") == {"value": "HELLO"}
assert Label().model_dump(mode="json") == {"value": None}
```

上例在 Python 模式下保留原字符串，在 JSON 模式下才调用 uppercase。值为 None 时不调用这个方法，输出中仍保留 None。是否省略该字段，再由 exclude_none 等参数决定。

- 加上 `computed_field` 后，导出模型时也会带上这个属性算出的值。使用时要考虑计算开销和输出字段范围，避免把内部数据一同导出。

## 别名

输入与输出可以使用不同的字段名。先区分以下三个配置项：

```python
from pydantic import BaseModel, Field

class Model(BaseModel):
    value: int = Field(
        alias="VALUE",  # 输出是否使用别名仍由 by_alias 控制
        validation_alias="inputValue",
        serialization_alias="outputValue",
    )

model = Model.model_validate({"inputValue": 3})
assert model.value == 3
assert model.model_dump() == {"value": 3}
assert model.model_dump(by_alias=True) == {"outputValue": 3}
```

- 只给 `alias` 时，校验和序列化共用这个别名；需要不同名称时（如入参用 snake_case、出参用 camelCase），分别设置校验别名和序列化别名。
- v2.11+ 同时接受字段本名和别名时，可配置 `validate_by_name=True`、`validate_by_alias=True`；兼容较早 v2 版本的旧写法是 `populate_by_name=True`。
- `model_dump(by_alias=True)` 按序列化别名输出；`model_validate` 认校验别名。

## 继承与多态

- 模型可以通过继承复用字段，并在子类中增加字段。需要表示多种数据形态时，也可以使用联合类型。
- **判别式联合**：适合带明确类型标签的事件或结构化数据；没有这类标签时可使用普通联合类型。

```python
from typing import Annotated, Literal
from pydantic import Field, BaseModel

class Ok(BaseModel):
    kind: Literal["ok"]
    value: str

class Err(BaseModel):
    kind: Literal["err"]
    code: int

class Result(BaseModel):
    status: Annotated[Ok | Err, Field(discriminator="kind")]

result = Result.model_validate({"status": {"kind": "ok", "value": "完成"}})
assert isinstance(result.status, Ok)
assert result.status.value == "完成"
```

- 判别式联合先根据标签选择分支，再校验该分支的数据。标签无效时会报告对应错误；相比逐个尝试多个模型，调用方通常更容易理解错误位置。
- `RootModel` 可以将列表等单个根值封装成模型，数据通过 `.root` 访问。FastAPI 也支持直接用 `list[Model]` 等类型声明顶层数组；是否封装取决于是否需要模型方法与额外规则。

## 与 FastAPI 集成

- FastAPI 可用 Pydantic 模型声明请求与响应结构。
- `response_model` 用于过滤输出字段和序列化，FastAPI 也用它生成 OpenAPI 定义。没有显式指定时，可以使用框架支持的返回类型注解；框架不会根据每次返回的值临时猜结构。没有输出约束时，要自行检查敏感字段。
- 未知字段策略决定额外输入能否进入，响应字段集合决定输出哪些值，别名规则决定外部名称。各接口可以分别配置。
- 依赖注入的 `Query(...)` 列表参数、路径参数校验底层都是 Pydantic。

## pydantic-settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    database_url: str
    redis_host: str = "localhost"
    debug: bool = False

# 显式关闭 dotenv，示例不读取当前目录 .env。
settings = Settings(database_url="sqlite:///example.db", debug=False, _env_file=None)
assert settings.database_url == "sqlite:///example.db"
assert settings.debug is False
```

- 继承 `BaseSettings` 后，环境变量可自动映射到字段，默认不区分大小写。默认配置下，构造参数优先于环境变量；自定义来源或启用 CLI 后，优先级可能改变。
- 当前示例中的 redis_host 是一个普通字段名，对应环境变量 REDIS_HOST。
- 要让 REDIS__HOST 对应 `redis.host`，需要先声明 redis 这个嵌套模型或字典字段，并设置 `env_nested_delimiter="__"`。
- 列表、字典等复杂的环境变量值，默认通常按 JSON 解析，不会自动按逗号拆分。
- 创建配置对象时检查必填项和字段约束。应用可以在启动阶段完成这一步，尽早暴露配置问题。
- 通过密钥管理系统提供密钥，不要把含密钥的 `.env` 提交到仓库。`repr=False` 只是在显示模型对象时隐藏字段，frozen 只限制赋值；两者都不会自动阻止数据被序列化或写入日志。

## 性能提示

- 批量解析可复用已经创建的 `TypeAdapter`，再根据模型复杂度、验证器与数据规模测量实际收益。
- 同一份可信数据没有变化、也没有新约束时，可以省去重复校验；数据被修改、跨边界流转或换了来源时，按约定重新检查。
- FastAPI 的 OpenAPI schema 通常按需生成并缓存，后续访问复用缓存结果。

## 字段变化对输入、输出与存储的影响

工具参数模型同时生成 JSON Schema、校验输入，说明和执行器就能共用字段定义。HTTP 请求面向不同调用方时，可以另设模型。

字段变动会影响输入、错误信息和输出。例如“没传取消理由”和“显式传 None”是否同义，由业务规则决定；理由若参与幂等操作的输入比较，存储层也要同步修改。

## 参考资料

- [Pydantic 配置与别名输入](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.populate_by_name)
- [FastAPI 响应类型与输出过滤](https://fastapi.tiangolo.com/tutorial/response-model/)
- [Pydantic 可变默认值](https://docs.pydantic.dev/latest/concepts/fields/#mutable-default-values)
- [Pydantic 序列化与字段筛选](https://docs.pydantic.dev/latest/concepts/serialization/)
- [Pydantic 序列化器条件](https://docs.pydantic.dev/latest/api/functional_serializers/)
- [pydantic-settings 环境变量与嵌套配置](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
