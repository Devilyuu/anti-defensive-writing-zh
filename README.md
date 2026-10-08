# anti-defensive-writing-zh

一个给 Claude Code 用的中文写作 Skill：写作、审稿、改稿时，去掉没有依据的自我削弱、重复免责、层层对冲和 AI 套话，同时守住事实、必要的边界和作者自己的语气。

它不是 AIGC 检测的对抗工具，也不判断作者身份、不输出“AI 含量”分数。目标只有一个：让文字对读者更清楚、更可信。

## 它做什么

- **从零写**：先想清楚给谁看、读完能做什么，再从材料里找要点，不凭空补事实。
- **改稿**：分校对、润色（默认）、改写三档；先分清“内容债”和“语言债”，内容空缺改写解决不了就直说。
- **只诊断**：标出影响最大的 3–5 处，每条给位置、原句片段、问题和修改方向，不附改写稿。
- **文体取舍**：论文、审稿回复、课题申报、教学材料、小红书/公众号、项目说明、邮件、公文各有默认力度。

核心约束（优先级从高到低）：事实与承诺 > 必要边界与行动指令 > 用户本轮的明确要求 > 作者语气与文体规范 > 去模板。

典型做法：

- 没有依据的评价（“显著提升”“值得推广”）有数据就改成数据，没有就删，不编数字。
- 原文里真实的犹豫、未完成、局限，原样保留，写准、写一次、放在相关主张旁边。
- “不是 X，而是 Y”一类翻案句拿掉虚设的 X 后，Y 若还是抽象判断，整句删，不换壳。
- 原稿本来就清楚的，说明不用改，不硬改。

## 安装

Skill 就是一个目录，里面有 `SKILL.md`。把这个仓库克隆到 Claude Code 的 skills 目录，目录名保持 `anti-defensive-writing-zh`：

macOS / Linux：

```bash
git clone https://github.com/Devilyuu/anti-defensive-writing-zh ~/.claude/skills/anti-defensive-writing-zh
```

Windows（PowerShell）：

```powershell
git clone https://github.com/Devilyuu/anti-defensive-writing-zh "$env:USERPROFILE\.claude\skills\anti-defensive-writing-zh"
```

重启 Claude Code 后生效。更新时在该目录里 `git pull`。

## 怎么用

直接说需求，满足以下情形会自动触发：

- 说“反防御性写作”“去 AI 味”“太像 AI 写的”“自然一点”“别那么多可能/但是/仅供参考”“写具体点别空”。
- 让它润色、改稿、诊断一段中文。
- 让它写论文、课题申报、任务书、项目进展、小红书或公众号文案、邮件、工作总结等中文正文。

示例：

```text
这是 AI 帮我写的家长群通知，读着太像 AI 了，帮我改改，改完我直接复制发群里。
```

```text
只诊断，别改。告诉我这段哪几处最有问题、为什么、往哪个方向改。
```

只处理中文正文，不做翻译、纯摘要或代码注释。

## 目录结构

```text
SKILL.md                        主流程：先守住内容 → 选处理方式 → 六步写作与改写 → 按文体取舍 → 交付
references/
  defensive-forms.md            防御填充与必要边界的判别法
  patterns-zh.md                中文 AI 痕迹候选信号表（强/弱信号，每行写保留条件）
  genre-guidance.md             各文体的取舍
  examples-zh.md                前后对照例子
scripts/
  find_candidates.py            列出稿子里值得回查的候选位置，只报告不改写
  check_facts.py                比对原稿和改稿的数字、日期、引用等硬信息
CHANGELOG.md                    更新记录
```

两个脚本零依赖，Python 3.8+，Skill 在文件模式下会自己调用，也可以单独跑：

```bash
python scripts/find_candidates.py 稿子.md            # 全部类别
python scripts/find_candidates.py 稿子.md --counts   # 只看各类数量
python scripts/find_candidates.py 稿子.md --plain    # 要贴到微信、Word、邮件时，加查 Markdown 符号
python scripts/check_facts.py 原稿.md 改稿.md        # 比对硬信息，只报告差异
```

脚本的命中只是候选，不是改写依据。

## 效果与局限

留出集实测（当前版本，8 道题，每题“用 Skill”和“不用 Skill”各跑一次，盲评）：用 Skill 7 胜 1 负，总体分 8.12 对 6.75（10 分制），事实忠实 4.88 对 4.12，没有误伤 4.75 对 3.75。

要如实说明的几点：

- 优势主要来自**不编造、不误伤、交付干净**；单看“去掉 AI 腔”本身，不用 Skill 的模型也能做得差不多。
- 每题只跑一次，执行和评审是同一个模型，部分判分点直接来自 Skill 自己的交付规范，对 Skill 有利。
- 已知短板：直接改 README 这类技术文档时偏保守，没核实的功能说法会留在文件里只在回复中提醒；材料很少时正文容易偏薄；耗时约为不用 Skill 的三倍。

## 许可证

[MIT](LICENSE)
