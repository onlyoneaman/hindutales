from typing import List, Any
import re

def seconds_to_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02}:{s:05.3f}"[:-1]  # ASS expects HH:MM:SS.cs

def generate_ass_file(
    words: List[Any],
    output_path: str,
    words_per_group: int = 3,
    target_width: int = 720,
    target_height: int = 1280,
):
    ass_header = f"""
[Script Info]
ScriptType: v4.00+
PlayResX: {target_width}
PlayResY: {target_height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,66,&H00E6E6E6,&H64000000,&H00000000,0,0,1,5,1,2,10,10,327,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".strip()
    MIN_DURATION = 0.5  # seconds
    GAP = 0.05  # seconds

    lines = []
    valid_words = [w for w in words if w.text.strip()]

    for i in range(0, len(valid_words), words_per_group):
        group = valid_words[i:i + words_per_group]
        start_time = group[0].start
        end_time = group[-1].end

        # Ensure minimum duration
        if end_time - start_time < MIN_DURATION:
            end_time = start_time + MIN_DURATION

        # Avoid overlap with previous line
        if lines:
            prev_line = lines[-1]
            prev_end_sec = group[0].start - GAP
            prev_line = prev_line.replace(prev_line.split(",")[2], seconds_to_ass_time(prev_end_sec))
            lines[-1] = prev_line

        # Create highlighted text for each word in the group
        highlighted_text = ""
        for j, word in enumerate(group):
            word_text = word.text.strip()
            
            if j > 0:
                highlighted_text += " "
            
            # Use ASS karaoke tags with color override
            # \kf = fill effect, \1c = primary color, \2c = karaoke fill color
            # ASS colors are in BGR format
            # highlighted_text += f"{{\kf{int((word.end - word.start) * 100)}\1c&HFFFFFF&\2c&H00FFFF&}}{word_text}"
            highlighted_text += word_text

        start = seconds_to_ass_time(start_time)
        end = seconds_to_ass_time(end_time)

        ass_line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{highlighted_text}"
        lines.append(ass_line)

    lines = [ass_header] + lines

    with open(output_path, "w") as f:
        f.write("\n".join(lines))


def srt_time_to_ass_time(srt_time: str) -> str:
    """
    Converts SRT time (00:00:01,000) to ASS time (0:00:01.00) with centiseconds.
    """
    h, m, s_ms = srt_time.split(':')
    s, ms = s_ms.split(',')
    cs = str(int(ms) // 10).zfill(2)  # milliseconds to centiseconds
    return f"{int(h)}:{m}:{s}.{cs}"

def srt_to_ass(
    srt_lines: List[str], font_size: int = 48, margin_v: int = 80, box_opacity: float = 0.5,
    width: int = 720, height: int = 1280, font_name: str = "Arial"
    ) -> str:
    """
    Converts SRT lines to ASS subtitle format with an opaque (or semi-opaque) background box, padding, and improved timing accuracy.
    The background box opacity is controlled by box_opacity (0.0 = fully opaque, 1.0 = fully transparent).
    """
    # Calculate ASS color alpha (00 = opaque, FF = transparent)
    opacity_hex = int((1 - box_opacity) * 255)
    back_colour = f'&H{opacity_hex:02X}000000'  # Black with variable alpha
    # For best visibility, use fully opaque by default
    back_colour = '&H40000000'  # Semi-transparent black
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,{back_colour},-1,0,0,0,100,100,0,0,3,3,1,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    i = 0
    while i < len(srt_lines):
        # Skip empty lines
        if srt_lines[i].strip() == '':
            i += 1
            continue
        # Subtitle number
        if re.match(r'^\d+$', srt_lines[i]):
            i += 1
            if i >= len(srt_lines): break
            # Time
            times = srt_lines[i].split(' --> ')
            start = srt_time_to_ass_time(times[0].strip())
            end = srt_time_to_ass_time(times[1].strip())
            i += 1
            # Text
            text_lines = []
            while i < len(srt_lines) and srt_lines[i].strip() != '':
                text_lines.append(srt_lines[i].strip().replace('{', '').replace('}', ''))
                i += 1
            text = r'\\N'.join(text_lines)
            events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
        else:
            i += 1
    return ass_header + '\n'.join(events) + '\n'
