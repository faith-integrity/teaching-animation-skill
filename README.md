# Teaching Animation Skill · 教学动画制作

把自然语言教学需求、讲稿或示意图，逐步变成可审核、可配音、可局部修改和复现的动画视频。

这是一套给 AI 编程助手使用的 **skill 与辅助工具**，不是自带模型的一键视频生成软件。默认提供 Manim 制作方法，也允许沿用现有引擎。TTS、ASR、字体和渲染环境按需接入。

## 它能帮助完成什么

1. 检查和配置环境，或给操作者提供配置步骤。
2. 生成逐 Shot 脚本和 C1/C2…字幕，迭代至操作者确认。
3. 确定通用对象、标题、字体、字幕布局与公式的视觉规格。
4. 支持全片初稿后逐镜头精调，也支持从单个 Shot 开始逐步制作。
5. 遇到歧义及时展示理解与预览，明确审核对象和影响范围。
6. 从自然语言或草图先制作样式板、静态关键帧或短预演。
7. 接入 voice/TTS 模型、兼容的参考音色和音频转写，测量音频并同步画面。
8. 处理吞字、噪声、过长停顿、公式排版、转场残影与旧版本误合并。

经验来自 P/N 型半导体、PN 结形成、PN 结单向导电、BJT、JFET 和 NMOS 六类动画的制作记录；领域内容只是经验来源，通用流程不限定半导体教学。

## 使用

可直接让支持读取文件的助手使用 [SKILL.md](skills/teaching-animation/SKILL.md)。安装到支持该格式的技能系统时，复制整个 `skills/teaching-animation` 文件夹，保留其内部结构；例如 Codex 的个人技能目录为 `$CODEX_HOME/skills`，未设置时为 `~/.codex/skills`。若已有同名目录，先对比并保留原版。

首次输入示例：

```text
使用 $teaching-animation 制作一个解释负反馈的教学动画。
面向大二学生，约 3 分钟，中文配音。
请先给我逐 Shot 脚本，列出每个 Shot 的画面和 C1/C2 字幕。
脚本确认后先看一张样式板，再制作动画。
```

已有工程示例：

```text
使用 $teaching-animation 修改现有工程的 S03:C02。
讲到“电压增大”时才开始画曲线。字幕和现有声音不变。
先给我 S03 的预览，通过后合回全片。
```

也可以明确说“先按你的理解做完整低清预览，再逐镜头调整”。skill 会将其视为草案预演授权，保留待确认假设，不强制等待所有镜头逐一批准。

## 文件导航

| 文件 | 用途 |
|---|---|
| [SKILL.md](skills/teaching-animation/SKILL.md) | 助手入口与审核流程 |
| [references](skills/teaching-animation/references) | 环境、脚本、动画、音频、时间轴、故障与交付指南 |
| [项目模板](skills/teaching-animation/assets/project-template.md) | 工作稿、视觉规格、分镜与审核记录 |
| [时间轴示例](skills/teaching-animation/assets/timeline.example.json) | 可直接校验的无声示例 |
| [VALIDATION.md](VALIDATION.md) | 当前实际验证范围和限制 |

## 辅助工具

在本仓库根目录运行，`python` 指向希望检查或使用的环境：

```bash
python skills/teaching-animation/scripts/doctor.py
python skills/teaching-animation/scripts/check_timeline.py skills/teaching-animation/assets/timeline.example.json
python skills/teaching-animation/scripts/check_timeline.py path/to/timeline.json --check-audio
python skills/teaching-animation/scripts/transcribe.py lecture.wav output/transcript --model path/to/local-model --language zh
python -m unittest discover -s tests -v
```

环境发现、时间轴检查和测试只使用 Python 标准库。转写需要在对应环境安装 `faster-whisper` 并准备兼容本地模型。脚本不自动下载模型，已有转写文件不会被覆盖。

配音通过助手接入可用服务或本地 GPT-SoVITS，具体流程见 [audio.md](skills/teaching-animation/references/audio.md)。本包没有内置 TTS 模型、声音权重或供应商凭据，也不宣称所有模型支持参考音色。第一次接入需完成真实试听和 API 适配。

## 贡献与公开范围

欢迎贡献真实案例对应的最小修复：描述请求、使用版本、观察到的失败、修改和复验。不要上传个人录音、密钥、私有教材或未获分发许可的权重。新增脚本需提供可重复验证；新规则应说明适用边界，避免把某个课程的风格变成所有项目的硬规则。

开源包采用 [MIT License](LICENSE)。许可证覆盖本仓库原创文本和代码，不替外部模型、字体、录音或素材授予分发权。
