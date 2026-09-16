# Maven 与 Gradle 面试问答

## Maven 解决什么问题？

Maven 通过 POM（Project Object Model）统一描述项目依赖、目录结构和构建流程，主要解决依赖管理、项目构建和多模块协作问题。它不是只负责“执行命令”，还通过生命周期、插件和构件坐标把构建过程标准化。

## Maven 如何定位和解析依赖？

依赖由 `groupId`、`artifactId` 和 `version` 唯一定位。Maven 会先查本地仓库，再按配置访问远程仓库；团队通常通过私服代理中央仓库并缓存依赖。

依赖具有传递性：A 依赖 B，A 通常也能使用 B 的依赖。可以用 `mvn dependency:tree` 排查版本冲突和依赖来源；不需要的传递依赖可用 `<exclusions>` 排除，但要确认运行时确实不需要。

## Maven 的依赖范围有什么区别？

- `compile` 是默认范围，参与主代码编译、测试和运行时。
- `provided` 由运行环境提供，例如容器提供的 API，编译时可用但通常不打包。
- `runtime` 不参与主代码编译，但参与运行和测试。
- `test` 只对测试代码的编译和运行生效。

回答范围问题时，要说明它影响的是编译、测试、运行时还是最终构件，而不是只背名称。

## `dependencyManagement` 会自动引入依赖吗？

不会。`dependencyManagement` 只负责统一版本、范围和其他默认配置；真正使用依赖仍要在 `<dependencies>` 中声明。父 POM 常用它管理版本，子模块决定是否实际引入。

## Maven 生命周期和常用命令怎么理解？

默认生命周期常见阶段为：`validate` → `compile` → `test` → `package` → `verify` → `install` → `deploy`。后面的阶段会包含前面的阶段；`clean` 属于独立的清理生命周期。

```bash
mvn clean test
mvn clean package
mvn verify
mvn install
mvn dependency:tree
```

`package` 只生成当前项目的构件；`install` 写入本地仓库；`deploy` 发布到远程私服。发布前应确认版本、测试结果和构件坐标，避免把快照版本当成稳定版本使用。

## Maven 多模块中的继承和聚合有什么区别？

- **继承**：父 POM 提取公共插件、属性和依赖版本，子模块可以覆盖父配置。
- **聚合**：父 POM 用 `<modules>` 统一构建多个模块。

聚合本身不等于继承，两者可以单独使用，也可以同时使用。分模块时常按 `api`、`service`、`repository` 等职责拆分，并保持依赖方向单向，避免模块互相依赖。

## `SNAPSHOT` 和 Release 应该如何使用？

`SNAPSHOT` 表示开发中的可变版本，适合联调，不应作为生产发布版本。Release 版本应不可变，发布后不要覆盖同一个坐标的内容。CI/CD 中应在发布前固定版本、运行测试并保存构件校验信息。

## Maven 私服和凭据有哪些安全边界？

私服应配置权限、代理缓存、构件保留和审计策略；凭据不要硬编码在 `pom.xml` 或提交到 Git。还要限制哪些仓库和构件可以被构建使用，避免依赖投毒或未经审核的构件进入生产。

## 如何验证一次 Maven 构建是否可靠？

至少检查依赖树和最终构件内容，执行 `mvn verify`，确认测试、静态检查和打包结果都通过；对多模块项目还要确认模块构建顺序、依赖方向和发布坐标。遇到“本地能构建、CI 失败”时，优先比较 JDK、Maven、私服、环境变量和缓存，而不是直接删除所有依赖重试。

## Gradle 和 Maven 的核心差异是什么？

核心回答：两者都解决依赖管理和构建自动化。Maven 以 POM、约定生命周期和插件 Goal 为中心，声明性强、团队认知成本低；Gradle 以 Task 图和插件模型为中心，使用 Groovy/Kotlin DSL，定制能力更强，并可通过增量构建和 Build Cache 减少重复工作。选型不能只看一次本地构建速度，还要考虑团队经验、插件生态、IDE/CI 支持和长期维护成本。

Gradle 的灵活性也意味着构建脚本更容易包含隐式逻辑。任务若在配置阶段读取当前时间、网络或机器状态，或者没有正确声明输入输出，缓存和增量结果可能不可靠。公共项目优先使用约定插件和清晰的 Task 依赖，不把业务发布逻辑散落在脚本副作用里。

常见追问：Gradle 脚本可使用 Groovy DSL 或 Kotlin DSL；这只是脚本语言选择，不改变 Gradle 的 Task/Plugin 核心模型。迁移构建工具需要对比最终依赖树、测试、资源、Manifest 和产物内容，而不是“命令能跑通”就结束。

## Gradle 的初始化、配置和执行阶段分别做什么？

核心回答：初始化阶段确定参与构建的项目；配置阶段读取构建脚本、创建并配置 Task 图；执行阶段只运行选中的 Task 及其依赖。理解三阶段的价值是避免在配置阶段做昂贵或带副作用的工作，否则即使某个 Task 最终不执行，也可能付出成本或改变环境。

Task 应明确声明输入、输出和依赖关系，才能让 Up-to-date Check、增量构建和缓存有可靠依据。排查“Task 没执行”时，先看请求的任务、任务图、条件和缓存/输入输出判定，而不是先怀疑业务代码。

## 为什么项目应该提交 Gradle Wrapper？

核心回答：Wrapper 把 Gradle 版本和启动方式固定在项目中，开发机和 CI 通过 `./gradlew` 使用同一声明版本，减少“本地版本不同”造成的构建漂移。应提交 Wrapper 脚本、配置和必要 JAR，并在升级时审查下载地址、校验值、插件兼容和构建结果。

Wrapper 只固定 Gradle 本身，不能自动固定 JDK、插件、仓库中的可变构件、操作系统工具和环境变量。可复现构建还需要固定工具链和依赖版本、保护仓库来源、保存锁定/校验信息，并用干净 CI 环境验证。

## Maven/Gradle 的依赖冲突和供应链风险如何治理？

核心回答：先输出完整依赖图，确认直接/传递来源和最终选中版本，再通过 BOM、`dependencyManagement`、版本约束或平台统一版本；排除依赖后必须运行编译、测试和启动验证。不要在多个子模块各自覆盖同一依赖版本，否则修复和回滚不可追踪。

安全边界包括：限制可信仓库、禁止凭据入库、避免动态/可变版本、校验构件、扫描漏洞与许可证、生成 SBOM，并确保发布构件不可被同坐标覆盖。锁定依赖只能提高可复现性，不能证明依赖没有漏洞或恶意代码。

## 来源与版本边界

- [JavaGuide：Maven 核心概念总结](https://javaguide.cn/tools/maven/maven-core-concepts.html)
- [JavaGuide：Maven 最佳实践](https://javaguide.cn/tools/maven/maven-best-practices.html)
- [JavaGuide：Gradle 核心概念总结](https://javaguide.cn/tools/gradle/gradle-core-concepts.html)

Gradle 的缓存、配置缓存、依赖锁定和校验能力会随版本变化；面试回答应先讲 Task/Plugin/Wrapper 和三阶段模型，具体选项以项目 Wrapper 对应版本为准。
