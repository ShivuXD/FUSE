from __future__ import annotations

import os
import shutil
import sys

from . import __version__

_UNICODE_MARK = (
    "███████╗██╗   ██╗███████╗███████╗",
    "██╔════╝██║   ██║██╔════╝██╔════╝",
    "█████╗  ██║   ██║███████╗█████╗  ",
    "██╔══╝  ██║   ██║╚════██║██╔══╝  ",
    "██║     ╚██████╔╝███████║███████╗",
    "╚═╝      ╚═════╝ ╚══════╝╚══════╝",
)
_ASCII_MARK = (
    "FFFFFF   U   U   SSSSS   EEEEEE",
    "F        U   U  S        E",
    "FFFFF    U   U   SSSS    EEEEE",
    "F        U   U      S    E",
    "F         UUU   SSSSS   EEEEEE",
)
_STOPS = ((220, 38, 38), (251, 113, 133), (167, 139, 250), (96, 165, 250), (55, 48, 255))
_RESET = "\033[0m"


def supports_color() -> bool:
    return (
        sys.stdout.isatty()
        and sys.stderr.isatty()
        and "NO_COLOR" not in os.environ
        and os.environ.get("TERM") != "dumb"
    )


def _fg(hex_color: str, enabled: bool) -> str:
    if not enabled:
        return ""
    rgb = bytes.fromhex(hex_color.lstrip("#"))
    return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"


def _paint(value: str, color: str, enabled: bool, *, bold: bool = False) -> str:
    if not enabled:
        return value
    return ("\033[1m" if bold else "") + _fg(color, True) + value + _RESET


def _gradient_line(line: str, enabled: bool, width: int) -> str:
    if not enabled:
        return line
    pieces = []
    last_rgb = None
    for x, char in enumerate(line):
        position = x / max(width - 1, 1) * (len(_STOPS) - 1)
        index = min(int(position), len(_STOPS) - 2)
        fraction = position - index
        a, b = _STOPS[index], _STOPS[index + 1]
        rgb = tuple(round(a[i] * (1 - fraction) + b[i] * fraction) for i in range(3))
        if rgb != last_rgb:
            pieces.append(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m")
            last_rgb = rgb
        pieces.append(char)
    pieces.append(_RESET)
    return "".join(pieces)


def show_banner() -> None:
    """Render a responsive, text-only welcome screen to stderr.

    Preserves the existing show_banner() API and non-TTY behavior.
    """
    if not sys.stdout.isatty() or not sys.stderr.isatty():
        return

    columns = shutil.get_terminal_size(fallback=(80, 24)).columns
    encoding = sys.stderr.encoding or "ascii"
    mark: tuple[str, ...]
    try:
        "".join(_UNICODE_MARK).encode(encoding)
        mark = _UNICODE_MARK
        unicode_ok = True
    except (LookupError, UnicodeEncodeError):
        mark = _ASCII_MARK
        unicode_ok = False

    color = supports_color()
    if columns < 40:
        lines = [
            _paint("FUSE by VIGIL", "#A78BFA", color, bold=True),
            _paint(f"v{__version__}  |  local security", "#94A3B8", color),
            _paint("Static evidence. Explicit coverage."[:columns], "#94A3B8", color),
        ]
        print("\n".join(lines) + "\n", file=sys.stderr)
        return

    # A clean, modern terminal frame. Width is bounded so the screen does not
    # become a full-width dashboard on large displays.
    inner = min(columns - 4, 68)
    frame_color = "#6065D9"
    rule = "─" if unicode_ok else "-"
    top_left, top_right, bottom_left, bottom_right, side = (
        ("╭", "╮", "╰", "╯", "│") if unicode_ok else ("+", "+", "+", "+", "|")
    )

    def frame(text: str = "", *, tint: str = "#CBD5E1") -> str:
        # Visible text only; never pass ANSI sequences into the width calculation.
        text = text[: inner - 4]
        pad = " " * max(inner - len(text) - 2, 0)
        return (
            _paint(side, frame_color, color)
            + " "
            + _paint(text, tint, color)
            + pad
            + " "
            + _paint(side, frame_color, color)
        )

    lines = [""]
    lines.append(_paint(top_left + rule * inner + top_right, frame_color, color))
    lines.append(frame("FUSE  /  VIGIL", tint="#A78BFA"))
    lines.append(frame())

    logo_width = max(map(len, mark))
    if columns >= logo_width + 8:
        for art_line in mark:
            # Render logo without truncating or wrapping inside the frame.
            spaces = " " * max(inner - len(art_line) - 2, 0)
            lines.append(
                _paint(side, frame_color, color)
                + " "
                + _gradient_line(art_line, color, logo_width)
                + spaces
                + " "
                + _paint(side, frame_color, color)
            )
    else:
        lines.append(frame("FUSE", tint="#A78BFA"))

    lines.extend(
        [
            frame(),
            frame("Firmware & Unified Security Engine", tint="#E2E8F0"),
            frame(
                f"by VIGIL   •   v{__version__}"
                if unicode_ok
                else f"by VIGIL   |   v{__version__}",
                tint="#94A3B8",
            ),
            frame("Static evidence. Explicit coverage.", tint="#94A3B8"),
            frame(),
            _paint(bottom_left + rule * inner + bottom_right, frame_color, color),
            _paint("  LOCAL ANALYSIS  /  Type /help to begin", "#60A5FA", color),
            "",
        ]
    )
    print("\n".join(lines), file=sys.stderr)
