---
name: engineering-infographic-zh
description: Build or faithfully reproduce Chinese engineering infographic boards (架构图 / 方案图 / 流程图 / 现场实施图) as vector HTML and render them to PNG or SVG. Use when the deliverable is a dense labeled diagram of the kind produced in PowerPoint/Visio, including requests to recreate a reference image "原模原样". Do not use for ordinary statistical charts (matplotlib/plotly) or photo editing.
metadata:
  short-description: 生成或复刻中文工程信息图（矢量 HTML→PNG/SVG）
---

# 中文工程信息图

这类图不是生成式模型画出来的位图，而是**矢量排版图**：圆角卡片 + 箭头 + 真实文字 + 小图标。要「原模原样」只能按坐标重建，然后渲染成图片。扩散模型永远对不齐文字。

## 选择版式

| 版式 | 长什么样 | 模板 |
|------|----------|------|
| **总览板** | 顶部标题+标签行，中间 4 张并列卡片（接口 / 工装 / 仪器 / 软件），下方 3 张清单卡 + 公式卡，底部一条箭头步骤带 | `assets/board-overview.html` |
| **方案板** | 顶部大标题，下面 2×3 六块带浅橄榄色标题条的白色面板，每块内部自己排（结构图 / 接口区 / 流程链 / 表格） | `assets/board-scheme.html` |

版式不确定时，先问用户是要「一张全景架构图」还是「多面板方案图」。

## 工作流程

1. **定画布**。默认 968×637（总览板）或 878×585（方案板）。有参考图时，用参考图的原始像素尺寸当画布，这样所有坐标可以 1:1 直接抄。
2. **抄坐标和色值**。不要靠目测。按 [references/reverse-engineer.md](references/reverse-engineer.md) 里的方法，用颜色聚类 + 连通域把每张卡片、每个标签的包围盒量出来，再取填充色。坐标是这套图能做像的唯一依据。
3. **填模板**。把模板复制到用户的输出目录，只改开头的 `DATA` 块（总览板）或各面板内的 HTML（方案板）。**不要改 `.root` 的宽高和坐标常量**，那会让整块版面错位。
4. **渲染**：
   ```bash
   python scripts/render_html.py 图.html 图.png --scale 3
   ```
   默认 3 倍输出，插 PPT 够清晰。需要矢量就加 `--pdf`（走浏览器打印，输出真矢量 PDF）。
5. **对照校验**。有参考图就必跑：
   ```bash
   python scripts/compare_images.py 参考图.png 生成图.png --report
   ```
   它报整体色差和按行/按列的错位带，用来定位是哪一块没对齐。反复到平均色差 < 15/255 且没有明显位移带为止。

## 硬约束

- **文字必须是真文本**，不要截图或描边。中文用 `思源黑体`，本机已装；回退顺序写 `"思源黑体","Source Han Sans SC","Microsoft YaHei",sans-serif`。
- **全部绝对定位**在固定尺寸的 `.root` 里，不要用 flex/grid 自动排版做整体框架——这类图的对齐是像素级的，自动排版会漂。
- 字号按参考图反推：量出某串文字的包围盒宽度 ÷ 字数 ≈ 每字像素宽 ≈ 字号（中文近似 1em/字）。填完模板后一定要重量一遍，别信目测。
- 图片型缩略图（示波器屏幕、仪器照片）如果无法还原，用矢量示意（正弦线、柱状图、点阵）并在交付说明里讲清楚，不要假装一样。
- 底部留白、网格底纹、卡片投影都属于版式的一部分，别省。

## 资源

- `assets/board-overview.html` — 总览板模板，数据驱动，改 `DATA` 即可。
- `assets/board-scheme.html` — 方案板模板，六块面板骨架 + 通用零件（标题条、表格、流程箭头、编号圆徽、虚线注释框、状态点）。
- `scripts/render_html.py` — HTML→PNG/SVG，自动找 Edge/Chrome。
- `scripts/compare_images.py` — 与参考图逐像素比对。
- `references/design-system.md` — 两套版式的全部色值、字号、间距、零件规格。**改配色或加新零件前先读它。**
- `references/reverse-engineer.md` — 从参考图反推坐标和色值的具体做法。

## 交付

给用户三样：渲染好的 PNG（3 倍）、可编辑的 HTML 源文件、以及一句说明差异在哪（哪些是矢量示意、哪些是抗锯齿差异）。不要只说"已完成"。
