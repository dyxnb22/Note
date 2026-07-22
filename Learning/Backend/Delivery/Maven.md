# Maven

Maven 通过 POM（Project Object Model）统一描述项目依赖、目录结构和构建流程，主要解决依赖管理、项目构建和多模块协作问题。

## 依赖管理

依赖由 `groupId`、`artifactId` 和 `version` 唯一定位。Maven 会先查本地仓库，再按配置访问远程仓库；团队通常通过私服代理中央仓库并缓存依赖。

常见注意点：

- 依赖具有传递性：A 依赖 B，A 通常也能使用 B 的依赖。
- `mvn dependency:tree` 可排查版本冲突和依赖来源。
- 不需要的传递依赖可用 `<exclusions>` 排除，但要确认运行时确实不需要。
- `compile` 是默认范围；`provided` 由运行环境提供；`runtime` 只在运行和测试时需要；`test` 只对测试编译和运行生效。
- `dependencyManagement` 只负责统一版本，不会自动把依赖加入项目；真正使用仍要在 `<dependencies>` 中声明。

## 生命周期与常用命令

默认生命周期常见阶段为：`validate` → `compile` → `test` → `package` → `verify` → `install` → `deploy`。后面的阶段会包含前面的阶段；`clean` 属于独立的清理生命周期。

```bash
mvn clean test
mvn clean package
mvn verify
mvn install
mvn dependency:tree
```

`package` 只生成当前项目的构件；`install` 写入本地仓库；`deploy` 发布到远程私服。发布前应确认版本、测试结果和构件坐标，避免把快照版本当成稳定版本使用。

## 多模块项目

- 分模块：按职责拆分 `api`、`service`、`repository` 等模块，减少依赖方向混乱。
- 继承：父 POM 提取公共插件、属性和依赖版本；子模块可以覆盖父配置。
- 聚合：父 POM 用 `<modules>` 统一构建多个模块；聚合本身不等于继承，两者可以单独使用。

依赖方向应保持单向，避免模块之间互相依赖；公共接口和实现分离时，要明确谁拥有数据访问和事务边界。

## 私服与版本

- `SNAPSHOT` 表示开发中的可变版本，适合联调，不应作为生产发布版本。
- Release 版本应不可变；发布后不要覆盖同一个坐标的内容。
- 私服应配置权限、代理缓存、构件保留和审计策略，凭据不要硬编码在 `pom.xml` 或提交到 Git。
