# 环境准备

先检查现有工具和项目锁定版本，不默认升级。主流程与引擎无关；Manim 适合公式、图表及二维解释，已有其他引擎项目继续用原工具。

## 两种交付方式

- 用户希望自己配置：给出对应操作系统的依赖清单、安装顺序、最小验证命令和预期结果。
- 用户希望代配置：先探测已有环境，在项目独立环境中安装缺失项，遵循当前权限和下载规则；成功后保存实际解释器、版本及复现命令。系统安装需要权限时说明具体包和用途。

## 分层检查

1. 渲染：Python/所选引擎；Manim 的兼容 Python、图形依赖与字体；需要 LaTeX 公式时检查 TeX 和 dvisvgm。不要把“import 成功”当作渲染成功。
2. 媒体：FFmpeg 和 FFprobe 用于抽帧、音频转换、合并及解码检查。
3. 字体：实际机器有无所选中文字体；缺失则使用可分发字体或用户字体并重验布局。
4. TTS：独立环境、推理入口、模型/权重与参考音频路径、设备和内存；CPU/GPU 能力实测，不承诺 GPU 是必需条件。
5. ASR：按需安装 faster-whisper，指定已下载的本地兼容模型；检查设备与精度组合。

运行 `python scripts/doctor.py`（脚本路径相对本 skill），结果仅表示依赖可发现。再渲染包含中文、完整上下标公式、几何对象与短运动的 2–5 秒场景；试听一条 TTS；转写一段已知内容。每层分别记“通过/未验证/缺失”。

## 环境创建骨架

选定兼容版本后在项目根目录创建 `requirements-render.txt`。它必须写入实际选定版本，不能照抄来源项目的个人路径。

Windows PowerShell：

```powershell
python -m venv .venv-render
& .\.venv-render\Scripts\python.exe -m pip install -r requirements-render.txt
& .\.venv-render\Scripts\python.exe -m manim -ql smoke_scene.py SmokeScene
```

macOS/Linux：

```bash
python3 -m venv .venv-render
.venv-render/bin/python -m pip install -r requirements-render.txt
.venv-render/bin/python -m manim -ql smoke_scene.py SmokeScene
```

这不是所有系统依赖的一键安装命令。针对当前系统查阅 [Manim 安装文档](https://docs.manim.community/en/stable/installation.html)，按所用版本补齐系统依赖。参考项目使用过 0.19.1，但本 skill 不锁死该版本。TTS 与渲染环境分开，避免 Torch/CUDA 等依赖冲突；不要为一次吞字故障重装整套环境。

安装网络失败时保留错误原因，依权限请求联网或提供离线方案，不冒充已安装。凭据使用环境变量或宿主安全存储；环境报告公开前删除绝对个人路径和服务凭据。
