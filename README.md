# 蓝湖原型自动分片截图 Skill

这是一个面向 Codex 的 Skill，用于把大型蓝湖／Axure 原型画布转换成适合 AI 阅读的完整证据包，解决只读取网页文字时缺少布局信息、手动滚动画布截图繁琐，以及截图与需求文字难以对应的问题。

## 能做什么

- 复用已登录的浏览器会话读取蓝湖原型。
- 在 100% 缩放下识别 Axure 画布的真实尺寸。
- 导出不含蓝湖顶部栏、侧边栏和滚动条的完整高清画布。
- 自动生成带重叠区域的高清分片，避免页面边缘和流程连线被截断。
- 同步提取原型文字和当前已加载的评审评论。
- 生成分片坐标清单，方便 AI 按正确顺序阅读并去除重复内容。
- 对完整画布和代表性分片进行可视化检查。

## 适用场景

- 根据大型蓝湖需求画布编写测试用例。
- 需要保留页面布局、标注、弹窗关系和流程连线。
- 原型过大，无法通过一两张手动截图完整覆盖。
- 网页可提取文字与画面位置对应不准确，需要图片和文字互相校验。

普通网页截图或单纯裁切本地图片时，不建议触发这个 Skill。

## 安装

将仓库克隆到 Codex 的个人 Skills 目录。Windows 默认路径示例：

```powershell
git clone https://github.com/HauntU21/lanhu-prototype-capture-skill.git "$env:USERPROFILE\.codex\skills\lanhu-prototype-capture"
```

如果设置了自定义 `CODEX_HOME`，请改为其中的 `skills/lanhu-prototype-capture` 目录。

浏览器捕获依赖 Codex 的浏览器控制能力；图片分片脚本需要 Python 3 和 Pillow。

## 使用示例

在 Codex 中发送蓝湖链接并调用 Skill：

```text
使用 $lanhu-prototype-capture，把这个蓝湖原型导出为完整高清画布、带重叠的分片、原型文字和评审评论：
https://lanhuapp.com/...
```

保持目标链接已在指定浏览器中登录并可访问。如果登录失效，Codex 会停下来请你完成登录，不会绕过访问控制或验证码。

如果已经有完整画布图片，也可以只运行分片脚本：

```powershell
python .\scripts\split_canvas.py .\canvas_full_100pct.png --output .\tiles
```

默认生成 1800 × 1200 的 PNG 分片，请求的横向重叠为 180 px、纵向重叠为 120 px。脚本会把最后一行和最后一列对齐到画布边缘，因此实际重叠可能更大。

## 输出内容

一次完整捕获通常生成：

```text
capture-output/
├── canvas_full_100pct.png
├── prototype_text.txt
├── review_comments.txt
├── capture_metadata.json
└── tiles/
    ├── manifest.json
    ├── tile_r01_c01.png
    ├── tile_r01_c02.png
    └── ...
```

- `canvas_full_100pct.png`：原生比例完整画布，用于理解全局流程。
- `tile_rNN_cNN.png`：按从上到下、从左到右排列的细节分片。
- `manifest.json`：每张分片在完整画布中的坐标和尺寸。
- `prototype_text.txt`：与截图来自同一 Axure 页面状态的文字。
- `review_comments.txt`：当前页面已经加载的评审评论。
- `capture_metadata.json`：来源、画布尺寸、缩放比例、时间和限制说明。

相邻分片包含重叠内容，AI 在汇总需求或编写测试用例时不应把重叠区域重复统计。

## 工作原理

Skill 会在同一浏览器会话中创建临时工作标签页，测量跨域 Axure iframe 的真实画布尺寸，再把画布临时展开到原生尺寸进行一次完整截图。该方法避免了滚轮落到错误容器、滚动距离不精确以及拼接漏图等问题。

如果画布超过浏览器单张截图限制，则退化为精确坐标滚动：逐个设置 iframe 的滚动位置、核对实际坐标，再截取对应区域。

任务结束后会关闭临时标签页并恢复临时视口设置，不修改用户原来的蓝湖工作标签页。

## 隐私与安全

本仓库只包含 Skill 的说明和通用脚本，不包含任何蓝湖项目链接、需求截图、原型文字或评审评论。

捕获产物默认保存在本地。除非用户明确指定上传内容和目标位置，否则 Skill 不会把原型、评论或提取文字上传到第三方。

## 仓库结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── browser-workflow.md
└── scripts/
    └── split_canvas.py
```
