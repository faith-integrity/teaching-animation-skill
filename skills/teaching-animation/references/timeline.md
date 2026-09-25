# 统一时间轴约定

推荐用 JSON 保存最终测时结果；已有项目可保留自己的格式并适配校验器，不为符合模板大改成熟项目。

`assets/timeline.example.json` 是无声、已测时的最小示例。所有时间以秒计；Shot 为正文局部坐标，cue 相对所在 Shot，cue 的语音起点也相对 Shot。`cover_duration` 只作用于总片偏移，不反复加入每个 Shot。Shot 显式间隙代表有意转场，必须在规格中说明。

```text
cue_global_start = cover_duration + shot.start + cue.start
voice_global_start = cover_duration + shot.start + cue.audio_start
```

每个 cue 至少包含 `id/start/end/display_text/speech_text`。有声音时添加 `audio_path/audio_start/audio_duration`，无声时 `speech_text` 为空。路径相对 manifest 所在目录。音频为已经完成片段拼接及裁边的 cue 文件；测到的真实时长才可填入 `audio_duration`。

`events` 可为句内动作记录 `id/start/end/trigger`，时间同样相对 Shot，落在所属 cue 区间。它们用于绑定语义动作，不代表脚本自动完成了语义对齐。需要更细时保存片段或词级时间。

保持 `shot.duration` 覆盖最后 cue、动作和出场，声音完全落入字幕时段。若项目刻意让字幕先退场、声音跨镜头或多个说话人重叠，需记录设计并另写适配规则；内置校验器针对顺序单旁白课程，不支持这些情况。

校验命令：

```bash
python scripts/check_timeline.py path/to/timeline.json
python scripts/check_timeline.py path/to/timeline.json --check-audio
```

脚本检查唯一 ID、正时长、有限数值、cue/镜头重叠与越界、事件边界、总时长及声音长度。`--check-audio` 还检查 PCM WAV 可读、非空、实际时长及采样率/声道一致。它不证明音色、发音、画面和教学概念正确。

帧量化尽量先换算绝对边界帧再相减，避免每段各自取整累积漂移；音频时长以样本数/采样率为准。重录后重建后续偏移、字幕和封面时间，不能只替换 WAV。
