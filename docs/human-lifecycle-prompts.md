# Tuxs VPN 人类一侧全周期使用提示词

本文档沉淀 Tuxingsun Network Governor / Tuxs VPN 从混沌开发、实战修复、真源重构到 GitHub 首发上线过程中的经验、弯路和可复用提示词。

目标是让人类操作者不再依赖零散指令，而是用三类标准化提示词驱动 Agent 完成完整生命周期治理：

1. 使用起始流程建档
2. 周期常态化运维
3. 故障问题检修

## 一、核心认知地图

### 1. 产品定位

- 产品全称：Tuxingsun Network Governor
- 产品简称：Tuxs VPN
- 产品定位：VPN自主分流路由治理中枢
- 长期方向：AI 时代网络墙穿越系统

Tuxs VPN 不是“开关 VPN”的工具，而是一个面向 Clash Verge Rev / mihomo / macOS system proxy 的本地路由治理中枢。

### 2. 正确目标态

浏览器、IDE、模型 API、国内网站和国外网站要同时可用，不能靠反复开关系统代理。

正确目标态是：

```text
macOS 系统代理：开启
入口：127.0.0.1:7897
mihomo mode：rule
国内 / 本地 / Trae / 字节 / mchost：DIRECT
Google / YouTube / GitHub / OpenAI / Claude 等国外站：PROXY
TUN：默认关闭
IPv6：默认关闭
watcher：运行并监控漂移
```

### 3. Clash Verge 真源锁链

必须区分“真源”和“生成物”。

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
- `clash-verge.yaml` 是生成后的 runtime config。
- mihomo `/rules` 和 `/configs` 是运行时证据。
- 只改 `clash-verge.yaml` 不是长期治理，只是临时修复。

### 4. 全局扩展覆写与脚本的边界

- 全局扩展覆写配置是配置生成阶段的 YAML merge，不是实时流量监听器。
- 全局扩展脚本是配置生成阶段的 JavaScript transform，不会在用户首次访问网站时自动 A/B 测试。
- 首访 A/B、学习、规则写入应由 Tuxs VPN 这样的外部治理进程完成，再写回 active rules/merge/script 真源层。

## 二、本轮最重要的技术弯路

这些弯路必须写入未来提示词，避免 Agent 重复犯错。

### 弯路 1：把关闭系统代理误判为稳态

错误做法：

```text
enable_system_proxy=false
macOS 系统代理关闭
```

后果：

- 国内直连看似正常。
- 浏览器访问 Google / YouTube 等国外站失败。
- 人类体验变成“修国内，国外坏；修国外，国内坏”。

正确做法：

```text
系统代理开启到 127.0.0.1:7897
mihomo mode=rule
由 Clash 规则完成国内 DIRECT / 国外 PROXY
```

### 弯路 2：用裸 curl 误判浏览器路径

错误做法：

```bash
curl https://www.google.com
```

裸 curl 不一定读取 macOS 系统代理，不能代表浏览器路径。

正确做法：

```bash
curl --proxy http://127.0.0.1:7897 https://www.google.com
```

浏览器路径验收必须模拟统一入口 `127.0.0.1:7897`。

### 弯路 3：只改 generated config，没有注入 active extensions

错误做法：

```text
直接改 clash-verge.yaml
直接改 mihomo runtime
```

后果：Clash Verge 重新生成配置后，修改可能丢失。

正确做法：

```text
active merge：固化 mode/mixed-port/tun/ipv6 等基线
active rules：固化 DIRECT/PROXY 分流规则
active script：固化防漂移 transform 和 proxy-group 优先级
runtime：仅用于验证
```

### 弯路 4：忽略 mihomo mode=global

`mode=global` 会绕过规则分流，导致国内外互相伤害。

正确验收：

```text
runtime mode 必须为 rule
mixed-port 必须为 7897
系统代理必须指向 127.0.0.1:7897
```

### 弯路 5：用 lsof 误判端口健康

`lsof` 在本机环境中曾经没显示 7897，但 TCP connect 实际可连。

正确做法：使用 TCP connect 检测端口可用性。

### 弯路 6：对人类意图的误解

人类不是要“一次性修好某个网站”，而是要：

- 建立可复用的 VPN 自主分流治理体系。
- 把经验沉淀为 Skill / 文档 / GitHub 项目。
- 用三类标准化提示词降低人类操作负担。
- 让 Agent 记住技术弯路、误解和产品反馈。
- 形成可上线、可回滚、可验证、可维护的治理中枢。

## 三、三类标准化提示词架构

以下提示词是人类一侧的标准入口。每次使用时，复制对应段落给 Agent 即可。

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

你必须先只读建档，不要直接修复、不要直接写规则、不要直接改系统代理。

目标：建立高质量起点，输出当前机器的真源锁链、运行状态、风险、漂移和下一步建议。

必须执行：

1. 识别产品上下文
   - 产品全称：Tuxingsun Network Governor
   - 产品简称：Tuxs VPN
   - 产品定位：VPN自主分流路由治理中枢
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
   - launchd watcher 是否运行

4. 建立备份与指纹
   - 备份 profiles.yaml
   - 备份 active merge/rules/script/proxies/groups
   - 备份 verge.yaml
   - 备份 clash-verge.yaml
   - 记录 sha256/mtime/size
   - 生成本地 baseline report

5. 不做以下错误动作
   - 不把关闭系统代理当成稳态
   - 不只改 clash-verge.yaml
   - 不跳过 active extension 检查
   - 不用裸 curl 代表浏览器路径
   - 不在未备份前写配置

6. 输出结果
   - 当前真源锁链
   - 当前系统代理状态
   - 当前 runtime 状态
   - 当前 watcher 状态
   - 当前风险清单
   - 是否需要进入周期常态化运维
   - 是否需要进入故障问题检修

验收口径：
只有完成建档报告、备份、真源链路、漂移清单后，才允许进入修复阶段。
```

## 起始建档输出模板

```text
Tuxs VPN 起始建档完成：

1. 真源锁链：
   profiles.yaml -> current=... -> merge=... -> script=... -> rules=...

2. 运行态：
   system proxy: on/off
   mixed-port: 7897 reachable/unreachable
   mode: rule/global/direct
   tun: on/off
   ipv6: on/off

3. watcher：
   label: ...
   running: yes/no

4. 风险：
   - ...

5. 建议下一步：
   - 周期常态化运维 / 故障检修 / 发布前收口
```

---

# B. 周期常态化运维提示词

## 适用场景

- 每日/每周巡检。
- Clash Verge 订阅刷新后。
- 电脑重启后。
- watcher 迁移或规则注入后。
- GitHub 发布前验证本地稳态。
- 用户感觉“有点不稳”，但不是单点故障。

## 标准提示词

```text
按 Tuxs VPN 周期常态化运维流程执行。

目标：维持“系统代理开启 + mihomo rule 分流 + active extension 真源固化 + watcher 防漂移”的稳态。

你必须先建档快照，再做验证；如需写配置，必须先备份。

必须执行：

1. 稳态目标确认
   - macOS 系统代理应开启
   - HTTP/HTTPS/SOCKS 指向 127.0.0.1:7897
   - 7897 TCP 可连
   - mihomo mode=rule
   - tun.enable=false
   - ipv6=false
   - Trae/国内走 DIRECT
   - Google/GitHub/OpenAI/Claude 等国外走 PROXY

2. 真源稳定性检查
   - profiles.yaml current 是否变化
   - active merge/rules/script/proxies/groups 是否变化
   - active merge 是否包含 mode: rule / mixed-port: 7897 / tun off / ipv6 off
   - active rules 是否包含国内 DIRECT 与国外 PROXY 关键规则
   - active script 是否包含 mode=rule 防漂移逻辑
   - generated clash-verge.yaml 是否与真源预期一致

3. watcher 检查
   - 新 watcher label：ai.tuxingsun.tuxs-vpn
   - 旧 watcher：com.openclaw.clash-rule-watcher 不应继续运行
   - launchd status 正常
   - watcher log 无 fatal error

4. 浏览器路径批量验收
   必须使用统一入口模拟浏览器路径：
   curl --proxy http://127.0.0.1:7897

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
   - wikipedia.org
   - reddit.com

5. 漂移修复规则
   - 如果 mode=global，必须切回 rule
   - 如果系统代理关闭，除非人类明确要求，否则应恢复为开启
   - 如果只改了 clash-verge.yaml，必须追溯写回 active extension 真源层
   - 如果 7897 不可连，先修 mihomo/Clash Verge，不要盲目写规则
   - 如果国外失败但规则存在，优先检查 proxy group 与节点健康

6. 输出运维报告
   - 当前稳态是否通过
   - 国内/Trae/国外批量结果
   - 真源是否漂移
   - watcher 是否正常
   - 本轮是否写入配置
   - 备份路径
   - 下一轮建议

禁止事项：
- 不要把系统代理关闭作为“修复”
- 不要只做国内或只做国外单边测试
- 不要用裸 curl 代替浏览器路径
- 不要在未验证 runtime /rules 前宣布完成
- 不要把 GitHub 发布前的本地 reports/backups 推到远端
```

## 周期运维输出模板

```text
Tuxs VPN 周期常态化运维结果：

1. 稳态：PASS / FAIL
2. 系统代理：on -> 127.0.0.1:7897
3. runtime：mode=rule, mixed-port=7897, tun=false, ipv6=false
4. 真源：merge/rules/script 已固化 / 存在漂移
5. watcher：ai.tuxingsun.tuxs-vpn running / not running
6. 浏览器路径验收：
   国内：x/y
   Trae：x/y
   国外：x/y
7. 本轮动作：
   - ...
8. 风险与建议：
   - ...
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

目标：先定位根因，再决定 DIRECT / PROXY / NO_WRITE。不要用猜测写规则，不要通过开关系统代理掩盖问题。

必须执行：

1. 明确症状
   - 失败对象：域名 / App / API / 浏览器页面
   - 失败路径：浏览器 / CLI / IDE / 模型 API
   - 当前系统代理是否开启
   - 当前 mihomo mode 是否 rule

2. 建立最小复现
   - 裸直连测试：curl https://DOMAIN
   - 浏览器路径测试：curl --proxy http://127.0.0.1:7897 https://DOMAIN
   - 必要时测试 HTTP code、time_total、remote_ip、stderr

3. 检查运行时证据
   - mihomo /configs
   - mihomo /rules
   - service_latest.log 中 match Match、timeout、connect failed
   - 当前 proxy group 选择与节点健康

4. 决策规则
   - direct 成功且 proxy 慢或失败：DIRECT
   - direct 失败且 proxy 成功：PROXY
   - direct/proxy 都失败：NO_WRITE，先查节点、DNS、上游服务或 TLS/HTTP 行为
   - Trae / mchost / 字节相关：优先 DIRECT，但必须有证据
   - Google / YouTube / GitHub / OpenAI / Claude：通常 PROXY，但仍以测试为准

5. 写入规则的正确位置
   - 优先写 active rules extension
   - 必要时写 active merge extension
   - 必要时写 active script extension 做防漂移
   - 不要只改 generated clash-verge.yaml

6. 验证
   - 重载 mihomo runtime
   - 检查 /rules 命中
   - 用浏览器路径重新测试
   - 同时抽测国内、Trae、国外，防止单边修复破坏另一边

7. 输出故障记录
   - 症状
   - 证据
   - 根因
   - 写入位置
   - 验证结果
   - 是否需要沉淀为产品规则或文档

禁止事项：
- 不要凭直觉把陌生域名写入 PROXY
- 不要凭直觉把国内域名写入 DIRECT
- 不要看到 HTTP 500 就判断服务商故障
- 不要跳过 proxy group / 节点健康检查
- 不要只修一个网站后不做国内/国外/Trae 回归
```

## 故障检修输出模板

```text
Tuxs VPN 故障检修结果：

1. 故障对象：...
2. direct 测试：...
3. browser/proxy 路径测试：...
4. runtime 规则证据：...
5. service log 证据：...
6. 根因判断：规则缺失 / mode 漂移 / proxy group 问题 / 节点问题 / 上游问题 / 系统代理问题
7. 决策：DIRECT / PROXY / NO_WRITE
8. 写入位置：active rules / active merge / active script / 不写入
9. 回归：
   国内：x/y
   Trae：x/y
   国外：x/y
10. 是否沉淀：是 / 否
```

---

## 四、发布与远端同步提示词

当需要把本地成果发布到 GitHub 时，使用：

```text
按 Tuxs VPN GitHub 发布收口流程执行。

要求：
1. 先完成本地真源锁链重构，隔离混沌历史文档。
2. 确认 README / CHANGELOG / ROADMAP / SECURITY / CONTRIBUTING / SESSION_HANDOFF / USAGE_LOG_TEMPLATE 已同步当前真实状态。
3. 运行 release_guard，确保 backups/reports/generated configs/token/secret 不会发布。
4. 执行 compileall、测试、build、clean install、CLI smoke。
5. git add 前必须 dry-run，确认没有本地敏感产物。
6. commit/tag/push/release 等权限动作必须获得人类授权。
7. 发布后验证远端 main、tag、Release、assets。
8. 如果人类在对话中泄露 token，提醒立即 revoke。
```

## 五、Agent 必须记住的人类意图

人类真正要的不是“临时修 VPN”，而是：

```text
用可验证、可回滚、可沉淀、可发布的方式，建立一个长期运行的 VPN 自主分流治理中枢。
```

因此 Agent 每次执行都必须：

- 先区分真源和生成物。
- 先建档再改动。
- 先证据再规则。
- 先本地验证再远端发布。
- 先保护 secrets 再生成文档。
- 把弯路和误解写回人类提示词与项目文档。

## 六、最小人类操作入口

如果只想用一句话，可以使用以下三个入口。

### 起始建档一句话

```text
按 Tuxs VPN 使用起始流程建档接管当前机器，只读检查 Clash Verge 真源锁链、mihomo runtime、系统代理、watcher、风险和下一步建议，不要直接修复。
```

### 周期运维一句话

```text
按 Tuxs VPN 周期常态化运维执行，确认系统代理开启、mihomo rule 模式、active extension 真源固化、watcher 正常，并用 127.0.0.1:7897 浏览器路径批量测试国内/Trae/国外站点。
```

### 故障检修一句话

```text
按 Tuxs VPN 故障问题检修处理：<问题描述或 URL>。先做 direct/proxy A/B 与 runtime/log 证据分析，再决定 DIRECT/PROXY/NO_WRITE，修复后必须回归国内/Trae/国外三组。
```
