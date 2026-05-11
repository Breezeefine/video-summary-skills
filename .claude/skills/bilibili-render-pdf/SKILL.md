---
name: bilibili-render-pdf
description: Use when the user provides a Bilibili video URL (BV number or b23.tv link) and wants to generate a structured Chinese LaTeX course note or PDF from the video. Activates for requests involving Bilibili lecture notes, video-to-PDF, or course note generation from Bilibili.
argument-hint: <bilibili-url> [additional-instructions]
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# Bilibili Render PDF

Convert a Bilibili video into a complete, compilable `.tex` note and rendered PDF. Extends the YouTube workflow with Bilibili-specific adaptations.

## Tool Paths

- **yt-dlp**: `C:/Users/Jiming/AppData/Roaming/Python/Python313/Scripts/yt-dlp.exe`
- **ffmpeg**: `D:/ffmpeg/bin/ffmpeg`
- **xelatex**: Not installed (skip PDF compilation, deliver .tex only until TeX Live is installed)

## Bilibili-Specific Adaptations

| Aspect | Handling |
|--------|----------|
| **Subtitle scarcity** | CC subs -> Whisper speech-to-text -> visual-only mode |
| **Login-gated HD** | 1080P+ requires cookies; prompt user: `yt-dlp --cookies-from-browser chrome` |
| **Multi-part videos** | Detect 分P, ask user which parts to process |
| **URL formats** | Support `bilibili.com/video/BVxxxxxxx` and `b23.tv` short links |
| **Non-teaching content** | Filter out "一键三连", "关注投币", etc. |
| **Danmaku** | Do NOT use as teaching source (too noisy) |

## Workflow

### Phase 1: Source Acquisition

1. **Get metadata** — detect title, chapters, duration, subtitle availability, multi-part:
   ```bash
   yt-dlp --dump-json --no-download "<URL>"
   ```

2. **Subtitle acquisition (three-level fallback):**

   **Priority 1 — CC subtitles:**
   ```bash
   yt-dlp --write-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh" --convert-subs srt --skip-download -o "subs.%(ext)s" "<URL>"
   ```

   **Priority 2 — Whisper speech-to-text** (if no CC subs):
   ```bash
   yt-dlp -x --audio-format wav -o "audio.%(ext)s" "<URL>"
   whisper audio.wav --model medium --language zh --output_format srt --output_dir .
   ```

   **Priority 3 — Visual-only** (if audio quality too poor): dense frame sampling only.

3. **Download cover image:**
   ```bash
   yt-dlp --write-thumbnail --skip-download --convert-thumbnails png -o "cover.%(ext)s" "<URL>"
   ```

4. **Download video:**
   ```bash
   yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4 -o "video.%(ext)s" "<URL>"
   ```
   Note: 1080P+ on Bilibili typically requires login cookies.

5. **Handle multi-part (分P) videos:** List all parts, ask user which to process before downloading.

### Phase 2: Subtitle Processing

- Clean subtitle file: remove duplicates, merge split lines.
- Strip non-teaching content: greetings, channel logistics, sponsorship, "一键三连", "关注投币".
- Keep substantive closing discussion (synthesis, limitations, future work).

### Phase 3: Key Frame Extraction

1. Use subtitle timestamps (CC or Whisper-generated) as primary locator for key concepts.
2. Extract dense candidate frames:
   ```bash
   ffmpeg -ss <start> -to <end> -i video.mp4 -vf "fps=1" frames/frame_%04d.png
   ```
3. Inspect candidates with Read tool (supports images) — verify frames show fully revealed, readable content.
4. For progressive PPT reveals, find the final fully populated state.
5. Crop when the full frame is too loose. Name semantically after visual confirmation.

### Phase 4: Content Generation

Start from `assets/notes-template.tex`. Fill metadata and replace body block.

**Writing rules (same as YouTube version):**
1. Write in Chinese unless user requests otherwise.
2. Organize with `\section{}` / `\subsection{}` — reconstruct teaching flow.
3. Front page: video cover image.
4. Figures for teaching clarity — optimize for explanation, not minimal count.
5. Formulas: plain Chinese explanation first, then `$$...$$`, then symbol list.
6. Code: explain role before, summarize after, `lstlisting` with `caption`.
7. Boxes: `importantbox` (core), `knowledgebox` (background), `warningbox` (misconceptions).
8. End sections with `\subsection{本章小结}`.
9. Final `\section{总结与延伸}` with speaker's closing + your synthesis.
10. Figure footnotes with source time intervals.

### Phase 5: Compilation

If xelatex is available, compile twice (second pass for TOC). Otherwise deliver `.tex` only.

## Long Video Strategy

For videos > 20 minutes or subtitle entries > 300:
- Split by chapter boundaries or 分P boundaries
- Process segments with subagents when available
- Integrate into one unified narrative

## Delivery

1. Final `.tex` file
2. Cover image
3. All figure assets
4. Compiled PDF (if xelatex available)
5. Whisper-generated SRT if speech-to-text was used

## Asset

- `assets/notes-template.tex`: default LaTeX template — copy and fill.
