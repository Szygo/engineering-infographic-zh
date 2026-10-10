# 从参考图反推坐标与色值

目标：把参考图里每个卡片、每个标签的包围盒量到像素级，然后 1:1 写进 HTML。
目测一定偏，用下面四步量。

## 1. 取调色板和背景

```python
from PIL import Image
import numpy as np
a = np.asarray(Image.open(ref).convert('RGB'), dtype=np.int16)
cols, counts = np.unique(a.reshape(-1, 3), axis=0, return_counts=True)
for c, n in sorted(zip(cols.tolist(), counts.tolist()), key=lambda t: -t[1])[:10]:
    print('#%02X%02X%02X' % tuple(c), n)
```

出现次数第一的通常是画布底色，之后依次是卡片白、标题条底色、各种标签底色。
底色和卡片白往往只差 4~8（比如 `#FBFBF7` 与 `#FFFFFF`），所以后续做掩膜时容差要小。

## 2. 量卡片矩形

卡片填充是纯色，直接按精确色做连通域最稳：

```python
from scipy import ndimage
m = (np.abs(a - np.array([255, 255, 255])).sum(axis=2) <= 2)   # 卡片白
lab, n = ndimage.label(m)
for i, sl in enumerate(ndimage.find_objects(lab)):
    area = (lab[sl] == i + 1).sum()
    if area < 600:
        continue
    y0, y1 = sl[0].start, sl[0].stop
    x0, x1 = sl[1].start, sl[1].stop
    print('x=%d y=%d w=%d h=%d' % (x0, y0, x1 - x0, y1 - y0))
```

标题条换一个色再跑一遍（例如 `#E6F0FA`），就能拿到每张卡片的头部带位置，
卡片本体和头部要对齐——这是检查有没有量错的最快办法。

阴影和底色渐变会让连通域"胖"几像素，取整时以边框线为准。

## 3. 量边框和间距

连通域量不到的（细边框、箭头、内部子卡），扫一整行或一整列看颜色跳变：

```python
def transitions(arr, i, lo, hi, thr=24):
    line = arr[i]; out = []; prev = line[lo]
    for x in range(lo + 1, hi):
        if np.abs(line[x] - prev).sum() > thr:
            out.append(x)
        prev = line[x]
    return out

print('行扫描', transitions(a, 200, 180, 500))   # 找竖直边框
print('列扫描', transitions(a, 196, 120, 360))   # 找水平边框
```

边框通常表现为「底色 → 深一档 → 更亮」，那对跳变点就是边框线位置，取中间值。

## 4. 反推字号

中文近似 1em = 1 个字宽，所以：

```python
def text_box(img, x0, y0, x1, y1, thr=115):
    sub = img[y0:y1, x0:x1]
    m = sub.sum(axis=2) < thr * 3
    ys, xs = np.where(m)
    return (x0 + xs.min(), y0 + ys.min(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
```

量出一行文字的宽度 ÷ 字数 ≈ 字号。量出来的高度用于校验（中文实高约为字号的 0.7~0.85 倍）。

注意：**取窗口时要留够余量**，窗口上边贴太紧会把上一行的字量进来，
结果看着像字号突然变大。一次只量一行。

另外要排掉干扰：同一行里如果有图标或徽标，先用 x 范围把它排除掉再量。

## 5. 迭代到收敛

```bash
python scripts/render_html.py board.html out.png --scale 3
python scripts/compare_images.py ref.png out.png --report
```

按报告里的行/列错位带去改对应卡片，一轮改一处，不要一次改五个地方——
改完分不清是哪个动作带来的效果。总览板这种密度，通常 2~3 轮能压到平均色差 12 左右。

要做到 0 色差是不现实的：字体抗锯齿、栅格化策略、参考图本身若经过有损压缩都会留下残差。
判断标准是「放大看不出差别」，而不是「数值等于 0」。
