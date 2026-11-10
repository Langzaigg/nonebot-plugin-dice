# nonebot-plugin-dice

**Dice! 的 NoneBot2 轻量化实现**

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![NoneBot](https://img.shields.io/badge/nonebot-2.0%2B-red.svg)](https://nonebot.dev/)

> 本项目是 [Dice!](https://github.com/Dice-Developer-Team/Dice)（QQ 跑团掷骰机器人，C++）指令层在
> NoneBot2 / OneBot v11 下的一比一复刻。响应文案、帮助词条、技能表与疯狂表全部提取自 Dice!
> `2.7.1beta1(668)` 的源码，**不是重新撰写**；掷骰表达式解析与展示格式逐行移植。

---

## 简介

Dice! 是一款经典的 TRPG 掷骰机器人，支持 COC/DND 掷骰、技能检定、人物卡、规则速查、
今日人品、牌堆抽卡、跑团日志等。原版以 C++ 编写、依赖酷 Q / Mirai / go-cqhttp 等框架，
部署与二次开发门槛较高。

本移植版把它搬到 Python 生态：

- 只依赖 `nonebot2` + `httpx` + `pyyaml`，无需编译；
- 所有指令在**一个 matcher** 内分发，命中指令后阻断后续插件，未命中则完全放行；
- 原版需要 WebUI 才能维护的内容（牌堆、自定义文本、全局开关）改为**本地 yml 文件**，启动时读取一次，
  改完执行 `.system load` 重载（不逐条消息扫盘）。

论坛: <https://forum.tuchan.tech>

---

## 核心功能

| 分类 | 指令 | 状态 |
| --- | --- | --- |
| 掷骰 | `.r` `.rh` `.rs` `.w` `.ww` `.wh` | ✅ 完整（奖惩骰、取高骰、命运骰、多轮、暗骰） |
| 检定 | `.rc` `.ra` `.sc` `.st` `.en` | ✅ 完整（难度、房规 0-7、多卡、统计回写） |
| 人物卡 | `.pc` 全套 | ✅ 完整（多卡、模板、别名、复制、统计） |
| 人物作成 | `.coc` `.coc6` `.coc7d` `.coc6d` `.cocd` `.dnd` | ✅ 完整 |
| 规则速查 | `.rule` `.rules` | ✅ 走官方规则库接口 |
| 今日人品 | `.jrrp` | ✅ 走官方接口，含当日缓存与本地兜底 |
| 疯狂症状 | `.ti` `.li` | ✅ 完整症状表 |
| 牌堆 | `.draw` `.deck` `.name` `.nnn` | ✅ 完整（实例、权重、嵌套、内嵌掷骰） |
| 跑团日志 | `.log` | ✅ 完整（落盘、发文件、上传 + 在线润色） |
| 游戏桌 | `.game` `.ob` `.init` `.ri` `.ak` | ✅ 完整（GM/PL/OB、轮盘骰、先攻表、安价） |
| 其它 | `.help` `.bot` `.setcoc` `.set` `.nn` `.me` | ✅ 完整 |

**已精简**（原版依赖 QQ 群管理权限或 WebUI 的部分）：`.group` 群管（禁言 / 踢人 / 名片 /
头衔 / 潜水成员）、`.groups`、`.admin`、`.master`、`.user`（信任级别）、`.authorize`、
`.dismiss`、`.welcome`、`.system` 控制台、`.cloud`、`.mod`、`.reply`、`.str`、`.link`、`.send`。

这些指令**不会出现在 `.help` 里**：帮助索引在启动时剔除对应词条，`.help 群管` 会直接回
「未找到相关词条」，`.help` 主页面也不再列出 `.dismiss` / `.help群管`。

> 功能开关保留：`.bot on/off`（插件总开关）、`.help on/off`、`.jrrp on/off`、`.me on/off`。
> 控制台只保留 `.system load`（重读 yml）与 `.system save`（强制落盘）。

详细的指令级迁移对照、响应文案来源与已知差异见 [`docs/migration.md`](docs/migration.md)。

---

## 安装

从仓库安装：

```bash
pip install git+https://github.com/Langzaigg/nonebot-plugin-dice.git
```

或者把仓库克隆下来，将 `nonebot_plugin_dice/` 目录整个拷进 bot 的插件目录：

```bash
git clone https://github.com/Langzaigg/nonebot-plugin-dice.git
```

若用 `requirements.txt` 固定来源，写成：

```text
nonebot-plugin-dice @ git+https://github.com/Langzaigg/nonebot-plugin-dice.git
```

需要 Python 3.9+、NoneBot2、OneBot v11 适配器（如 `nonebot-adapter-onebot`）。

## 启用

在 bot 的 `pyproject.toml` 里加载插件：

```toml
[tool.nonebot]
plugins = ["nonebot_plugin_dice"]
```

也可以直接 `nonebot.load_plugin("nonebot_plugin_dice")`。

## 配置

插件本身只有几个可选项（`plugin_config` / `.env`）：

| 配置项 | 默认 | 说明 |
| --- | --- | --- |
| `DICE_SELF_NAME` | 空 | 骰娘自称；空则依次取 `NICKNAME`、兜底「骰娘」 |
| `DICE_MAID_QQ` | 0 | 骰娘 QQ，用于 `.jrrp` / `.rules` 接口，空则取事件 `self_id` |
| `DICE_PREFIX` | `[".", "!", "。", "！", "．"]` | 触发前缀 |
| `DICE_LISTEN_AT` | `true` | 是否响应 @ 骰娘 的消息 |

首次运行会自动生成三个本地配置文件（**替代原版 WebUI**；启动时读一次，改完执行 `.system load` 生效）：

### `data/dice/config.yml`

```yaml
self_name: ""          # 骰娘自称，空则用 bot 昵称
master: 0              # Master QQ（仅文本展示；0 则取 SUPERUSERS）
default_coc_rule: 0    # 默认 COC 房规 0-7
disabled_global: false # 全局静默（仅 .bot 可查版本，关闭需改本文件）
disabled_draw: false   # 全局禁用 .draw
disabled_deck: false   # 全局禁用 .deck
disabled_jrrp: false   # 全局禁用 .jrrp
disabled_me: false     # 全局禁用 .me
```

### `data/dice/messages.yml`

覆盖内置文案与帮助词条（键与 Dice! 的 `PlainMsg` / `HelpDoc` 一致）：

```yaml
messages:
  strJrrp: "{nick}今天的人品值是: {res}"
help:
  本群房规: "本群使用 COC7 规则书，暗骰请私聊。"
```

### `data/dice/decks.yml`

公共牌堆。支持权重 `内容::张数::内容`、嵌套 `{牌堆}`、内嵌掷骰 `[1d6]`：

```yaml
decks:
  随机姓名: ["{随机姓氏}{随机名字}"]
  随机姓氏: [王, 李, 张]
  俄罗斯轮盘: ["有弹", "::5::无弹"]
```

### `data/dice/PublicDeck/*.json`

原版 Dice! 的牌堆包格式，**可以直接把原版的 `PublicDeck` 目录拷进来**：
每个 json 是 `{"牌堆名": ["卡面", ...]}`，多个文件合并。

同名牌堆的优先级：`decks.yml` > `PublicDeck/*.json` > 代码内置。

仓库里的 [`examples/PublicDeck/塔罗.json`](examples/PublicDeck/塔罗.json) 是一份 78 张全套塔罗牌范例
（含 22 张大阿卡纳、56 张小阿卡纳、花色 / 牌阵 / 权重示例），拷贝到
`data/dice/PublicDeck/` 后 `.system load` 即可 `.draw 塔罗 3`。用法与牌面语法见
[`examples/README.md`](examples/README.md)。

### 数据目录

```
data/dice/
├── config.yml          # 全局开关
├── messages.yml        # 自定义文本 / 帮助
├── decks.yml           # 公共牌堆（本地配置）
├── PublicDeck/*.json   # 原版牌堆包（可选，文件名随意）
├── users.json          # 用户：称呼、个人配置、jrrp 兜底
├── players.json        # 角色卡
├── chats.json          # 群记录：群名、群选项、房规
├── daily.json          # 当日 jrrp 缓存
├── session/*.json      # 游戏桌（牌堆实例、轮盘、日志状态）
└── log/*.txt           # 跑团日志正文
```

### 权限

复用 NoneBot 生态已有的字段，不额外维护信任表：

| 身份 | 来源 | 能做什么 |
| --- | --- | --- |
| 主人 | NoneBot `SUPERUSERS` | 全部指令，含 `.system load/save`；不受全局 `disabled_*` 与群内禁用影响 |
| 群主 / 管理员 | OneBot 事件的 `sender.role` | 群内开关：`.bot on/off`、`.help on/off`、`.jrrp on/off`、`.me on/off`、`.deck`、`.setcoc`、`.game new`、`.ob on/off/clr` 等 |
| 普通成员 | — | 掷骰、检定、人物卡、`.jrrp`、`.draw`、`.ob join` 等日常指令 |

私聊不设限（操作范围只有自己）。原版的信任分级（trust 0-5）、邀请人临时权限、
`.authorize`/`.dismiss` 那套不做。`config.yml` 里的 `master` 仅用于文案展示，
真正的权限判定只看 `SUPERUSERS`。

---

## 用法示例

```
.r 1d100 侦查
.rh 1d100 心理学          # 暗骰，结果私聊
.rs 3d6                   # 只给结果
.rc 力量                  # 技能检定（读角色卡）
.rc 困难侦查 70           # 困难难度、成功率 70
.sc 1d10/1d100 60         # 理智检定
.st 力量:60 敏捷:55       # 录入属性
.pc new COC7:pc:卡特      # 新建 COC7 人物卡
.coc                      # 随机调查员
.jrrp                     # 今日人品
.rules 大失败             # 规则速查
.draw 随机姓名 3          # 抽牌
.log new 第一话           # 开始记录日志
.log end                  # 结束并上传（拿到在线润色链接）
```

## 关于外部接口

`.jrrp`、`.rules` 与日志上传使用的是 Dice! 官方公共接口，凭据即骰娘自身 QQ 号：

- `POST http://api.kokona.tech:5555/jrrp`
- `POST http://api.kokona.tech:5555/rules`
- 日志：匿名上传到 `dicelogger` 存储桶，再由 <https://logpainter.kokona.tech> 渲染

若接口不可达，`.jrrp` 会回落到当日固定的本地值并在日志中提示；`.rules` 会返回
「规则数据获取失败 + 具体原因」。日志上传失败会重试 3 次后提示失败原因，日志文件仍会
先直接发送到群/私聊，不会丢。

> 上方域名是 Dice! 官方服务端点，即使本项目对外文案已改用 `tuchan` 品牌也不会替换——
> 换成其他域名会直接导致 `.jrrp` / `.rules` / 日志上传失败。

---

## 与原版的差异

完整清单见 [`docs/migration.md`](docs/migration.md)，主要几处：

1. **权限用 NoneBot 的字段**：原版按 `trust` 分级（Master / 信任用户 / 普通用户），并要求群管理；
   本移植只认 `SUPERUSERS`（主人）与群主/管理员，群内开关类指令普通成员发不动，
   但不做信任分级、不记邀请人、不主动退群/入群。
2. **随机源不同**：原版 `mt19937(rdtsc)`，本版 Python `random`。概率公式、取整方向、展示格式一致，
   序列不可比。
3. **牌堆数据**：原版的 `PublicDeck/*.json` 可以直接复用（`data/dice/PublicDeck/`，
   见 [`examples/`](examples/) 里的塔罗范例）；另外内置了一小套保底牌堆（随机姓名、
   性别、调查员职业等），不够可在 `decks.yml` 里补。
4. **昵称**：只使用事件中的群名片/昵称与本地缓存，未知用户回落 `陌生人[QQ]`。
5. **原版缺陷已修正**（不再追求 1:1 复制 bug）：`.coc6` 的死代码、`.rc 力量-10` 负修正不生效、
   `.ww 3#10a8` 多轮结果重复、`.ww [骰池] 原因` 里 `{reason}` 不替换、`.help 房规` 内嵌整条
   setcoc、`.help setcoc` 参数写成 0-6 等，清单见 `docs/migration.md` 第 11 节。

---

## 开发者

本移植版：**langzaigg**（<https://github.com/Langzaigg/nonebot-plugin-dice>）

原版 Dice! 贡献者：w4123溯洄、Shiki、jh123111、緋色月下、スイカを食う

感谢：Flandre、Cirno、回転、他是王家乐。、白いとう、哞哞哞哞哞哞哞哞哞哞哞哞、丸子、黯星、
一盏大师、初音py2001、Coxxs、orzFly、[水纹霖霖CauchyDOOM](https://github.com/Dice-Developer-Team/Dice/commits?author=CauchyDOOM)
等（排名不分先后）

本移植版：响应文案与数据表由脚本从 Dice! 源码提取，掷骰内核逐行移植，指令层按
`DiceEvent::BasicOrder` / `InnerOrder` 的分发顺序重写。

## 相关链接

- Dice! 主仓库：<https://github.com/Dice-Developer-Team/Dice>
- Dice! 论坛：<https://forum.tuchan.tech>
- Dice! 手册：<https://v2docs.tuchan.tech>
- NoneBot2 文档：<https://nonebot.dev>

## License

Dice! QQ Dice Robot for TRPG

Copyright (C) 2018-2022 w4123溯洄 Shiki

本移植版（NoneBot2 实现）作为 Dice! 的衍生作品，同样以 **AGPL-3.0** 发布：

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU Affero General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this
program. If not, see <http://www.gnu.org/licenses/>.
