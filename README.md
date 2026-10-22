# zunney 的统一 FnDepot 应用源

在 FnDepot 中添加本仓库地址，然后同步源：

https://github.com/zunney/FnDepot

JSON 直链：https://raw.githubusercontent.com/zunney/FnDepot/main/fnpack.json

| 应用 | 原作者 | 支持架构 |
| --- | --- | --- |
| Clash for fnOS | chenpingonline | x86_64、ARM64 |
| fnMusic 音源扩展 | javycoder | x86_64、ARM64 |

安装包直接引用原作者正式 Release，不重新打包。fnMusic 需要先安装官方飞牛音乐，最低 fnOS 1.2.0；默认音源服务使用 Docker。Clash 的通用 all 包不内置 Mihomo，优先使用对应架构包。

工作流每 6 小时检查原作者最新正式 Release（北京时间约 02:43、08:43、14:43、20:43），也可在 Actions 手动运行。直接读取 Releases 和对应 tag 的 manifest，不依赖旧 Fork 的索引或同步任务。GitHub 调度可能延迟，长期无活动可能停用。

校验应用名、版本、架构安装包、最低系统版本、大小及 GitHub 提供的 SHA256；缺少校验值或发现已收录安装包被替换时停止更新，保留已有源文件。保留最多 100 个已收录历史版本。

迁移：先停用原来的两个单应用源，再添加本统一源并同步，避免重复应用。停用源无需卸载应用。确认统一源正常后，可删除旧源记录。

以后新增应用只需维护本仓库，客户端无需再添加新源。各应用的许可与使用要求以原作者项目为准。
