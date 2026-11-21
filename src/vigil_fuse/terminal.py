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
    """Check whether the terminal supports ANSI colors."""
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
    pieces: list[str] = []
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


def _unicode_available() -> bool:
    encoding = sys.stderr.encoding or "ascii"
    try:
        "".join(_UNICODE_MARK).encode(encoding)
        return True
    except (LookupError, UnicodeEncodeError):
        return False


def _rule(length: int, color: str, *, enabled: bool, unicode_ok: bool) -> str:
    character = "─" if unicode_ok else "-"
    return _paint(character * max(length, 1), color, enabled)


def show_banner() -> None:
    """Render the FUSE identity without changing the terminal background."""
    if not sys.stdout.isatty() or not sys.stderr.isatty():
        return

    columns = shutil.get_terminal_size(fallback=(80, 24)).columns
    unicode_ok = _unicode_available()
    mark = _UNICODE_MARK if unicode_ok else _ASCII_MARK
    color = supports_color()

    if columns < 40:
        lines = [
            _paint("FUSE", "#FB7185", color, bold=True),
            _paint("by VIGIL", "#60A5FA", color, bold=True),
            _paint(f"v{__version__}  |  local security", "#94A3B8", color),
            _paint("Static evidence. Explicit coverage.", "#94A3B8", color),
        ]
        print("\n".join(lines) + "\n", file=sys.stderr)
        return

    # Match the original compact prototype banner, not a full-width dashboard.
    inner = min(columns - 4, 44)
    frame_color = "#3730FF"
    rule = "─" if unicode_ok else "-"
    top_left, top_right, bottom_left, bottom_right, side = (
        ("╭", "╮", "╰", "╯", "│") if unicode_ok else ("+", "+", "+", "+", "|")
    )

    def frame(text: str = "", *, tint: str = "#CBD5E1", bold: bool = False) -> str:
        text = text[: max(inner - 2, 0)]
        pad = " " * max(inner - len(text) - 2, 0)
        return (
            _paint(side, frame_color, color)
            + " " + _paint(text, tint, color, bold=bold) + pad + " "
            + _paint(side, frame_color, color)
        )

    lines = ["", _paint(top_left + rule * inner + top_right, frame_color, color), frame()]
    logo_width = max(map(len, mark))
    if inner >= logo_width + 2:
        for art_line in mark:
            # Center the full ASCII mark inside the blue frame.
            padding = max(inner - logo_width, 0)
            left = padding // 2
            right = padding - left
            lines.append(
                _paint(side, frame_color, color)
                + " " * left
                + _gradient_line(art_line, color, logo_width)
                + " " * right
                + _paint(side, frame_color, color)
            )
    else:
        lines.append(frame("FUSE", tint="#A78BFA", bold=True))

    lines.extend([
        frame(),
        frame("by VIGIL", tint="#60A5FA", bold=True),
        frame("Firmware & Unified Security Engine", tint="#E2E8F0", bold=True),
        frame(f"v{__version__}  |  Local-first firmware security", tint="#94A3B8"),
        frame(),
        _paint(bottom_left + rule * inner + bottom_right, frame_color, color),
        _paint("  Type /help for commands.", "#94A3B8", color),
        "",
    ])
    print("\n".join(lines), file=sys.stderr)


def show_prompt_top() -> None:
    """Draw the red upper rule (used by the plain-input fallback)."""
    width = max(10, shutil.get_terminal_size(fallback=(80, 24)).columns - 2)
    print(
        _rule(width, "#DC2626", enabled=supports_color(), unicode_ok=_unicode_available()),
        file=sys.stderr,
    )


def show_prompt_bottom() -> None:
    """Draw the blue lower rule (used by the plain-input fallback)."""
    width = max(10, shutil.get_terminal_size(fallback=(80, 24)).columns - 2)
    print(
        _rule(width, "#60A5FA", enabled=supports_color(), unicode_ok=_unicode_available()),
        file=sys.stderr,
    )


_PROMPT_HISTORY = None


def read_command() -> str:
    """Read one command between red and blue rules, directly beside each other.

    prompt_toolkit's bottom_toolbar is deliberately not used here: it anchors
    to the *bottom of the terminal window*, not beneath the active input.
    The non-full-screen three-row layout keeps both rules next to the cursor.
    """
    try:
        from prompt_toolkit.application import Application, get_app
        from prompt_toolkit.buffer import Buffer
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.layout import Dimension, HSplit, Layout, Window
        from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
        from prompt_toolkit.layout.processors import BeforeInput
        from prompt_toolkit.output import ColorDepth
    except ImportError:
        # The core scanner still works if the optional UI library is missing.
        show_prompt_top()
        command = input("❯ " if _unicode_available() else "> ")
        show_prompt_bottom()
        return command

    global _PROMPT_HISTORY
    if _PROMPT_HISTORY is None:
        _PROMPT_HISTORY = InMemoryHistory()

    use_color = supports_color()
    red_style = "fg:#dc2626" if use_color else ""
    blue_style = "fg:#60a5fa" if use_color else ""
    cursor_style = "fg:#fb7185 bold" if use_color else ""
    text_style = "fg:#e2e8f0" if use_color else ""
    glyph = "─" if _unicode_available() else "-"
    prompt_symbol = "❯ " if _unicode_available() else "> "

    def line_fragments(style: str):
        # Use the active prompt's width; adapt when Windows Terminal resizes.
        width = max(1, get_app().output.get_size().columns - 2)
        return [(style, glyph * width)]

    buffer = Buffer(multiline=False, history=_PROMPT_HISTORY)
    editor = Window(
        BufferControl(buffer=buffer, input_processors=[BeforeInput(prompt_symbol, style=cursor_style)]),
        height=1,
        dont_extend_height=True,
        style=text_style,
    )
    layout = HSplit(
        [
            Window(FormattedTextControl(lambda: line_fragments(red_style)), height=1, dont_extend_height=True),
            editor,
            Window(FormattedTextControl(lambda: line_fragments(blue_style)), height=1, dont_extend_height=True),
        ],
        height=Dimension.exact(3),
    )

    keys = KeyBindings()

    @keys.add("enter")
    def accept(event):
        command = buffer.text
        if command.strip():
            _PROMPT_HISTORY.append_string(command)
        event.app.exit(result=command)

    @keys.add("c-c")
    def interrupt(event):
        event.app.exit(exception=KeyboardInterrupt())

    @keys.add("c-d")
    def end_of_file(event):
        if not buffer.text:
            event.app.exit(exception=EOFError())
        else:
            buffer.delete(1)

    app = Application(
        layout=Layout(layout, focused_element=editor),
        key_bindings=keys,
        full_screen=False,
        erase_when_done=False,
        color_depth=ColorDepth.TRUE_COLOR if use_color else ColorDepth.DEPTH_1_BIT,
    )
    return app.run()
