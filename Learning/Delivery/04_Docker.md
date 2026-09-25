# Docker

Docker 的核心目标是把应用和它依赖的运行环境一起打包，让应用在不同机器上以相近方式运行。

## 核心概念

## 镜像、容器、仓库和 Dockerfile 有什么区别？

| 概念              | 作用                                               | 面试表达                         |
| ----------------- | -------------------------------------------------- | -------------------------------- |
| 镜像 Image        | 静态模板，包含代码、依赖、环境和启动配置           | 类似安装包或类                   |
| 容器 Container    | 镜像运行后的实例，有自己的进程、文件系统和网络空间 | 类似进程或对象实例               |
| 仓库 Repository   | 存放和分发镜像的地方                               | 例如 Docker Hub、私有镜像仓库    |
| Dockerfile        | 描述镜像如何从基础镜像构建                         | 镜像构建脚本                     |
| Docker Compose    | 管理多容器应用的工具                               | 用配置文件统一管理多个服务       |

镜像是只读模板，容器是运行时实例。一个镜像可以启动多个容器，删除容器不会影响镜像；但容器运行期间写入的数据，如果没有挂载卷，删除容器后通常会丢失。

## Docker 镜像分层和容器可写层是什么？

镜像采用分层存储。Dockerfile 中会产生文件系统变化的构建步骤通常会形成可复用的镜像层，多个容器可以共享相同的只读底层。

容器启动后会在镜像层之上叠加可写层。容器删除后，可写层也会消失；需要持久化的数据应使用 bind mount 或 named volume。

## Docker 为什么比虚拟机轻量？

Docker 主要依赖 Linux 内核的两个特性：

- namespace：隔离进程、网络、文件系统、用户等资源视图。
- cgroup：限制和统计 CPU、内存、块设备 I/O 等资源使用。

虚拟机需要虚拟出完整操作系统，每台虚拟机通常都有自己的内核，资源开销较大。容器共享宿主机内核，只隔离进程和运行环境，因此通常启动更快、部署密度更高。但容器与虚拟机的隔离边界不同，安全性不能简单等同。

## Dockerfile

## Dockerfile 常用指令有哪些？

| 指令       | 作用                                                         |
| ---------- | ------------------------------------------------------------ |
| FROM       | 指定基础镜像，通常是 Dockerfile 的第一条构建指令             |
| RUN        | 构建镜像时执行命令，安装依赖或生成文件                       |
| COPY       | 将构建上下文中的文件复制到镜像，通常优先使用                 |
| ADD        | COPY 的扩展，支持部分远程资源和归档处理；无特殊需求时优先 COPY |
| WORKDIR    | 设置后续指令和容器默认使用的工作目录                         |
| ENV        | 设置环境变量，容器运行时也可以读取                           |
| EXPOSE     | 声明容器监听端口，只是元数据，不会自动发布到宿主机           |
| CMD        | 提供容器启动时的默认命令或参数，可被运行时命令覆盖           |
| ENTRYPOINT | 定义容器的固定入口，运行时参数通常会追加到入口之后           |

Docker build 会按顺序执行 Dockerfile。构建缓存会复用没有变化的步骤；并不是每条指令都一定对应一个独立的文件系统层。

## CMD 和 ENTRYPOINT 有什么区别？

- CMD 提供默认命令或默认参数，运行容器时可以覆盖。
- ENTRYPOINT 定义相对固定的入口程序，运行时传入的参数通常会追加到入口之后。
- 两者可以组合：ENTRYPOINT 定义程序，CMD 提供默认参数。

示例：

~~~dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
ENTRYPOINT ["python"]
CMD ["app.py"]
~~~

~~~bash
docker build -t myimage .
docker run myimage
docker run myimage main.py
~~~

第一条运行命令执行 python app.py，第二条会使用 main.py 作为参数。

## 如何减小 Docker 镜像体积？

- 根据兼容性选择 slim、alpine 或 distroless；alpine 使用 musl libc，部分程序可能存在兼容性差异。
- 合并相关 RUN 指令，并在同一层清理 apt 缓存。
- 使用 .dockerignore 排除 node_modules、.git、日志和构建产物。
- 使用多阶段构建：在 builder 阶段编译，最终镜像只复制构建产物。
- 使用固定版本 tag 或 digest，避免 latest 随时间变化导致构建不可复现。
- 只安装运行时依赖，不把编译工具链带入最终镜像。

## Docker Compose

## Docker Compose 解决什么问题？

单个容器可以直接使用 docker run；真实项目通常有 Web、数据库、Redis、消息队列等多个服务，逐个手动启动容易出错。

Compose 用一份 docker-compose.yml 描述多个服务，统一管理容器、网络、卷和环境变量，常见于：

- 本地开发环境一键启动。
- Web + PostgreSQL + Redis 等多服务依赖管理。
- 测试环境快速拉起临时服务。

## 如何编写 docker-compose.yml？

YAML 对缩进敏感，只能使用空格，不能使用 Tab。下面是一个 Web + PostgreSQL + Redis 示例：

~~~yaml
services:
  web-app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./code:/app
    env_file:
      - .env
    depends_on:
      - postgres-db
      - redis-db
    networks:
      - app-network

  postgres-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: example
      POSTGRES_DB: app_db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

  redis-db:
    image: redis:alpine
    networks:
      - app-network

volumes:
  postgres-data:

networks:
  app-network:
~~~

## image、build、ports、volumes 等字段有什么作用？

| 字段          | 含义                                   | 注意点                                      |
| ------------- | -------------------------------------- | ------------------------------------------- |
| image         | 指定服务使用的现成镜像                 | 例如 redis:alpine、postgres:16-alpine       |
| build         | 根据 Dockerfile 构建镜像               | 常用于自己的后端或前端项目                  |
| ports         | 端口映射，格式为宿主机端口:容器端口     | 8080:80 表示访问本机 8080 转到容器 80       |
| volumes       | 挂载目录或命名卷                       | 用于代码同步和数据持久化                    |
| environment   | 设置环境变量                           | 不建议把生产密码直接写死                    |
| env_file      | 从 .env 文件读取环境变量               | 适合管理本地配置                            |
| depends_on    | 控制服务启动顺序                       | 短语法不保证依赖服务已经可用                |
| networks      | 指定服务加入哪个网络                   | 同一网络内可通过服务名互相访问              |

## Compose 网络如何通信？localhost 为什么不对？

同一个 Compose 项目的服务通常会加入同一个网络，Docker 内部 DNS 会把服务名解析到对应容器 IP。

例如后端连接 Redis 和 PostgreSQL：

~~~text
redis-db:6379
postgres-db:5432
~~~

这里不要写 localhost。容器内部的 localhost 指向当前容器自己，不是宿主机，也不是其他容器。容器之间在同一网络中通信通常不依赖 expose，expose 主要用于声明或记录容器端口；需要从宿主机或外部访问时使用 ports。

## ports 和 expose 有什么区别？

- ports：把容器端口发布并映射到宿主机，外部可以通过宿主机端口访问。
- expose：声明容器提供的端口，不发布到宿主机；同一网络中的服务通常可以直接通过服务名和端口通信。

## depends_on 能保证数据库已经启动完成吗？

短语法 depends_on 只能保证依赖容器先启动，不能保证数据库已经初始化并可以接受连接。

更可靠的做法是：

- 给数据库配置 healthcheck，并在支持的 Compose 配置中使用 service_healthy 条件。
- 应用侧增加连接重试和退避。
- 或在启动脚本中等待依赖服务真正可用。

## Compose 的 version 字段还需要写吗？

老教程常写：

~~~yaml
version: "3.8"
~~~

现在 Docker Compose v2 通常不强制要求 version，直接写 services、volumes、networks 等顶层配置即可。具体行为仍以当前 Compose 版本文档为准。

## 运行与最佳实践

## 如何进入容器或执行容器内命令？

docker exec 是在正在运行的容器中执行命令，不是必须先进入 shell。

~~~bash
docker exec -it container_name sh
docker exec -it container_name bash
docker exec -it postgres_container psql -U username -d database
~~~

- -i：保持标准输入打开。
- -t：分配伪终端，方便交互。
- sh / bash：具体使用哪个取决于镜像是否安装 bash。

## Docker 数据如何持久化？

容器本身是临时的，删除容器后容器内写入的数据可能丢失。可以使用：

- bind mount：把宿主机目录或文件挂载到容器，适合本地开发和需要直接管理宿主机文件的场景。
- named volume：由 Docker 管理存储位置，适合数据库等持久化数据。
- 外部存储：生产环境可以使用对象存储、云盘或数据库等独立存储服务。

数据库数据应放到 volume 或外部存储中，不要只写入容器可写层。

## 常见避坑和最佳实践有哪些？

- YAML 缩进只能用空格，不能用 Tab。
- 敏感信息不要直接提交到 Git，可以使用 .env、环境变量、密钥管理服务或 Docker secrets。
- 生产镜像尽量小，固定版本 tag 或 digest，避免直接使用 latest。
- 日志优先输出到标准输出和标准错误，方便 docker logs 或日志系统采集。
- 为数据库和关键依赖配置 healthcheck，并在应用侧实现重试和退避。
- 容器只运行一个主要进程，服务组合交给 Compose 或其他编排工具管理。
- 不要把容器当成虚拟机使用；需要调试时优先查看日志、配置和容器状态。

docker-compose 是旧版命令形式，现在更推荐 Docker Compose v2 的 docker compose。

## 命令速查

## 初始化、镜像和容器

~~~bash
docker pull nginx
docker images
docker build -t my-app:1.0 .
docker rmi image_id
docker run -d --name web -p 8080:80 nginx
docker ps
docker ps -a
docker logs -f container_name
docker stop container_name
docker rm container_name
docker exec -it container_name sh
~~~

## Compose

~~~bash
docker compose up -d
docker compose up --build -d
docker compose ps
docker compose logs -f
docker compose logs -f web-app
docker compose stop
docker compose down
docker compose down -v
~~~
