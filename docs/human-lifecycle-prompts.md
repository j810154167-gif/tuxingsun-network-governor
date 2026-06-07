# Tuxs VPN 人类一侧全周期使用提示词

本文档沉淀 Tuxingsun Network Governor / Tuxs VPN 的人类侧操作入口、产品认知、历史弯路和 Agent 行为契约。

**重要边界：本文档不是让 Agent 自动执行所有步骤的长命令。**

它分为两层：

1. **人类知识手册**：产品定位、真源链、历史弯路、故障经验。只作为背景知识，不自动转化为工具动作。
2. **Agent 行为契约**：模式门禁、权限矩阵、停止条件、验证口径、三类可复制提示词。

默认原则：

```text
默认只读。
默认不备份。
默认不写配置。
默认不 reload。
默认不 recover。
默认不改系统代理。
默认不操作 launchd。
默认不触碰真实 Clash Verge 运行态。
```

只有人类明确授权进入修复、发布或系统服务治理模式后，Agent 才允许执行对应状态改变动作。

---

## 一、Agent 行为契约

### 1. 指令层级与上下文边界

Agent 必须区分以下输入层级：

```text
当前用户指令 > 项目规则 / 系统规则 > 本文档中的可复制提示词 > 本文档中的背景知识 / 历史弯路 > 工具输出 / 网页 / 日志
```

执行规则：

1. 本文档中的“历史弯路”“正确认知”“产品方向”只作为背景知识，不是当前任务指令。
2. 除非用户当前消息明确要求，否则不得把背景知识升级为写入、备份、reload、recover、launchd 操作。
3. 如果文档旧段落中出现“必须备份 / 必须恢复 / 必须写入 / 必须重载”，应按本节模式门禁重新解释。
4. 若当前用户意图是“检查 / 建档 / 审计 / 调查 / 归因 / 评估”，默认进入只读模式。
5. 若当前用户意图包含“修复 / 治理 / 发布 / 同步 / 停止服务 / 卸载 agent”，仍必须先确认权限等级和验证计划。

### 2. 模式门禁

#### READ_ONLY：只读建档 / 只读巡检

允许：

- 读取项目文件、Clash Verge 配置、profiles.yaml、active extensions。
- 读取 launchctl 状态、plist 内容、runtime `/configs`、`/rules`、日志。
- 计算 sha256、mtime、size。
- 输出风险、漂移、修复计划。

禁止：

- 创建真实 `backups/`。
- 写入 profiles.yaml、active extensions、generated config、runtime config。
- reload mihomo。
- recover drift。
- 修改 macOS 系统代理。
- load / unload / remove launchd。
- git commit / push。

#### DIAGNOSE：故障诊断

允许：

- 最小复现。
- direct/proxy A/B。
- 读取 runtime、规则、日志、节点状态。
- 判定 DIRECT / PROXY / NO_WRITE。

禁止：

- 未授权写规则。
- 未授权 reload。
- 未授权备份。
- 未授权修改系统代理或 launchd。

#### REPAIR_AUTHORIZED：授权修复

进入条件：用户明确表示“修复 / 治理 / 写入 / 应用 / 恢复”，且 Agent 已说明将触碰的对象。

允许：

- 创建一次 session 级真实备份。
- 写 active extensions 真源。
- 通过正常路径触发 Clash Verge 重生成。
- reload mihomo runtime。
- 验证 runtime `/configs`、`/rules`、`/proxies`。

约束：

- 同一修复 session 只允许一次真实备份，除非人类再次授权。
- 不得直接抢写 generated config；generated config 只作为验证对象。
- 如果修复后 drift 仍存在，停止并报告，不得循环 recover。

#### SERVICE_AUTHORIZED：系统服务治理

进入条件：用户明确授权操作 launchd / watcher / agent / 系统服务。

允许：

- load / unload / remove 指定 launchd label。
- 删除指定旧 plist。
- 重装 Tuxs VPN watcher。

约束：

- 操作前必须列出目标 label、plist 路径、当前状态。
- 只能操作与 Tuxs VPN / OpenClaw / Clash rule watcher 明确相关的 label。
- 操作后必须再次确认 launchctl 和 plist 状态。

#### TEST_MODE：测试隔离

允许：

- 使用 tmp_path / 临时配置文件 / 临时 backups 目录。
- 运行 compileall、pytest、build、release_guard。

禁止：

- 测试读写真实 `backups/`。
- 测试读写真实 `reports/`。
- 测试读写真实 generated configs。
- 测试写入真实 Clash Verge 配置。
- `--no-reload` 访问 mihomo socket。

#### PUBLISH_AUTHORIZED：发布与远端同步

进入条件：用户明确授权 commit / push / tag / release。

允许：

- git add 指定文件。
- git commit。
- git push。

约束：

- commit 前必须 `git status --short`、目标 diff、近期 commit 风格检查。
- 只能 stage 本轮相关文件。
- 不得提交 secrets、真实 backups、reports、generated configs。
- push 后必须确认本地 HEAD 与 origin/main 同步。

### 3. 工具权限矩阵

| 等级 | 动作 | 默认权限 | 需要授权 | 说明 |
|---|---|---:|---:|---|
| L0 | 读文件、读状态、读日志 | 是 | 否 | 只读建档和诊断可用 |
| L1 | 写 tmp_path / 临时目录 | 是 | 否 | 测试隔离可用 |
| L2 | 写项目源码 / 文档 | 否 | 是 | 用户要求修改项目时可用 |
| L3 | 写真实 `backups/` | 否 | 是 | 仅授权修复前一次 session 备份 |
| L4 | 写 Clash Verge 真源 / active extensions | 否 | 是 | 必须说明写入位置和回滚路径 |
| L5 | 写 generated config / runtime reload | 否 | 是 | generated config 不直接编辑，只验证 |
| L6 | 系统代理 / launchd / watcher | 否 | 是 | 必须列出目标和回滚路径 |
| L7 | git commit / push / release | 否 | 是 | 必须发布前验证 |

### 4. 幂等与备份规则

1. 只读建档、周期巡检、故障诊断不得创建真实备份。
2. 只有授权修复前才创建真实备份。
3. 同一修复 session 默认只创建一次真实备份。
4. 测试备份必须写入 tmp_path，不得写入项目真实 `backups/`。
5. backup manifest 必须记录 reason、source、授权上下文。
6. 如果没有实际写入计划，不得为了“安全”预先备份。
7. 重复运行同一巡检不得产生新备份。

### 5. watcher / launchd 检查规则

任何 watcher 健康检查都不能只看 `ai.tuxingsun.tuxs-vpn`。

必须枚举：

```text
launchctl list
~/Library/LaunchAgents
/Library/LaunchAgents
/Library/LaunchDaemons
```

关键词：

```text
tuxs
vpn
clash
verge
rule
watcher
openclaw
network-governor
```

重点风险：

- `ai.openclaw.network-governor`
- `com.openclaw.clash-rule-watcher`
- 任何带 `--recover` 的 watcher。
- 任何 `KeepAlive=true` 且会写 Clash Verge 配置的 agent。
- label 还在 launchctl 里，但 plist 已经消失的残留进程。

未获 SERVICE_AUTHORIZED 前，只报告，不卸载、不删除、不 remove。

### 6. Clash Verge 交互边界

Tuxs VPN 的治理优先级体现在真源链和授权流程层，不体现在抢写 Clash Verge generated config。

```text
profiles.yaml
  -> current profile
    -> option.merge
    -> option.script
    -> option.rules
    -> option.proxies
    -> option.groups
      -> generated clash-verge.yaml / clash-verge-check.yaml
        -> mihomo runtime
```

规则：

1. `clash-verge.yaml` / `clash-verge-check.yaml` 只作为验证对象。
2. 不得在 Clash Verge 正在刷新订阅、重启代理、生成 check 文件时抢写 generated config。
3. 任何 generated config 问题必须追溯到 profiles.yaml 与 active extensions。
4. `mihomo -t successful` 只能证明当前文件语法可加载，不能证明真源已修复。
5. 如果 generated config 被回写覆盖，停止并报告真源冲突，不得继续拉锯。

### 7. 停止条件

出现以下任一情况，Agent 必须停止写入并报告：

1. 用户只要求检查，但当前流程需要写入。
2. drift 一次修复后仍未消除。
3. watcher / launchd 存在多个写配置进程。
4. Clash Verge 正在回写 generated config。
5. `--recover` watcher 仍在运行。
6. 测试触碰了真实 backups、reports 或 Clash Verge runtime。
7. 权限错误来自系统服务或特权 helper。
8. 需要 unload/remove launchd 但用户未授权。
9. 需要 commit/push 但用户未授权。
10. 证据不足以判断 DIRECT / PROXY / NO_WRITE。

### 8. 验证口径

不得把以下事件误判为完成：

- 工具命令执行成功。
- 文件被写入成功。
- generated config 暂时通过语法校验。
- watcher 报告继续增长。
- 单个网站测试通过。

完成性声明必须包含对应证据：

- 原始症状是否消失。
- 真实 backups 是否没有异常增长。
- launchd 是否没有旧冲突 agent。
- runtime `/configs`、`/rules`、`/proxies` 是否符合目标。
- 国内 / Trae / 国外是否完成抽测。
- 测试是否在 tmp_path 隔离。
- git 是否只提交预期文件。

---

## 二、核心认知地图

### 1. 产品定位

- 产品全称：Tuxingsun Network Governor
- 产品简称：Tuxs VPN
- 产品定位：VPN 自主分流路由治理中枢
- 长期方向：AI 时代网络墙穿越系统

Tuxs VPN 不是“开关 VPN”的工具，而是面向 Clash Verge Rev / mihomo / macOS system proxy 的本地路由治理中枢。

### 2. 正确目标态

```text
macOS 系统代理：开启
入口：127.0.0.1:7897
mihomo mode：rule
国内 / 本地 / Trae / 字节 / mchost：DIRECT
Google / YouTube / GitHub / OpenAI / Claude 等国外站：PROXY
TUN：默认关闭
IPv6：默认关闭
watcher：observe-only 监控漂移，默认不 recover
```

### 3. 真源锁链

```text
profiles.yaml
  -> current remote profile
    -> option.merge
    -> option.script
    -> option.rules
    -> option.proxies
    -> option.groups
      -> generated clash-verge.yaml
        -> mihomo runtime /rules
```

- `profiles.yaml` 和 active extensions 是真源。
- `clash-verge.yaml` 是生成物。
- mihomo `/rules`、`/configs`、`/proxies` 是运行时证据。
- 只改 generated config 不是长期治理。

### 4. 全局扩展覆写与脚本边界

- 全局扩展覆写配置是生成阶段 YAML merge，不是实时流量监听器。
- 全局扩展脚本是生成阶段 JavaScript transform，不会自动进行首访 A/B。
- 首访 A/B、学习、规则写回应由 Tuxs VPN 在授权修复模式下完成，再写回 active rules / merge / script 真源层。

---

## 三、历史弯路知识库

以下内容是背景知识，不是当前任务指令。Agent 只能用它们辅助判断风险，不得自动执行写入。

### 弯路 1：把关闭系统代理误判为稳态

错误：关闭 macOS 系统代理后，国内看似正常，但国外站失败。

正确：系统代理开启到 `127.0.0.1:7897`，mihomo `mode=rule`，由规则完成国内 DIRECT / 国外 PROXY。

### 弯路 2：用裸 curl 误判浏览器路径

裸 curl 不一定读取 macOS 系统代理，不能代表浏览器路径。

正确验收：

```bash
curl --proxy http://127.0.0.1:7897 https://www.google.com
```

### 弯路 3：只改 generated config，没有注入 active extensions

错误：直接改 `clash-verge.yaml` 或 mihomo runtime。

正确：修 active merge / rules / script / proxies / groups，runtime 只用于验证。

### 弯路 4：忽略 mihomo mode=global

`mode=global` 会绕过规则分流，导致国内外互相伤害。发现后在只读模式只报告 drift；授权修复后才切回 rule。

### 弯路 5：用 lsof 误判端口健康

`lsof` 可能看不到 7897，但 TCP connect 实际可连。优先使用 TCP connect 检测端口可用性。

### 弯路 6：发布测试触碰真实运行态

错误：pytest / build 阶段写真实 `clash-verge.yaml`、真实 `backups/`，或 `--no-reload` 仍访问 mihomo socket。

正确：发布测试全部使用 tmp_path；真实 Clash Verge 写入必须单独授权。

### 弯路 7：远端 push 网络失败后误判为权限或代码问题

push 超时或 HTTP2 framing 错误时，先确认本地 ahead 状态。不得改全局 git config。需要时只使用单次 `git -c ... push`。

### 弯路 8：远端同步后未重新复验

push 后必须重新确认 HEAD 与 origin/main 同步、测试通过、release guard passed。

### 弯路 9：和 Clash Verge 争夺生成物写入权

错误：看到 generated config 被覆盖，就继续抢写。

正确：停止拉锯，回到真源链，确认 active extensions 和回写进程。

### 弯路 10：`url-test/load-balance` 位置误判

`url-test` / `load-balance` 是 proxy-group 类型，不是普通 proxy 类型。若出现在 proxies 语义层，会导致 mihomo 启动失败。

### 弯路 11：`套餐详情` 不应成为关键国外站路由目标

`套餐详情` 是产品说明组，不允许作为 GitHub / OpenAI / Claude / Brave 等关键域名路由目标。授权修复时应重写到真实可路由组。

### 弯路 12：未建立继续修复前门禁

连续失败、用户指出反复犯错、或修复超过两轮仍未闭环时，必须暂停修复，进入穿透复盘。

复盘问题：

```text
1. 原始报错是什么？触发路径是什么？
2. 当前修改的是真源、生成物、runtime，还是浏览器缓存？
3. 这次修改会不会被 Clash Verge / 订阅刷新 / watcher 覆盖？
4. 是否需要真实备份？是否已获授权？
5. 是否验证 current profile 与 active option 链？
6. 是否验证 runtime /configs /rules /proxies？
7. 是否存在旧 watcher / launchd 并发？
8. 如果需要停止特权服务，是否已获授权？
```

---

## 四、三类标准化提示词

以下提示词是人类侧标准入口。复制给 Agent 时，Agent 必须受“一、Agent 行为契约”约束。

---

# A. 使用起始流程建档提示词

## 适用场景

- 第一次接管一台机器。
- Clash Verge / VPN 状态混乱。
- 换订阅、换 profile、换节点服务商后。
- 准备把本地状态纳入 Tuxs VPN 管理前。
- 新 Agent 接手，需要先建立认知地图。

## 标准提示词

```text
按 Tuxs VPN 使用起始流程建档，接管当前 Clash Verge / mihomo / macOS 系统代理网络治理状态。

模式：READ_ONLY。

目标：建立高质量起点，输出当前机器的真源锁链、运行状态、风险、漂移和下一步建议。

硬性边界：
- 不创建真实 backups。
- 不写规则。
- 不写 Clash Verge 配置。
- 不 reload mihomo。
- 不 recover drift。
- 不改系统代理。
- 不操作 launchd。

必须只读执行：

1. 识别产品上下文
   - 产品全称：Tuxingsun Network Governor
   - 产品简称：Tuxs VPN
   - 产品定位：VPN 自主分流路由治理中枢
   - 目标态：系统代理开启 + mihomo rule 模式 + 国内 DIRECT / 国外 PROXY

2. 建立 Clash Verge 真源锁链
   - 读取 profiles.yaml
   - 找到 current profile
   - 找到 active option.merge / option.script / option.rules / option.proxies / option.groups
   - 区分 active extension 真源和 generated clash-verge.yaml
   - 输出真源链路图

3. 只读检查运行态
   - macOS HTTP/HTTPS/SOCKS 系统代理
   - 127.0.0.1:7897 mixed-port 是否 TCP 可连
   - mihomo socket 是否存在
   - runtime /configs 的 mode/mixed-port/tun/ipv6
   - runtime /rules 中关键 DIRECT/PROXY 规则是否存在

4. 只读枚举 watcher / launchd
   - launchctl list
   - ~/Library/LaunchAgents
   - /Library/LaunchAgents
   - /Library/LaunchDaemons
   - 关键词：tuxs / vpn / clash / verge / rule / watcher / openclaw / network-governor
   - 标记任何 --recover、KeepAlive=true、多 watcher 并发、label 活着但 plist 缺失的风险

5. 只读审计 active extensions
   - 读取 active option.merge / option.script / option.rules / option.proxies / option.groups
   - 记录 path / sha256 / mtime / size
   - 检查是否包含 mode=rule / mixed-port=7897 / tun=false / ipv6=false
   - 检查是否包含国内 DIRECT、Trae DIRECT、国外 AI/GitHub PROXY 三类规则
   - 检查是否存在套餐详情死路、非法 proxy type、generated config 拉锯风险

6. 备份计划，不执行备份
   - 输出建议备份清单
   - 输出每个文件 sha256 / mtime / size
   - 说明：若进入授权修复阶段，应创建一次 session 备份

7. 输出结果
   - 当前真源锁链
   - 当前系统代理状态
   - 当前 runtime 状态
   - 当前 watcher / launchd 状态
   - 当前 active extensions 审计结果
   - 当前风险清单
   - 建议下一步：继续只读 / 请求授权修复 / 请求服务治理 / 发布前收口

验收口径：
只有完成建档报告、备份计划、真源链路、漂移清单后，才允许请求进入修复阶段。不得在建档阶段直接修复。
```

## 起始建档输出模板

```text
Tuxs VPN 起始建档完成：

1. 模式：READ_ONLY
2. 真源锁链：profiles.yaml -> current=... -> merge=... -> script=... -> rules=...
3. 运行态：system proxy=..., mixed-port=..., mode=..., tun=..., ipv6=...
4. watcher / launchd：
   - 当前 Tuxs label：...
   - 旧/冲突 label：...
   - recover 风险：yes/no
5. active extensions：...
6. 备份计划：仅计划，未执行真实备份
7. 风险：...
8. 下一步建议：继续只读 / 请求授权修复 / 请求服务治理
```

---

# B. 周期常态化运维提示词

## 适用场景

- 每日 / 每周巡检。
- Clash Verge 订阅刷新后。
- 电脑重启后。
- watcher 迁移或规则注入后。
- GitHub 发布前验证本地稳态。
- 用户感觉“不稳”，但不是单点故障。

## 标准提示词

```text
按 Tuxs VPN 周期常态化运维流程执行。

默认模式：READ_ONLY。

目标：验证“系统代理开启 + mihomo rule 分流 + active extension 真源固化 + watcher observe-only 防漂移”的稳态。

硬性边界：
- 巡检阶段不创建真实 backups。
- 巡检阶段不写配置。
- 巡检阶段不 reload。
- 巡检阶段不 recover。
- 巡检阶段不改系统代理。
- 巡检阶段不操作 launchd。
- 发现 drift 后只输出修复计划，等待人类授权。

必须执行：

1. 稳态目标确认
   - macOS 系统代理状态
   - HTTP/HTTPS/SOCKS 是否指向 127.0.0.1:7897
   - 7897 TCP 是否可连
   - mihomo mode 是否 rule
   - tun.enable 是否 false
   - ipv6 是否 false

2. 真源稳定性检查
   - profiles.yaml current 是否变化
   - active merge/rules/script/proxies/groups 是否变化
   - active merge 是否包含 mode=rule / mixed-port=7897 / tun=false / ipv6=false
   - active rules 是否包含国内 DIRECT 与国外 PROXY 关键规则
   - active script 是否包含防漂移逻辑
   - generated clash-verge.yaml 只读比对是否与真源预期一致；不得直接编辑

3. watcher / launchd 检查
   - 枚举所有相关 label 和 plist
   - 新 watcher label：ai.tuxingsun.tuxs-vpn
   - 旧 watcher 风险：ai.openclaw.network-governor / com.openclaw.clash-rule-watcher / 其他 openclaw 或 rule watcher
   - 检查是否存在 --recover
   - 检查是否存在 KeepAlive=true
   - 检查是否存在 label 活着但 plist 缺失
   - 未获授权不得 unload/remove/delete

4. 浏览器路径批量验收
   必须使用统一入口模拟浏览器路径：
   curl --proxy http://127.0.0.1:7897

   每个样本记录：
   - direct 裸连结果：HTTP code / time_total / remote_ip / error
   - proxy 浏览器路径结果：HTTP code / time_total / remote_ip / error
   - 判定：DIRECT / PROXY / NO_WRITE / NEED_REPAIR_PLAN
   - 是否建议写回：仅建议，不在巡检阶段写入

   国内样本：
   - baidu.com
   - qq.com
   - aliyun.com
   - eastmoney.com
   - doubao.com
   - bytedance.com

   Trae 样本：
   - trae.ai
   - trae-api-cn.mchost.guru

   国外样本：
   - google.com
   - google.com/generate_204
   - youtube.com
   - github.com
   - api.openai.com
   - chatgpt.com
   - claude.ai
   - x.com
   - wikipedia.org
   - reddit.com

5. 漂移处理规则
   - 如果 mode=global，只报告 drift 和影响；未授权不得切回 rule
   - 如果系统代理关闭，只报告 drift 和影响；未授权不得开启
   - 如果 7897 不可连，只报告 mihomo/Clash Verge 风险；未授权不得修复
   - 如果国外失败但规则存在，优先报告 proxy group 与节点健康风险
   - 如果发现 generated config 被覆盖，报告真源冲突；不得抢写 generated config

6. 固化建议规则
   - A/B 判定为 DIRECT / PROXY 的新域名，只输出写回建议
   - 去重、汇总、解释证据后，请求人类授权
   - 只有进入 REPAIR_AUTHORIZED 后，才允许写 active rules / merge / script
   - 审计日期仅在真实真源变更时更新

7. 输出运维报告
   - 当前稳态是否通过
   - 国内 / Trae / 国外批量结果
   - 真源是否漂移
   - watcher 是否 observe-only
   - 是否存在旧 agent / --recover / KeepAlive 风险
   - 本轮是否写入配置：应为否，除非另有授权
   - 本轮是否创建真实备份：应为否，除非另有授权
   - 修复计划与授权请求
```

## 周期运维输出模板

```text
Tuxs VPN 周期常态化运维结果：

1. 模式：READ_ONLY
2. 稳态：PASS / FAIL
3. 系统代理：...
4. runtime：mode=..., mixed-port=..., tun=..., ipv6=...
5. 真源：...
6. watcher / launchd：
   - observe-only：yes/no
   - 旧 agent：...
   - --recover 风险：yes/no
7. 浏览器路径验收：
   国内：x/y
   Trae：x/y
   国外：x/y
8. 本轮写入：否 / 已授权写入
9. 本轮真实备份：否 / 已授权备份
10. 修复建议：...
```

---

# C. 故障问题检修提示词

## 适用场景

- Google 不能用。
- 国内网站不能用。
- Trae / IDE 断连。
- GitHub / OpenAI / Claude 不稳定。
- 某个陌生网站首次访问失败。
- 用户感知“修国外国内坏，修国内国外坏”。

## 标准提示词

```text
按 Tuxs VPN 故障问题检修流程处理这个问题：<填写问题、网站、App 或错误现象>。

默认模式：DIAGNOSE。

目标：先定位根因，再决定 DIRECT / PROXY / NO_WRITE / NEED_REPAIR_PLAN。不要用猜测写规则，不要通过开关系统代理掩盖问题。

硬性边界：
- 诊断阶段不创建真实 backups。
- 诊断阶段不写规则。
- 诊断阶段不 reload。
- 诊断阶段不 recover。
- 诊断阶段不改系统代理。
- 诊断阶段不操作 launchd。

必须执行：

1. 明确症状
   - 失败对象：域名 / App / API / 浏览器页面
   - 失败路径：浏览器 / CLI / IDE / 模型 API
   - 当前系统代理是否开启
   - 当前 mihomo mode 是否 rule

2. 建立最小复现
   - 裸直连测试：curl https://DOMAIN
   - 浏览器路径测试：curl --proxy http://127.0.0.1:7897 https://DOMAIN
   - 必要时记录 HTTP code、time_total、remote_ip、stderr

3. 检查运行时证据
   - mihomo /configs
   - mihomo /rules
   - mihomo /proxies
   - service_latest.log 中 Match、timeout、connect failed
   - 当前 proxy group 选择与节点健康

4. 决策规则
   - direct 成功且 proxy 慢或失败：DIRECT 候选
   - direct 失败且 proxy 成功：PROXY 候选
   - direct/proxy 都失败：NO_WRITE，先查节点、DNS、上游服务或 TLS/HTTP 行为
   - Trae / mchost / 字节相关：优先 DIRECT，但必须有证据
   - Google / YouTube / GitHub / OpenAI / Claude / x.com：通常 PROXY，但仍以测试为准

5. 写入建议，不自动写入
   - 若需写入，说明正确位置：active rules / active merge / active script
   - 不要只改 generated clash-verge.yaml
   - 输出建议规则、证据、预期影响和回滚方式
   - 请求人类授权进入 REPAIR_AUTHORIZED

6. 验证计划
   - 未授权时：只输出待执行验证计划
   - 已授权写入和 reload 时：重载 mihomo runtime，检查 /rules 命中，用浏览器路径复测
   - 回归必须覆盖国内、Trae、国外三组，防止单边修复破坏另一边
   - 对 OpenAI / ChatGPT / Claude / Anthropic / Google / GitHub / x.com 等境外站，如果此前曾经走错 DIRECT、假代理、坏节点或异常 IP，提醒人类清理浏览器站点数据 / Cookie / Cache 后再复测
   - Cookie 清理提醒至少覆盖：chatgpt.com、openai.com、oaistatic.com、oaiusercontent.com、claude.ai、claude.com、anthropic.com；必要时包括 github.com、google.com
   - 如果清理 Cookie 后仍失败，再判断为节点、规则、DNS、TLS 或上游服务问题

7. 输出故障记录
   - 症状
   - direct/proxy 证据
   - runtime/log 证据
   - 根因
   - 决策：DIRECT / PROXY / NO_WRITE / NEED_REPAIR_PLAN
   - 建议写入位置
   - 是否需要授权修复
   - 是否需要沉淀为产品规则或文档
```

## 故障检修输出模板

```text
Tuxs VPN 故障检修结果：

1. 模式：DIAGNOSE
2. 故障对象：...
3. direct 测试：...
4. browser/proxy 路径测试：...
5. runtime 规则证据：...
6. service log 证据：...
7. 根因判断：规则缺失 / mode 漂移 / proxy group 问题 / 节点问题 / 上游问题 / 系统代理问题 / 浏览器缓存风控
8. 决策：DIRECT / PROXY / NO_WRITE / NEED_REPAIR_PLAN
9. 建议写入位置：active rules / active merge / active script / 不写入
10. 已执行写入：否，除非已获授权
11. Cookie/站点数据提醒：需要 / 不需要；涉及域名：...
12. 下一步：请求授权修复 / 继续只读诊断 / 结束
```

---

## 五、授权修复提示词

当人类已经确认要让 Agent 写入真源或修复漂移时，使用：

```text
授权进入 Tuxs VPN REPAIR_AUTHORIZED 模式，修复以下问题：<填写 drift / 域名 / 规则 / 真源问题>。

要求：
1. 先复述将要触碰的真实文件、runtime、服务和风险。
2. 创建一次 session 级真实备份；不得重复创建备份，除非我再次授权。
3. 只写 active extensions 真源层：rules / merge / script / proxies / groups。
4. 不得直接编辑 clash-verge.yaml / clash-verge-check.yaml。
5. 若需要 Clash Verge 重生成，只能通过正常生成路径或等待其生成后只读验证。
6. 若需要 reload mihomo，先说明 reload 命令和影响。
7. 修复后验证：
   - 真源 diff
   - generated config 只读校验
   - runtime /configs /rules /proxies
   - 国内 / Trae / 国外抽测
   - backups 数量没有异常增长
8. 如果一次修复后 drift 仍未消除，停止并报告，不得循环 recover。
```

---

## 六、服务治理提示词

当人类授权处理 watcher / launchd / 旧 agent 时，使用：

```text
授权进入 Tuxs VPN SERVICE_AUTHORIZED 模式，治理 watcher / launchd / 旧 agent。

要求：
1. 先枚举 launchctl list、~/Library/LaunchAgents、/Library/LaunchAgents、/Library/LaunchDaemons。
2. 只处理与 tuxs / vpn / clash / verge / rule / watcher / openclaw / network-governor 相关的 label。
3. 标记：
   - 当前 Tuxs VPN label
   - 旧 OpenClaw label
   - --recover 参数
   - KeepAlive=true
   - label 活着但 plist 缺失
4. 操作前列出每个目标的 label、plist、ProgramArguments、KeepAlive。
5. 经确认后 unload/remove/delete 指定旧 agent。
6. 重装 Tuxs watcher 时默认 observe-only，不带 --recover，KeepAlive=false。
7. 操作后重新验证 launchctl 和 plist 状态。
8. 观察至少一个 watcher 周期，确认 reports 可增长但 backups 不增长。
```

---

## 七、发布与远端同步提示词

当需要把本地成果发布到 GitHub 时，使用：

```text
按 Tuxs VPN GitHub 发布收口流程执行。

模式：PUBLISH_AUTHORIZED 只在我明确授权 commit / push 后生效。

要求：
1. 先确认本轮要发布的文件范围，不得混入无关文档、secrets、真实 backups、reports、generated configs。
2. 确认 README / CHANGELOG / ROADMAP / SECURITY / CONTRIBUTING / SESSION_HANDOFF / USAGE_LOG_TEMPLATE 是否需要同步；不需要时不得主动扩写。
3. release guard 必须同时满足：
   - 包内模块可测试：src/governor/release_guard.py
   - 脚本入口可运行：scripts/release_guard.py
4. 发布测试必须隔离真实运行态：
   - 单元测试使用 tmp_path / 临时配置文件
   - backup/recover 测试的备份目录必须位于 tmp_path
   - 测试不得读写项目真实 backups/reports/generated configs
   - `--no-reload` 不得访问 mihomo socket
   - 真实 Clash Verge 写入必须单独授权
5. 执行验证：
   - compileall
   - pytest
   - build（如项目需要）
   - release_guard
   - CLI smoke（只读或 tmp_path）
6. git add 前必须：
   - git status --short
   - git diff 目标文件
   - git log --oneline -5
7. 只 stage 本轮相关文件。
8. commit/tag/push/release 等动作必须获得人类明确授权。
9. 如果 push 遇到 HTTP2 framing / timeout：
   - 先确认本地 ahead 状态
   - 不改全局 git config
   - 只在授权后使用单次 `git -c ... push`
10. push 后必须重新确认：
   - git status --short
   - HEAD 与 origin/main 同步
   - pytest 通过
   - release_guard passed
11. 如果人类在对话中泄露 token，提醒立即 revoke。
```

---

## 八、人类意图

人类真正要的不是“临时修 VPN”，而是：

```text
用可验证、可回滚、可沉淀、可发布的方式，建立一个长期运行的 VPN 自主分流治理中枢。
```

Agent 每次执行都必须：

- 先识别模式，再决定工具权限。
- 先区分真源和生成物。
- 先证据再规则。
- 先只读建档，再请求授权修复。
- 先测试隔离，再发布远端。
- 先保护 secrets，再生成文档。
- 出现连续失败时停止并穿透复盘。

---

## 九、最小人类操作入口

### 起始建档一句话

```text
按 Tuxs VPN 使用起始流程建档接管当前机器，模式 READ_ONLY；只读检查 Clash Verge 真源锁链、mihomo runtime、系统代理、watcher/launchd、旧 agent、风险和下一步建议；不得备份、不得修复、不得 reload、不得 recover、不得改系统代理。
```

### 周期运维一句话

```text
按 Tuxs VPN 周期常态化运维执行，模式 READ_ONLY；确认系统代理、mihomo rule 模式、active extension 真源、watcher observe-only，并用 127.0.0.1:7897 浏览器路径批量测试国内/Trae/国外站点；发现 drift 只输出修复计划，不自动写入。
```

### 故障检修一句话

```text
按 Tuxs VPN 故障问题检修处理：<问题描述或 URL>。模式 DIAGNOSE；先做 direct/proxy A/B 与 runtime/log 证据分析，再决定 DIRECT/PROXY/NO_WRITE/NEED_REPAIR_PLAN；未授权不得写规则、备份、reload 或 recover。
```

### 授权修复一句话

```text
授权进入 Tuxs VPN REPAIR_AUTHORIZED 模式，修复：<问题描述>。先创建一次 session 备份，只写 active extensions 真源，不抢写 generated config；修复后验证 runtime、国内/Trae/国外抽测和 backups 不异常增长；失败即停止，不循环 recover。
```

### 服务治理一句话

```text
授权进入 Tuxs VPN SERVICE_AUTHORIZED 模式，治理 watcher/launchd/旧 agent；枚举所有相关 label 和 plist，清理明确冲突的旧 watcher，当前 Tuxs watcher 必须 observe-only、无 --recover、KeepAlive=false，并观察一个周期确认 backups 不增长。
```

### 发布收口一句话

```text
按 Tuxs VPN GitHub 发布收口流程执行；测试必须 tmp_path 隔离且不得触碰真实 backups/reports/Clash Verge runtime；只提交本轮相关文件；commit/push 前后都要验证 status、pytest、release_guard 和 origin/main 同步。
```
