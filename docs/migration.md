# Dice! → NoneBot2 迁移清单

对比基准：`Dice-Developer-Team/Dice` 上游源码（Dice! `2.7.1beta1(668)`，C++ 源码）。
移植实现：`nonebot_plugin_dice/`。

响应文案全部来自 `Dice/GlobalVar.cpp` 的 `PlainMsg` / `HelpDoc`，由脚本原样提取到
`_msgdata.py`（356 条消息、148 条帮助词条），**不是重写措辞**。

---

## 1. 触发规则

| 项目 | 原版 | 本移植 |
| --- | --- | --- |
| 前缀 | `.` `!` `。` `！` `．`（`init2()` 归一为 `.`） | 一致（`event.normalize_message`） |
| 前导空白 | 先 trim | 一致 |
| 群内 @ 骰娘 | 可省略前缀 | 一致（前导 at 段剥离后仍需前缀） |
| @ 别人 | `isOtherCalled && !isCalled` → 不响应 | 一致 |
| 群内没被点名 | 正常响应（仅受群开关约束） | 一致 |
| 未命中指令 | 不回复、不拦截 | 一致（不会吞掉其他插件的消息） |
| 命中指令 | — | **抛 `StopPropagation`，后续插件不再收到该消息** |
| `.bot off` 后 | 只有 `.bot` / `.help` 等基础指令仍响应 | 一致（`.r` 等转为不拦截） |
| 全局静默 | `DisabledGlobal` | `data/dice/config.yml: disabled_global` |

实测（`test/dice/probe4_block.py`）：

```
普通聊天           骰子回复=0  其他插件收到 ✓
.r 1d6 / 。r / ！r / ．r   骰子回复=1  其他插件未收到 ✓
.不是指令 / 。识别 图片     骰子回复=0  其他插件收到 ✓
@别人 .r            骰子回复=0  其他插件收到 ✓
.bot off 后 .r       骰子回复=0  其他插件收到 ✓
```

---

## 2. 掷骰核心

| 指令 | 状态 | 说明 / 响应 |
| --- | --- | --- |
| `.r [表达式] [原因]` | ✅ 完整 | `RD` 类逐行移植：表达式归一化、`+ - * /`、`X` 乘除、`K` 取高、`F` 命运骰、`P/B` 奖惩骰、`{}` 括号、`>20` 骰排序、`FormStringSeparate/Combined/Complete/Short` 四套格式全部一致 |
| `.rh` | ✅ | 暗骰：公屏回 `strRollHidden`，私聊发 `在<窗口>中 …`，同时私发给本桌 OB |
| `.rs` | ✅ | 只给结果（`FormShortString`） |
| `.r3#d6` | ✅ | 轮数解析、`strRollTurn`（`3#d` 才回显轮数）、多轮拼接 `", "`+`line(8)` |
| `.r 100` | ✅ | 与原版一致：纯数字不是表达式 → 当作掷骰原因，实际掷默认骰 |
| `.w` / `.ww` / `.wh` | ✅ | `DicePool` 移植：`Na` 加骰参数、目标值 8、加骰链、`to_circled` 圈号、`≥100` 骰的统计式展示 |
| 错误分支 | ✅ | `Value/Input/ZeroDice/ZeroType/DiceTooBig/TypeTooBig/AddDiceVal/DiceCnt` 八种错误码对应文案 |
| 骰点统计 | ✅ | `pc.cntRollStat` / `cntRcStat`，`.pc stat` 用 `DiceEst`（含原版用期望均值算方差的写法） |

## 3. 检定与人物卡

| 指令 | 状态 | 说明 |
| --- | --- | --- |
| `.rc` / `.ra` | ✅ | 暗骰 `h`/`_`、轮数 `N#`、难度（困难/极难/极限/简单/自动成功）、`*n` 乘、`+n` 加、`/n` 除、`卡名:属性`、`卡名的属性`、缺省技能值查卡、`SkillDefaultVal` 兜底、房规 0-7 成功等级、隐藏检定 |
| `.sc` | ✅ | `成功/失败`表达式、大失败取最大值、自动回写 SAN、`strSanityRoll` 的 `grade/rank` 分档 |
| `.st` | ✅ | 录入 / `show` / `del` / `clr`、`属性+1d6` 变化、`&表达式`、`卡名::属性`、文本属性、`>9` 位数值保护、`strStDetail` 的 5 种变更行格式 |
| `.en` | ✅ | 成长/增强检定、`+1d10`、`失败值/成功值`、回写角色卡 |
| `.pc` | ✅ | `new / build / redo / show / list / grp / nn / del / cpy / tag / clr / type / temp / tojson / stat` 全部实现，含模板预设、32 张上限、重名/冒号校验、错误码文案 |
| `.coc` / `.coc6` | ✅ | `COC7()` / `COC6()` 文本逐行一致（含 `%d/%d/%d` 三档） |
| `.coc7d` / `.coc6d` / `.cocd` | ✅ | 详细作成文本逐行一致 |
| `.dnd` | ✅ | `4D6K3`、降序、`<10` 补空格 |
| `.ti` / `.li` | ✅ | 10 条临时/总结症状 + 100 条恐惧症/躁狂症表（原样提取） |
| `.setcoc` | ✅ | `show / clr / 0-7`，8 段房规说明文本一致 |
| `.set` | ✅ | 默认骰 1-9999，写角色卡或用户配置 |

## 4. 外部数据（依赖溯洄接口）

| 指令 | 状态 | 说明 |
| --- | --- | --- |
| `.jrrp` | ✅ 实测可用 | `POST http://api.kokona.tech:5555/jrrp`，`QQ=<骰娘QQ>&v=20190114&QueryQQ=<uid>`；当日缓存；接口失败回落本地固定值（对应 `jrrp_local`） |
| `.rule set [规则]` | ✅ | 写当前桌/用户的默认规则 |
| `.rules [规则:]词条` | ✅ 实测可用 | `POST .../rules`，`Name=<URL编码>&QQ=<骰娘QQ>&v=20190114[&Type=Rules-<规则>]`；命中回正文，空回包按 `strRuleNotFound` 处理；找不到时回 `strRuleErr + 具体信息` |
| 凭据 | — | 与原版一致：仅需骰娘自身 QQ 号（`dice_maid_qq`，缺省取事件 `self_id`），无 token |

实测：`.rules 大失败`、`.rules COC7:大失败`、`.jrrp` 均返回真实数据。

## 5. 牌堆与抽牌

| 指令 | 状态 | 说明 |
| --- | --- | --- |
| `.draw [牌堆] [数量]` | ✅ | 会话实例优先 → 公共牌堆临时实例；`_`/`h` 暗抽；抽空回 `strDeckEmpty` |
| `.deck set` | ✅ | `公共牌堆` / `牌堆名=公共牌堆` / `member`（群成员）/ `range 起 止 [步长]` |
| `.deck new` | ✅ | `牌堆名=卡1|卡2…`，支持 `内容::张数::内容` 权重语法 |
| `.deck show` / `reset` / `del` / `clr` | ✅ | 剩余牌列表、重置、删除、清空，10 个实例上限 |
| `.name [类型] [数量]` | ✅ | `随机姓名_<类型>` 子牌堆优先，`1-10` 数量限制，`、` 分隔 |
| `.nnn [类型]` | ✅ | 随机称呼并写入当前窗口 |
| 牌堆文本展开 | ✅ | `{牌堆}` 嵌套、`{%牌堆}` 可放回、`[1d6]` 内嵌掷骰、`\` 转义 |
| 公共牌堆数据 | ⚠️ | 源码包未附 `PublicDeck/*.json`，改为 `data/dice/decks.yml`；内置最小示例（随机姓名/性别/职业/背景词条），可自行补齐 |

## 6. 游戏桌 / 旁观 / 日志 / 安科 / 先攻

| 指令 | 状态 | 说明 |
| --- | --- | --- |
| `.game new/open/master/set/join/call/close/over/exit/kick/state/rou` | ✅ | 桌号 `名字#序号`，`rou` 支持 `N`、`N*M`（≤100）、`hist`、`reset`、`clr` |
| `.ob join/exit/list/clr/on/off` | ✅ | 暗骰私发旁观者；`no_ob` 开关 |
| `.init list/clr/del` | ✅ | 先攻表按点数降序，`\n1.名字: 点数` |
| `.ri [加值][名字]` / `.ri N#名字` | ✅ | 自动记入先攻表、`init_exp` 记录表达式、批量生成、轮数上限校验 |
| `.ak new/add/del/get/show/clr` | ✅ | `#标题`、`+选项|选项`、`-序号`、`=` 随机抽取并结束本轮、`fork` 传递 |
| `.log new/on/off/end` | ✅ | **玩家发言与骰娘回复都会落盘**（`fwdMsg` / `logEcho`），文件名 `桌号_日志名.txt` |
| 日志文件直发 | ✅ | `.log end` 先调 `upload_group_file` / `upload_private_file` 把文件发到群/私聊 |
| 日志上传 + 润色 | ✅ 实测可用 | 匿名 PUT 到 `https://dicelogger.s3-accelerate.amazonaws.com/<base64url(文件名)>`，成功后回 `strLogUpSuccess` 并给出 `https://logpainter.kokona.tech/?s3=<key>`（即原版「润色」入口）；失败重试 3 次（原版 2 分钟×3，本版 3 秒×3），最终回 `strLogUpFailureEnd` |
| 日志落盘位置 | — | `data/dice/log/<桌号>_<日志名>.txt`（UTF-8，格式与原版一致：`昵称(QQ) 时间\n正文\n\n`） |

实测：`.log new 第一次跑团` → 聊天 → `.r` → `.log off` → `.log end`，文件内容正确，
上传后 `logpainter` 页面 HTTP 200。

## 7. 其他

| 指令 | 状态 | 说明 |
| --- | --- | --- |
| `.help [词条]` | ✅ | 裸指令回版本+引导；精确命中回词条；唯一近似词条回 `strHelpRedirect`；多近似词条回 `.help xxx` 列表；未找到回 `strHelpNotFound` |
| `.help on/off` | ✅ | 群内开关（功能开关保留） |
| `.bot` | ✅ | `试验型 Dice! by 溯洄 & Shiki Ver 2.7.1beta1(668) on\nNoneBot2(OneBot v11)\n使用.help 查看<骰娘>帮助文档` |
| `.bot on/off` | ✅ | **骰子插件总开关**（原「停用指令」群选项） |
| `.nn [称呼]` | ✅ | `del` / `clr` / 50 字节上限 / 写群或全局称呼 |
| `.me [动作]` / `.me [群号] [动作]` / `.me on/off` | ✅ | 第三人称动作、私聊指定群发送、`禁用me` 开关 |
| `.jrrp on/off` | ✅ | 群内开关（功能开关保留） |
| 消息格式化 | ✅ | `{nick} {pc} {self} {at} {at:xxx} {print:master} {case:…} {grade:…} {sample:…} {var:…} {ran:…} {len:…} {expired:…}`、`&消息键` 重定向、`\{` 转义、`ResList` 分页与分行 |
| 角色卡模板 | ✅ | COC7 模板（9 项主属性 + 100 条技能默认值 + 120 条武器表达式 + 别名替换） |
| 会话持久化 | ✅ | `data/dice/session/*.json`（桌号/规则/GM/PL/OB/轮盘/牌堆/日志/自定义表） |

---

## 8. 未复刻项与替代方案

原版这些能力依赖 WebUI / 云服务 / QQ 平台权限，按要求（群管、权限管理不复刻）改为本地 yml：

| 未复刻 | 原版作用 | 本移植替代 |
| --- | --- | --- |
| `.group` / `.groups` | 群管：禁言、踢人、名片、头衔、潜水成员、群选项 | 不实现；群选项仍由 `.bot on/off`、`.help on/off`、`.jrrp on/off`、`.me on/off`、`.draw` 的群开关写入 |
| `.admin` / `.master` / `.user` / `.authorize` / `.dismiss` | Master 认主、信任级别、拉黑、授权、退群 | 不实现；权限校验一并移除（所有群设置类指令不再校验身份） |
| `.welcome` | 入群欢迎词 | 不实现 |
| `.reply`（含 `.reply set/list/del/show`） | 自定义关键词回复（mod 驱动） | 不实现；问答类需求请用 `.ak` 或 yml 文本覆盖 |
| `.mod` / `.str` / `.helpdoc` | 模块管理、自定义消息、帮助词条编辑 | 改为 `data/dice/messages.yml`（`messages:` / `help:`）手工维护 |
| `.system` / `.cloud` | 控制台：存盘/重载/状态/更新/云黑 | 改为 `data/dice/config.yml`；进程管理交给 NoneBot |
| `.link` / `.send` | 窗口转发、向 Master 发消息 | 不实现 |
| `.chan` | QQ 频道独立开关 | 不实现（本部署不使用频道） |
| 黑名单 / 云黑 / 敏感词 / 刷屏监控 | `BlackListManager`、`DiceCensor`、`FrqMonitor` | 不实现 |
| WebUI | 浏览器管理面板 | 全部改为本地 yml（见下） |

---

## 9. 本地配置文件（替代 WebUI）

首次运行自动生成，**修改后下一条消息即热加载**，无需重启。

### `data/dice/config.yml`

```yaml
self_name: ""          # 骰娘自称，空则用 bot 昵称
master: 0              # Master QQ（仅用于 {print:master} 展示）
default_coc_rule: 0    # 默认 COC 房规 0-7
disabled_global: false # 全局静默
disabled_draw: false   # 全局禁用 .draw
disabled_deck: false   # 全局禁用 .deck
disabled_jrrp: false   # 全局禁用 .jrrp
disabled_me: false     # 全局禁用 .me
disabled_send: false   # 预留（.send 未复刻）
```

### `data/dice/messages.yml`

```yaml
messages:              # 覆盖内置消息文本，键同 PlainMsg
  strJrrp: "{nick}今天的人品值是: {res}"
help:                  # 覆盖/新增 .help 词条
  我的房规: "本群房规：……"
```

### `data/dice/decks.yml`

```yaml
decks:
  随机姓名: ["{随机姓氏}{随机名字}"]
  随机姓氏: [王, 李, 张]
  俄罗斯轮盘: ["有弹", "::5::无弹"]   # 1/6 概率有弹
```

### 数据目录

```
data/dice/
├── config.yml          # 全局开关（原 WebUI 配置页）
├── messages.yml        # 自定义文本/帮助（原 WebUI 自定义文本页）
├── decks.yml           # 公共牌堆（原 WebUI 牌堆页）
├── users.json          # 用户：信任级别、称呼、个人配置、jrrp 兜底
├── players.json        # 角色卡
├── chats.json          # 群记录：群名、群选项、房规
├── daily.json          # 当日 jrrp 缓存
├── session/*.json      # 游戏桌（含牌堆实例、轮盘、日志状态）
└── log/*.txt           # 跑团日志正文
```

---

## 10. 已知差异（有意为之）

1. **随机源**：原版 `mt19937(rdtsc)`，本移植用 Python `random`（Mersenne Twister）。分布一致，序列不可比；所有概率公式、取整方向、展示格式保持原样。
2. **权限**：无 trust/master/admin 体系，`can_host` 恒为真；因此任何群成员都能用 `.bot off`、`.setcoc`、`.game new` 等（原版要求群管理或信任）。
3. **`.rc 属性-10`**：与原版一致地**不生效**（`readNum` 对前导 `-` 返回 -3，属上游既有缺陷，为保持 1:1 未修正）。`+10` 正常。
4. **`.ww 3#10a8`（已有角色卡时）**：与原版一致地解析失败（`#` 走 `readAttrName` 分支）。
5. **昵称**：原版会实时查 QQ 昵称；本移植只用事件里的群名片/昵称与本地缓存，未知用户回落 `陌生人[QQ]`。
6. **日志重传节奏**：原版失败后 2 分钟重试，共 3 次；本移植 3 秒重试，避免长时间占用会话。
7. **`{list_extern_deck}` / `{list_reply_deck}` / `{list_dice_sister}`**：返回空（mod、自定义回复、姐妹骰未复刻）；`{list_all_deck}` 正常返回 `decks.yml` 里的牌堆名。
8. **`.help` 文案**：仍会列出 `.group` / `.dismiss` / `.welcome` 等未实现指令（帮助文档原样保留），实际发送不会响应。

---

## 11. 验证记录

移植过程中用 7 组冒烟脚本覆盖了：指令冒烟、深浅检定、触发与阻断、日志落盘与上传、
牌堆全套、多卡与预设作成。另对 `.jrrp`、`.rules`、日志上传三个外部接口做了真实请求验证
（HTTP 200）。这些脚本留在开发仓库中，不随本包发布。

