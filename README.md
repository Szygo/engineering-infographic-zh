# engineering-infographic-zh

一个 Codex 技能（Skill），用来**生成或复刻中文工程信息图** —— 架构图、方案图、流程图、现场实施图这类，用 PowerPoint / Visio 做出来的那种密集标注图。

输出的是一套固定尺寸的矢量 HTML，再渲染成 3 倍 PNG 或矢量 PDF。全程是真文字、真形状，可以改、可以缩放。

---

## 它解决什么问题

这类图**不能靠文生图模型画**。扩散模型输出的位图，文字必然变形、框线必然歪，尺寸也对不上。唯一的可靠做法是按坐标把形状和文字重建出来，再渲染成图片。

这个技能把这套流程固化下来了：量坐标 → 填模板 → 无头浏览器渲染 → 与参考图逐像素比对 → 按错位带修坐标。

## 预览

**总览板**（968×637）：顶部标题 + 标签行，中间四张并列卡片，下方清单卡与公式卡，底部箭头步骤带。

![总览板](assets/preview-overview.png)

**方案板**（878×585）：六块带橄榄色标题条的面板，适合放结构图、接口分区、流程链、数据表。

![方案板](assets/preview-scheme.png)

**实际产出示例**（超外差收发机链路图，用方案板做的）：

![示例](assets/example-superhet.png)

## 安装

克隆到 Codex 的 skills 目录即可。

Windows（PowerShell）：

```powershell
git clone https://github.com/Szygo/engineering-infographic-zh.git
Copy-Item -Recurse engineering-infographic-zh "$env:USERPROFILE\.codex\skills\engineering-infographic-zh"
```

macOS / Linux：

```bash
git clone https://github.com/Szygo/engineering-infographic-zh.git ~/.codex/skills/engineering-infographic-zh
```

## 用法

在 Codex 里直接说需求，例如：

> 用 $engineering-infographic-zh 做一张「XX 系统总体架构图」，内容分四块：……

或者丢一张参考图给它：

> 照这张图复刻一版，文字换成……

也可以只用脚本：

```bash
python scripts/render_html.py board.html board.png --scale 3   # HTML → PNG
python scripts/render_html.py board.html board.pdf --pdf       # HTML → 矢量 PDF
python scripts/compare_images.py ref.png board.png --report    # 与参考图比对
```

## 仓库结构

```
engineering-infographic-zh/
├── SKILL.md                    技能主文件（Codex 载入的入口）
├── agents/openai.yaml          UI 元信息
├── assets/
│   ├── board-overview.html     总览板模板（数据驱动，改 DATA 块即可）
│   ├── board-scheme.html       方案板模板（六面板骨架 + 通用零件）
│   └── preview-*.png           预览图
├── scripts/
│   ├── render_html.py          HTML → PNG / PDF，自动找 Edge / Chrome
│   └── compare_images.py       与参考图逐像素比对，报错位带
└── references/
    ├── design-system.md        两套版式的全部色值、字号、坐标常量
    └── reverse-engineer.md     从参考图反推坐标与字号的具体做法
```

## 依赖

- **渲染**：Microsoft Edge 或 Google Chrome（用无头模式截图，无需安装额外浏览器）
- **比对**：Python 3 + `Pillow`、`numpy`
- 模板本身零依赖，双击 HTML 就能在浏览器里看

## 两套版式的区别

| | 总览板 | 方案板 |
|---|---|---|
| 画布 | 968×637 | 878×585 |
| 结构 | 4 并列卡片 + 3 清单卡 + 底部步骤带 | 2×3 六块面板 |
| 适合 | 系统总体架构、现场实施全景 | 方案说明、结构 + 接口 + 流程 + 数据表 |
| 改法 | 只改文件开头的 `DATA` 对象 | 各面板内部自己排 |

## 设计原则

- 全部**绝对定位**在固定画布上，不用自动排版 —— 这类图的对齐是像素级的
- 文字必须是**真文本**，不截图、不描边
- 色值和坐标从参考图里量出来，不靠目测
- 渲染后必须和参考图比对，不是"看着差不多"就交付

## License

MIT

---

## English

A Codex skill for building or faithfully reproducing dense Chinese engineering infographics (architecture diagrams, scheme boards, flowcharts) as vector HTML, then rendering to PNG or vector PDF.

Diffusion models can't produce these — the text garbles and the boxes drift. The only reliable route is rebuilding the shapes and text at measured coordinates. This skill packages that workflow: measure → fill template → render headless → diff against the reference → fix the offending bands.

Install by cloning into `~/.codex/skills/engineering-infographic-zh`, then ask Codex for a diagram in that style.
