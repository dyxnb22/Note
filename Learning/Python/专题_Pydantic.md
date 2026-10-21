# 专题：Pydantic

> Pydantic 根据类型注解和显式规则，在运行时校验数据并完成序列化。示例使用 v2。它可以表达部分业务规则，但权限、资源状态和外部操作结果仍需应用代码判断。

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

`Person` 是类，`person` 是校验后实例。字段注解描述类型，`Field` 补充约束。普通 Python 类型提示不会自动校验；这里由 `BaseModel` 的构造机制读取并执行规则。

`model_dump()` 返回普通字典，不会保存文件或数据库；默认 `mode="python"` 保留部分 Python 类型，`mode="json"` 返回适合 JSON 编码的数据结构。`model_dump_json()` 才直接返回 JSON 字符串。

`name: str | None` 表示允许值为 `None`；加上 `= None` 才同时允许省略字段。模型构造、字典输出和外部保存是不同步骤，应分别理解。

## 运行时校验与静态类型检查

- `dataclass` 主要减少数据类的重复定义；额外校验通常需要手动实现。Pydantic 则在模型构造或显式校验时执行类型转换与约束。选择时要看是否需要运行时校验，而不是只比较两者的写法。
- `mypy`、`pyright` 根据类型标注检查代码中的类型关系；Pydantic 检查实际输入是否符合模型规则。静态检查通过，不代表运行时输入一定合法；两种检查互相补充。

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
- 与 `Annotated` 组合(`Annotated[int, Field(gt=0)]`)让类型和约束分离，约束可起名复用。
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

配置项不是必须全部一起启用的清单。例如 `frozen=True` 会禁止字段赋值；希望允许赋值但重新校验，应另用 `validate_assignment=True`，而不是期待它绕过冻结限制。示例使用 v2.11+ 的别名配置。

- `strict` 控制是否接受部分类型转换。默认模式下，整数类型字段可以接受字符串 `"1"` 并转换为 `1`；严格模式可以拒绝这类输入。
- 具体行为取决于字段类型和输入格式。应先明确接口允许什么，再选择严格模式，不要把所有数据入口一概设置成相同策略。
- `validate_assignment` 控制字段重新赋值时是否校验。默认情况下，模型构造后的一般赋值不会再次执行字段校验；开启后，非法赋值会报错。
- `validate_default` 则控制默认值是否接受校验。它与赋值校验解决的是两个不同阶段的问题。
- `extra` 控制声明以外的字段是丢弃、保留还是拒绝。
- `frozen` 限制模型字段的常规重新赋值，不会递归冻结字段中的列表等可变对象。
- v2.11+ 推荐用 validate_by_name 与 validate_by_alias 分别控制字段本名和别名是否可用于输入；旧代码的 `populate_by_name=True` 相当于两者都开启。
- `from_attributes=True` 允许模型从对象属性中读取输入，例如解析 ORM 对象。它不代表模型自动与数据库绑定。

### 默认转换与严格模式

默认校验可能将兼容输入转换为声明的类型，例如把字符串年龄转换为整数。strict=True 对下面的 Python 字典输入拒绝这种转换；它不代表所有输入来源、所有字段类型都采用完全相同的接受规则。字段约束、未知字段策略和默认值仍各自生效。

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

### extra 未知字段策略

- `"ignore"`(默认)静默丢弃、`"allow"` 保留成动态属性(`model.extra_field`)、`"forbid"` 报 `extra_forbidden` 错。
- ignore 会丢弃额外字段；如果拼写错误导致缺少必填字段，仍然会报错。有默认值的字段更容易掩盖拼写问题。需要拒绝未知字段的边界可显式使用 forbid。

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

- 常规字段赋值抛 `ValidationError`；frozen 不递归冻结内部容器。只有字段值也可哈希，实例才可成功用于哈希容器。
- model_copy(update=...) 不校验更新值，因此示例中的 unchecked 可以包含负数。需要校验新数据时，将合并后的字典传给 model_validate；仅把已有模型实例重新传入，默认也不保证重新校验。
- 典型用途包括值快照和适合哈希的消息标识；仍需避免通过内部可变字段或跳过校验的通道破坏约定。

## 校验入口

- v2 新代码使用 `Model.model_validate(data)` 校验已有数据，使用 `model_validate_json()` 校验 JSON 文本或字节；旧的 `validate()` 入口已弃用。
- TypeAdapter 为任意受支持的类型提供校验入口，例如 `TypeAdapter(list[int]).validate_python(["1", "2"])` 得到整数列表。它不要求先把数据包成 BaseModel 字段。
- `model_construct()` 跳过正常校验，适用于已经可信的数据。它会处理默认值，但不会替你补齐缺失的必填字段；由此产生的对象可能不满足正常模型约定。不要仅凭“可能更快”就使用它。

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
- model_validator 可做跨字段校验：before 接收原始输入，不一定是 dict；after 接收已构造实例，通常返回 `self`；wrap 可在调用默认处理器前后插入逻辑。
- `ValidationInfo.data` 提供当前字段之前已经校验完成的字段值。因此，读取其他字段时要考虑声明顺序。复杂的跨字段关系通常更适合模型级验证器。
- 上例由模型级 after 验证器抛出的区间错误，位置 loc 为空元组；若模型嵌套在其他字段中，外层错误位置还会包含嵌套路径。错误位置取决于校验发生的位置，不是所有跨字段检查都只能报在根上。
- Annotated 中的 BeforeValidator / AfterValidator 可以将规则绑定到可复用的类型。field_validator 将规则绑定到模型中的指定字段；两类写法都能通过相应接口获得校验上下文，主要区别在于规则如何组织与复用。
- 输入不符合规则时，验证器通常抛出 `ValueError`。错误说明不应包含原始密钥等敏感值，因为它可能被记录或返回给调用方。

## `ValidationError`

- 正常输入约束失败通常组织为 `ValidationError`；验证器中的编程错误等不一定转换成它。`str(exc)` 是多行可读文本，结构化消费用 `exc.errors()`。
- 每条错误的键：`loc`(出错位置元组，如 `("items", 0, "qty")`，模型级错误为空元组)、`type`(错误类型码，如 `int_type` / `extra_forbidden`)、`msg`(人类可读)、`input`(触发的原始值)、`url`(官方文档锚点)；有参数的错误还有 `ctx`。
- 对外错误可以通过 `loc`、`type` 等字段映射为稳定的接口格式。返回前应检查 `input`、`msg` 和 `ctx` 是否包含敏感值或内部信息，避免直接暴露完整异常对象。
- FastAPI 的请求校验错误通常返回 422；内部或响应校验失败通常属于服务器错误，不会把任意 `ValidationError` 都自动转换为 422。自定义错误响应要自己捕获转换。

## 序列化

- `model_dump()` 默认使用 `mode="python"`：嵌套模型会转换为字典，但 `datetime`、`Decimal` 等值仍可保留其 Python 类型。
- `mode="json"` 返回适合 JSON 编码的数据结构，例如将日期时间转换为字符串。它的返回值仍是数据结构；需要 JSON 字符串时，使用 `model_dump_json()`。

序列化时，按输出目的选择参数：

| 参数 | 作用 |
|---|---|
| `exclude_none=True` | 省略值为 `None` 的字段 |
| `exclude_unset=True` | 排除仍被记录为未显式设置的字段；后续赋值也会更新这份记录 |
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

两个模型刚创建时字段值相同，但显式提供的字段不同。exclude_unset 根据字段是否被显式设置过筛选，exclude_none 根据当前值筛选；后续给 omitted.note 赋值后，它也会被记录为已设置。

- 导出的字典不再具有模型实例的字段访问与校验行为。需要重新接收外部修改后的数据时，应再次校验。
- 导出再导入不一定是无损往返。别名、自定义序列化器和计算字段都可能改变结果；应按具体配置验证。
- 只需模型自身的 JSON 字符串时可直接用 `model_dump_json()`；需要与其他字段组合完整输出时，也可以先 model_dump(`mode="json"`) 再统一编码。

### 自定义序列化

- field_serializer 自定义指定字段的输出，model_serializer 自定义整个模型的输出。plain 直接给出结果，wrap 取得默认处理器后可在调用前后加工结果。
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

Python 模式保持原字符串，JSON 模式调用序列化器；None 不进入该方法，仍保留为 None，是否删除字段由 exclude_none 等参数另行控制。

- `computed_field` 可以将计算属性纳入序列化结果。使用时要考虑计算成本和输出字段范围，不应因此意外暴露内部数据。

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

- 只给 `alias` 时校验和序列化共用；要分开(如入参 snake_case、出参 camelCase)分别传。
- v2.11+ 同时接受字段本名和别名时，可配置 `validate_by_name=True`、`validate_by_alias=True`；兼容较早 v2 版本的旧写法是 `populate_by_name=True`。
- `model_dump(by_alias=True)` 按序列化别名输出；`model_validate` 认校验别名。

## 继承与多态

- 模型可以通过继承复用字段，并在子类中增加字段。需要表示多种数据形态时，也可以使用联合类型；若数据具有明确标签，判别式联合通常更容易定位分支和错误。
- **判别式联合**（适合具有明确类型标签的事件或结构化数据，不是所有联合类型都必须使用）：

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

- FastAPI 可用模型处理请求与响应；默认请求校验错误通常是 422，响应校验失败通常是服务器错误，不能混为同一路径。
- `response_model` 控制输出过滤与序列化，并驱动 OpenAPI schema；未显式指定时可从有效的返回类型注解推导；并非从每次实际返回值自动推断。无输出约束时，应特别检查敏感字段。
- 对外接口应明确未知字段策略、响应字段集合和别名规则。它们共同决定调用方能发送什么、收到什么，不要求所有接口采用同一套配置。
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

- 继承 `BaseSettings`，环境变量自动映射字段名(大小写不敏感)，默认常规来源顺序中，构造参数优先于环境变量；自定义来源或 CLI 可改变顺序。
- 当前示例的 redis_host 是平面字段，对应环境变量 REDIS_HOST。只有声明 redis 这样的嵌套模型或字典字段后，REDIS__HOST 才能借助 env_nested_delimiter="__" 映射为内部的 host。列表、字典等复杂环境值默认通常按 JSON 解析，不是自动按逗号拆分。
- 创建配置对象时检查必填项和字段约束。应用可以在启动阶段完成这一步，尽早暴露配置问题。
- 密钥仍由密钥管理注入，不写进 `.env` 提交；`repr=False` 只影响表示形式，frozen 只限制赋值，均不能独立防止敏感数据被序列化或记录。

## 性能提示

- 批量解析可以使用 `TypeAdapter`，并复用已经创建的适配器。是否值得优化，应根据模型复杂度、验证器和数据规模测量，不预先假定某种写法总是更快。
- 避免在没有新校验需求时反复校验同一份可信数据。但对象经过修改、跨边界流转或来自不同来源时，仍应按约定重新检查。
- FastAPI 的 OpenAPI schema 通常按需生成并缓存，不应笼统认定一定在启动阶段预先生成。

## 参考资料

- [Pydantic 配置与别名输入](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.populate_by_name)
- [FastAPI 响应类型与输出过滤](https://fastapi.tiangolo.com/tutorial/response-model/)

- [Pydantic 可变默认值](https://docs.pydantic.dev/latest/concepts/fields/#mutable-default-values)
- [Pydantic 序列化与字段筛选](https://docs.pydantic.dev/latest/concepts/serialization/)
- [Pydantic 序列化器条件](https://docs.pydantic.dev/latest/api/functional_serializers/)
- [pydantic-settings 环境变量与嵌套配置](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
