---
name: youtube-render-pdf
description: Use when the user provides a YouTube URL and wants to generate a structured Chinese LaTeX course note or PDF from the video. Activates for requests involving YouTube lecture notes, video-to-PDF, or course note generation from YouTube.
argument-hint: <youtube-url> [additional-instructions]
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# YouTube Render PDF

Convert a YouTube video into a complete, compilable `.tex` note and rendered PDF.

## Tool Paths

- **yt-dlp**: `C:/Users/Jiming/AppData/Roaming/Python/Python313/Scripts/yt-dlp.exe`
- **ffmpeg**: `D:/ffmpeg/bin/ffmpeg`
- **xelatex**: Not installed (skip PDF compilation, deliver .tex only until TeX Live is installed)

## Workflow

### Phase 1: Source Acquisition

1. **Get metadata** — extract title, chapters, duration, thumbnail, subtitle availability:
   ```bash
   yt-dlp --dump-json --no-download "<URL>"
   ```

2. **Download cover image** — highest resolution thumbnail available:
   ```bash
   yt-dlp --write-thumbnail --skip-download --convert-thumbnails png -o "cover.%(ext)s" "<URL>"
   ```

3. **Download subtitles** — prefer manual over auto-generated, prefer `zh-Hans`/`zh-CN`/`zh`/`ai-zh`:
   ```bash
   yt-dlp --write-subs --write-auto-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh,en" --convert-subs srt --skip-download -o "subs.%(ext)s" "<URL>"
   ```

4. **Download video** — best usable resolution for frame extraction:
   ```bash
   yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4 -o "video.%(ext)s" "<URL>"
   ```

### Phase 2: Subtitle Processing

- If CC subtitles exist, use them directly.
- If only auto-subs exist, use them with lower confidence.
- If no subtitles: extract audio then transcribe with Whisper if available, or fall back to visual-only mode.
- Clean the subtitle file: remove duplicates, merge split lines, strip non-teaching content (greetings, "一键三连", sponsorship).

### Phase 3: Key Frame Extraction

1. Use subtitle timestamps to locate key concept intervals.
2. Extract dense candidate frames with ffmpeg:
   ```bash
   ffmpeg -ss <start> -to <end> -i video.mp4 -vf "fps=1" frames/frame_%04d.png
   ```
3. Inspect candidates using the Read tool (supports images) to find frames where slides/formulas/diagrams are fully revealed and readable.
4. Crop or isolate relevant regions when the full frame is too loose.
5. Name frames semantically after visual confirmation (e.g., `transformer_architecture.png`).

### Phase 4: Content Generation

Start from `assets/notes-template.tex`. Fill metadata and replace the body block with generated notes.

**Writing rules:**
1. Write in Chinese unless user requests otherwise.
2. Organize with `\section{}` / `\subsection{}` — reconstruct teaching flow, don't mirror subtitle order.
3. Each section answers: what problem, why insufficient, core idea, how it works, takeaway.
4. Front page must include video cover image on first page.
5. Include figures whenever they improve explanation — optimize for teaching clarity, not figure count.
6. For formulas: explain in plain Chinese first, then `$$...$$`, then symbol list.
7. For code: explain role before listing, summarize after, wrap in `lstlisting` with `caption`.

**Highlight boxes:**
- `importantbox` — core concepts, definitions, key mechanisms
- `knowledgebox` — background, prerequisites, tradeoffs, analogies
- `warningbox` — common misconceptions, failure points
- Figures must stay OUTSIDE these boxes.

**Structure:**
- End each major section with `\subsection{本章小结}`
- End document with `\section{总结与延伸}` — speaker's closing discussion + your synthesis + takeaways
- No `[cite]` placeholders.

**Figure provenance:** Each figure from a video frame must have a footnote with the source time interval, e.g., `视频画面时间区间：00:12:31--00:12:46`

### Phase 5: Compilation

If xelatex is available:
```bash
xelatex -interaction=nonstopmode notes.tex
xelatex -interaction=nonstopmode notes.tex  # second pass for TOC
```

If xelatex is NOT available, deliver the `.tex` file only and inform the user.

## Long Video Strategy

For videos > 20 minutes or subtitle files > 300 entries:
- Split by chapter boundaries or coherent time windows
- Process segments in parallel with subagents when available
- Each segment returns: teaching goal, core claims, formulas/code, required figures
- Integrate into one unified narrative (not concatenated chunks)

## Delivery

Deliver:
1. The final `.tex` file
2. Cover image referenced on front page
3. All extracted figure assets
4. Compiled PDF (if xelatex available)

## Asset

- `assets/notes-template.tex`: default LaTeX template — copy and fill metadata block, then replace body content.
