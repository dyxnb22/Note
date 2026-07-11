# Docker

## 1. Docker 核心概念
Docker 的核心目标是把应用和它依赖的运行环境一起打包，让应用在不同机器上都能以相同方式运行。

| 概念 | 作用 | 面试表达 |
| --- | --- | --- |
| 镜像 (Image) | 静态模板，包含代码、依赖、环境和启动配置 | 类似“安装包”或“类” |
| 容器 (Container) | 镜像运行后的实例，有自己的进程、文件系统和网络空间 | 类似“进程”或“对象实例” |
| 仓库 (Repository) | 存放镜像的地方，例如 Docker Hub、私有镜像仓库 | 用于拉取和分发镜像 |
| Dockerfile | 构建镜像的脚本 | 描述镜像怎么从基础镜像一步步构建出来 |
| Docker Compose | 多容器编排工具 | 用一个 `docker-compose.yml` 管理多个服务 |

镜像是只读模板，容器是运行时实例。一个镜像可以启动多个容器，容器删除后不会影响镜像。

镜像采用分层存储（Union File System），每条 Dockerfile 指令生成一个只读层，多个容器共享相同的底层，节省磁盘空间。容器在镜像层之上叠加一个可写层，容器删除后该层消失，数据不持久化。

Docker 底层依赖两个 Linux 内核特性：namespace 负责隔离（进程、网络、文件系统、用户等资源视图各自独立），cgroup 负责限制（CPU、内存、磁盘 IO 等资源的使用上限）。这也是容器比虚拟机轻量的根本原因：没有 Hypervisor 和 Guest OS，直接共享宿主机内核。

---

## 2. Docker 常用命令速查

### 2.1 镜像管理
| 命令 | 用途 |
| --- | --- |
| `docker pull nginx` | 从仓库拉取镜像 |
| `docker images` | 查看本地镜像 |
| `docker build -t my-app:1.0 .` | 根据当前目录的 Dockerfile 构建镜像 |
| `docker rmi <image_id>` | 删除镜像 |

### 2.2 容器管理
| 命令 | 用途 |
| --- | --- |
| `docker run -d --name web -p 8080:80 nginx` | 后台启动 nginx 容器，并把宿主机 8080 映射到容器 80 |
| `docker ps` | 查看正在运行的容器 |
| `docker ps -a` | 查看所有容器，包括已停止的容器 |
| `docker logs -f <container_name>` | 持续查看容器日志 |
| `docker stop <container_name>` | 停止容器 |
| `docker rm <container_name>` | 删除已停止的容器 |

### 2.3 进入容器执行命令
`docker exec` 用于在运行中的容器内执行命令。

```bash
docker exec -it mysql bash
docker exec -it redis redis-cli
```

常见参数：
- `-i`：保持标准输入打开。
- `-t`：分配伪终端。
- `-it`：交互式进入容器。

如果容器没有 `bash`，可以改用 `sh`：

```bash
docker exec -it alpine sh
```

### 2.4 数据卷与文件拷贝
| 命令 | 用途 |
| --- | --- |
| `docker volume ls` | 查看数据卷 |
| `docker volume rm <volume>` | 删除数据卷 |
| `docker cp a.txt web:/tmp/a.txt` | 把宿主机文件复制到容器 |
| `docker cp web:/var/log/nginx/access.log .` | 把容器文件复制到宿主机 |

---

## 3. Dockerfile 核心知识

Dockerfile 是镜像构建脚本，本质上是一系列有顺序的指令。

### 3.1 常见指令
| 指令 | 作用 |
| --- | --- |
| `FROM` | 指定基础镜像 |
| `WORKDIR` | 设置工作目录 |
| `COPY` | 复制文件到镜像中 |
| `ADD` | 功能类似 COPY，但支持自动解压和远程 URL |
| `RUN` | 构建阶段执行命令，生成新镜像层 |
| `ENV` | 设置环境变量 |
| `EXPOSE` | 声明容器暴露端口 |
| `CMD` | 指定容器默认启动命令 |
| `ENTRYPOINT` | 指定容器入口命令 |

### 3.2 一个常见 Dockerfile 示例
```dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/demo.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

执行逻辑：
1. 以 `openjdk:17-jdk-slim` 为基础镜像。
2. 工作目录切到 `/app`。
3. 把本地 `target/demo.jar` 复制到镜像中，命名为 `app.jar`。
4. 声明应用使用 8080 端口。
5. 容器启动时执行 `java -jar app.jar`。

### 3.3 CMD 和 ENTRYPOINT 区别
这是面试高频问题。

`CMD`：提供默认命令，如果 `docker run` 后面追加命令，会覆盖它。

`ENTRYPOINT`：定义主命令，`docker run` 后追加内容通常会作为参数传给它，不会完全替换。

示例：

```dockerfile
CMD ["echo", "hello"]
```

运行：

```bash
docker run my-image
```

输出：

```bash
hello
```

如果运行：

```bash
docker run my-image ls
```

则 `CMD` 会被 `ls` 覆盖。

而如果写成：

```dockerfile
ENTRYPOINT ["echo", "hello"]
```

运行：

```bash
docker run my-image world
```

实际执行接近：

```bash
echo hello world
```

所以：
- `CMD` 更适合“默认参数/默认命令”。
- `ENTRYPOINT` 更适合“固定入口程序”。
- 两者也可以组合使用：`ENTRYPOINT` 定义主程序，`CMD` 提供默认参数。

---

## 4. 如何减少镜像体积

这是实际开发和面试都会问到的问题。

常见优化手段：

### 4.1 选择更小的基础镜像
例如：
- `openjdk:17-jdk` 很大。
- `openjdk:17-jdk-slim` 更轻量。
- Alpine 系列更小，但某些库兼容性要注意。

### 4.2 合并 RUN 指令
减少镜像层数量：

```dockerfile
RUN apt-get update && apt-get install -y curl vim && rm -rf /var/lib/apt/lists/*
```

### 4.3 清理构建缓存
安装依赖后删除临时文件、包缓存，否则它们会跟着进入镜像层。

### 4.4 使用多阶段构建
典型做法是前一阶段编译，后一阶段只复制最终产物：

```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /build
COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /build/target/demo.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

优点：
- 构建工具和源码不进入最终镜像。
- 镜像更小。
- 更安全。

### 4.5 使用 `.dockerignore`
避免把无关文件复制进镜像：

```gitignore
.git
node_modules
target
logs
*.md
```

---

## 5. Docker Compose

Compose 用于定义和运行多个相互关联的容器。比如一个项目里同时有：
- `app`
- `mysql`
- `redis`
- `nginx`

如果只用 `docker run`，命令会很长，还不好维护。Compose 可以把这些信息写进一个 YAML 文件里统一管理。

### 5.1 一个典型示例
```yaml
services:
  mysql:
image: mysql:8.0
container_name: mysql
restart: always
environment:
  MYSQL_ROOT_PASSWORD: 123456
  MYSQL_DATABASE: demo
ports:
  - "3306:3306"
volumes:
  - mysql_data:/var/lib/mysql

  redis:
image: redis:7
container_name: redis
restart: always
ports:
  - "6379:6379"

  app:
build: .
container_name: demo-app
depends_on:
  - mysql
  - redis
ports:
  - "8080:8080"

volumes:
  mysql_data:
```

### 5.2 常见字段解释
| 字段 | 作用 |
| --- | --- |
| `services` | 定义所有服务 |
| `image` | 直接使用现成镜像 |
| `build` | 根据当前目录 Dockerfile 构建镜像 |
| `container_name` | 指定容器名称 |
| `ports` | 端口映射 |
| `volumes` | 挂载目录或数据卷 |
| `environment` | 设置环境变量 |
| `depends_on` | 定义启动依赖关系 |
| `restart` | 定义重启策略 |

### 5.3 Compose 常用命令
| 命令 | 用途 |
| --- | --- |
| `docker compose up -d` | 后台启动所有服务 |
| `docker compose down` | 停止并删除容器、网络 |
| `docker compose ps` | 查看服务状态 |
| `docker compose logs -f` | 查看日志 |
| `docker compose up -d --build` | 重新构建并启动 |

### 5.4 `depends_on` 的注意点
`depends_on` 只保证“启动顺序”，不保证“服务已经真正可用”。

例如 app 依赖 mysql，mysql 容器虽然先启动了，但数据库可能还在初始化，此时 app 仍然可能连接失败。

解决方式：
- 应用里增加重试机制。
- 配置健康检查（healthcheck）。
- 启动脚本等待依赖服务 ready。

---

## 6. Docker 网络

Docker 容器之间可以通过网络互通。

常见网络模式：
- `bridge`：默认模式，同一 bridge 网络内的容器可以互通。
- `host`：直接使用宿主机网络，没有独立网络命名空间。
- `none`：没有网络。

在 Compose 中，同一个 `docker-compose.yml` 下的服务默认就在同一个网络，可以直接通过服务名访问。

例如：
- `app` 连接 MySQL 时主机名写 `mysql`
- `app` 连接 Redis 时主机名写 `redis`

而不是 `127.0.0.1`。

这是很多新手最容易犯的错误。

---

## 7. 数据持久化

容器本身是临时的，删除容器后，其可写层数据也会丢失。

所以数据库、日志、上传文件等需要持久化。

两种常见方式：

### 7.1 Bind Mount
把宿主机目录挂到容器里：

```bash
docker run -v /data/mysql:/var/lib/mysql mysql:8
```

优点：直观、方便直接查看宿主机文件。

### 7.2 Volume
使用 Docker 管理的数据卷：

```bash
docker volume create mysql_data
docker run -v mysql_data:/var/lib/mysql mysql:8
```

优点：更适合生产，和宿主机目录解耦。

---

## 8. 常见问题与面试高频题

### 8.1 Docker 和虚拟机有什么区别
Docker 容器共享宿主机内核，只隔离进程和资源；虚拟机是完整虚拟出一套硬件，再跑一个独立操作系统。

所以：
- 容器更轻量。
- 启动更快。
- 资源开销更小。
- 部署密度更高。

但虚拟机隔离更彻底。

### 8.2 Docker 为什么启动快
因为容器本质上是宿主机上的一个受隔离进程，不需要像虚拟机那样额外启动 Guest OS。

### 8.3 容器删除后数据为什么会丢
因为数据默认写在容器可写层，容器删除后这层也没了。要想持久化，必须挂载 volume 或宿主机目录。

### 8.4 Dockerfile 中 `COPY` 和 `ADD` 区别
`COPY` 更纯粹，只负责复制文件。
`ADD` 除了复制，还支持自动解压压缩包和下载 URL。

实际开发通常优先使用 `COPY`，除非明确需要 `ADD` 的额外能力。

### 8.5 一个镜像可以启动多个容器吗
可以。镜像是模板，容器是实例。就像一个类可以创建多个对象。

### 8.6 为什么说 Docker Compose 适合开发环境
因为它非常适合在单机上统一编排多个服务，便于本地联调和测试。

如果是大规模生产环境编排，通常会进一步使用 Kubernetes。

---

## 9. 实战经验总结

开发中常见建议：

1. 应用、数据库、缓存尽量用 Compose 管理，方便一键启动。
2. 数据库、Redis 等有状态服务一定挂载 volume。
3. 不要在容器里直接存重要业务文件而不做持久化。
4. 镜像尽量精简，减少体积和攻击面。
5. 使用多阶段构建，把编译环境和运行环境分离。
6. 容器之间通信优先使用服务名，不要误写成 `localhost`。
7. `depends_on` 不能代替健康检查。
8. 生产环境不要把 root 密码、密钥直接写死在镜像里。

---

## 10. 面试简答模板

如果面试官问：“你怎么理解 Docker？”

可以这样答：

Docker 是一种容器化技术，它把应用和运行依赖一起打包成镜像，再以容器方式运行，解决环境不一致问题。它底层依赖 Linux 的 namespace 和 cgroup 实现资源隔离和限制。相比虚拟机，Docker 更轻量、启动更快、资源利用率更高。实际开发里我通常会用 Dockerfile 构建应用镜像，用 Docker Compose 管理应用、MySQL、Redis 等多服务联调，并通过 volume 做数据持久化。
