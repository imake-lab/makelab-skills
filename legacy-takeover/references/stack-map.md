# 技术栈对照

执行规格里的示例以 Java / Spring Boot / Maven / MySQL / React 为准。规格里出现 `pom.xml`、`Controller`、`mvn test`、`SpringBootTest` 这些词的地方，按下表换成项目实际使用的技术栈。

先识别技术栈：看根目录和子目录有哪些构建文件，再看 CI 配置和 Makefile 里实际跑的是什么命令。**项目实际在用的命令，优先于下表。**

| 项 | Java / Spring | Node / TS | Go | Python | Rust | .NET | PHP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 构建文件 / 模块划分 | `pom.xml` / `build.gradle`，看 modules | `package.json`、workspaces、`pnpm-workspace.yaml` | `go.mod`，`cmd/` `internal/` | `pyproject.toml` / `setup.py` / `requirements*.txt` | `Cargo.toml` workspace | `*.sln` / `*.csproj` | `composer.json` |
| 配置 | `application*.yml/properties` | `.env*`、`config/` | `config*.yaml`、环境变量 | `settings*.py`、`.env*` | `config*.toml` | `appsettings*.json` | `.env*`、`config/` |
| HTTP 入口 | `@RestController` / `@Controller` 加 `@*Mapping` | Express / Koa / Nest 路由、`@Controller` | `http.HandleFunc`、gin / echo / chi 路由 | Django `urls.py`、FastAPI / Flask 装饰器 | axum / actix 路由 | `[ApiController]`、Minimal API | Laravel `routes/`、Symfony 路由 |
| 定时 / 消息入口 | `@Scheduled`、`@KafkaListener`、`@RabbitListener` | cron 库、消费者注册 | cron 库、consumer 循环 | Celery、APScheduler | tokio 定时任务、消费者 | HostedService | 队列 worker、Schedule |
| 数据模型来源 | 建表 SQL、Flyway / Liquibase、JPA `@Entity`、MyBatis | migrations、Prisma schema、TypeORM entity | migrations、gorm struct | Django models + migrations、SQLAlchemy、Alembic | migrations、diesel / sea-orm | EF migrations | migrations、Eloquent |
| 编译 / 启动 | `mvn clean package` / `gradle build`，然后 `java -jar` 或 `spring-boot:run` | `npm ci && npm run build`，然后 `npm start` | `go build ./...`，然后运行 | `pip install -e .`，然后用 uvicorn / gunicorn / manage.py 启动 | `cargo build`，然后 `cargo run` | `dotnet build`，然后 `dotnet run` | `composer install`，然后 `php artisan serve` |
| 全量测试 | `mvn test` / `gradle test` | `npm test`（jest / vitest） | `go test ./...` | `pytest` | `cargo test` / `cargo nextest run` | `dotnet test` | `phpunit` / `pest` |
| 单个测试 | `mvn test -pl <模块> -am -Dtest=<类>` | `npx jest <文件>` | `go test ./pkg -run <名>` | `pytest <文件>::<名>` | `cargo test <名>` | `dotnet test --filter` | `phpunit --filter` |
| 集成测试起完整上下文 | `@SpringBootTest`，可加 Testcontainers | supertest + 测试库，或 Testcontainers | `httptest` + 测试库，或 Testcontainers | Django `TestCase` / FastAPI `TestClient` | 起测试服务，加 sqlx 测试库 | `WebApplicationFactory` | Laravel Feature Test |
| Mock | Mockito（`@ExtendWith(MockitoExtension.class)`） | jest.mock / vitest vi.mock | gomock / 接口替身 | unittest.mock / pytest-mock | mockall | Moq / NSubstitute | Mockery |
| Lint / 格式 | spotless / checkstyle | eslint / prettier | `go vet`、golangci-lint、gofmt | ruff / flake8 / black | `cargo clippy`、`cargo fmt` | `dotnet format` | phpstan / pint |
| CI 运行时版本来源 | `java.version` / toolchain | `.nvmrc`、`engines` | `go.mod` 里的 go 版本 | `requires-python` | `rust-toolchain.toml` | `TargetFramework` | `composer.json` 里的 php |
| 依赖缓存 | `~/.m2` | npm / pnpm 缓存 | `~/go/pkg/mod` | pip 缓存 | `~/.cargo`、`target/` | NuGet 缓存 | composer 缓存 |

## 前端

| 项 | 怎么找 |
| --- | --- |
| 路由 / 菜单 | 路由表（react-router、vue-router）、菜单配置数组、`pages/` 目录约定 |
| API 调用层 | `services/`、`api/`、`request` 封装 |
| 类型声明 | `types/`、`*.d.ts`、接口生成代码 |
| 构建 | `npm run build`（看 package.json 的 scripts） |
| 现有组件库 | antd、element、MUI 等：改造时用现有组件，不引入新库 |

## 画图对照

| 图 | 主要素材 |
| --- | --- |
| 应用架构图 | README 的功能列表、前端路由和菜单配置、Controller 分组、包结构、表名前缀 |
| 技术架构图 | README、顶层目录、入口、docker-compose |
| 模块依赖图 | 上表的「构建文件 / 模块划分」 |
| 外部依赖（画在技术架构图底部） | 构建文件、所有环境的配置、compose、README 里的配置节 |
| ER 图 | 上表的「数据模型来源」，以数据库层为准 |
