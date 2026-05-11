---
name: douyin-render-markdown
description: Use when the user provides a Douyin video link (v.douyin.com short link or douyin.com video URL) and wants to generate a structured Chinese Markdown document from the video content. Activates for requests involving Douyin video notes, video-to-markdown, or content extraction from Douyin.
argument-hint: <douyin-url> [additional-instructions]
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# Douyin Render Markdown

Convert a Douyin video into a structured Markdown document with key frames and content analysis.

## Tool Paths

- **ffmpeg**: `D:/ffmpeg/bin/ffmpeg`

## Workflow

### Phase 1: Source Acquisition (Python + requests)

Douyin's anti-bot protection makes yt-dlp unreliable. Use the mobile share page approach instead:

```python
import requests, json, re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# Follow short URL to get mobile share page
resp = session.get('<DOUYIN_URL>', timeout=15, allow_redirects=True)
html = resp.text

# Extract video URL from play_addr
match = re.search(r'"play_addr".*?"url_list":\s*\["(.*?)"', html)
video_url = match.group(1).encode().decode('unicode_escape')

# Extract cover
cover_match = re.search(r'"origin_cover".*?"url_list":\s*\["(.*?)"', html)
cover_url = cover_match.group(1).encode().decode('unicode_escape')

# Extract metadata
title_match = re.search(r'"desc":"(.*?)"', html)
author_match = re.search(r'"nickname":"(.*?)"', html)
```

### Phase 2: Two-Pass Frame Extraction

**Pass 1 — Scene change detection** to find all transition points:

```bash
ffmpeg -i video.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr -q:v 2 frames/scene_%04d.jpg 2>&1 | grep "pts_time" > frames/timestamps.txt
```

Parse `timestamps.txt` to get the timestamp of each scene change. This gives ~20-40 key frames covering all visual transitions.

**Pass 2 — Dense extraction for key segments** identified in Pass 1:

For each important segment (e.g., a tutorial step shown on screen), extract additional frames at 2-3 second intervals:

```bash
ffmpeg -ss <start> -to <end> -i video.mp4 -vf "fps=1/2" -q:v 2 frames/detail_%04d.jpg
```

### Phase 3: Frame Review and Content Extraction

Inspect EVERY frame using the Read tool. For each frame:

1. **Read all on-screen text** — titles, subtitles, button labels, prices, step numbers
2. **Identify the content type** — tutorial step, demo screen, title card, talking head, transition
3. **Group related frames** — frames showing the same step or topic belong together
4. **Note timestamps** — record when each step/topic appears

**Critical**: Do NOT skip frames. Tutorial videos hide important details in specific screens. Missing one frame means missing a step.

### Phase 4: Markdown Generation

#### For Tutorial/Strategy Videos (most common)

```markdown
# [Video Title]

**作者**: [Author]
**时长**: [Duration]
**链接**: [URL]

![封面](cover.jpg)

---

## 前置准备

[What you need before starting — accounts, tools, materials, etc.]

## 操作步骤

### 步骤 1：[Step Title]

[Detailed explanation of what to do and why]

![步骤1截图](frames/scene_0001.jpg)
*时间戳: 00:00:30*

**要点**：
- [Key point 1]
- [Key point 2]

### 步骤 2：[Step Title]

[Detailed explanation]

![步骤2截图](frames/detail_0001.jpg)
*时间戳: 00:01:15*

**注意事项**：
- ⚠️ [Important warning or common mistake]

### 步骤 3：[Step Title]

...

## 注意事项

- [Common pitfall 1]
- [Common pitfall 2]
- [Best practice]

## 总结

[Complete summary of the workflow, key takeaways, and any final tips from the video]
```

#### For Analysis/Commentary Videos

```markdown
# [Video Title]

**作者**: [Author]
**时长**: [Duration]
**链接**: [URL]

![封面](cover.jpg)

---

## 视频概述

[What this video is about]

## 内容分析

### [Section 1 Title]

[Analysis]

![帧1](frames/scene_0001.jpg)
*时间戳: 00:00:30*

### [Section 2 Title]

[Analysis]

## 关键帧集锦

| 时间 | 内容描述 |
|------|----------|
| 00:00:30 | [Description] |

## 总结

[Summary and key takeaways]
```

### Phase 5: Deliver

1. The final `.md` file
2. Cover image (`cover.jpg`)
3. All extracted frame images (`frames/` directory)

## Markdown Style Rules

1. Use Chinese unless user requests otherwise.
2. Use `##` for main sections, `###` for subsections.
3. Include images with descriptive alt text and captions.
4. Add timestamps for all frame references.
5. Use `**bold**` for key terms and `⚠️` for warnings.
6. Each step must have at least one screenshot.
7. End with a complete summary, not just a bullet list.

## Video Type Detection

Determine the video type from the first few frames and title:

- **Tutorial/How-to**: Has numbered steps, screen recordings, "how to" in title → Use tutorial template
- **Strategy/Analysis**: Has section headers, commentary, analysis text → Use analysis template
- **Entertainment**: Random scenes, no clear structure → Use simplified template (fewer sections)

Adapt the markdown structure to match the actual content flow. Do NOT force a template that doesn't fit.
