"""Bounded extraction of cFE software-bus call evidence from C source."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping

MAX_BUS_FILES = 512
MAX_BUS_FILE_BYTES = 2 * 1024 * 1024
MAX_BUS_TOTAL_BYTES = 10 * 1024 * 1024
MAX_BUS_CALLS = 10_000
MAX_BUS_ARGUMENT_CHARS = 4096
MAX_BUS_CALL_DEPTH = 64
_CALL = re.compile(
    r"\b(CFE_SB_CreatePipe|CFE_SB_SubscribeEx|CFE_SB_Subscribe|"
    r"CFE_SB_TransmitMsg|CFE_SB_TransmitBuffer|CFE_MSG_SetMsgId)\s*\("
)


@dataclass(frozen=True)
class BusCall:
    file: str
    line: int
    api: str
    arguments: tuple[str, ...]


@dataclass(frozen=True)
class BusCalls:
    status: str
    calls: tuple[BusCall, ...]
    limitations: tuple[str, ...]


def _mask_c(text: str) -> tuple[str, bool]:
    """Mask comments and quoted literals while preserving offsets and newlines."""
    masked = list(text)
    i = 0
    complete = True
    while i < len(text):
        start = i
        if text.startswith("//", i):
            end = text.find("\n", i + 2)
            i = len(text) if end < 0 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end < 0:
                i = len(text)
                complete = False
            else:
                i = end + 2
        elif text[i] in "\"'":
            quote = text[i]
            i += 1
            while i < len(text) and text[i] != quote:
                i += 2 if text[i] == "\\" else 1
            if i >= len(text):
                i = len(text)
                complete = False
            else:
                i += 1
        else:
            i += 1
            continue
        for position in range(start, i):
            if masked[position] != "\n":
                masked[position] = " "
    return "".join(masked), complete


def extract_bus_calls(files: Mapping[str, bytes]) -> BusCalls:
    """Extract literal call expressions; no C preprocessing or target execution occurs."""
    limitations = {
        "C preprocessing, data flow, application ownership, and runtime routing are not resolved.",
        "Recognized expressions may include declarations or inactive code.",
    }
    if len(files) > MAX_BUS_FILES:
        return BusCalls("partial", (), ("Software-bus file limit exceeded.",))
    if sum(map(len, files.values())) > MAX_BUS_TOTAL_BYTES:
        return BusCalls("partial", (), ("Software-bus total byte limit exceeded.",))
    calls: list[BusCall] = []
    for name, data in sorted(files.items()):
        if len(data) > MAX_BUS_FILE_BYTES:
            limitations.add("At least one source file exceeded the byte limit.")
            continue
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            limitations.add("At least one source file is not UTF-8.")
            continue
        masked, complete = _mask_c(text)
        if not complete:
            limitations.add("At least one source file has an unterminated comment or string.")
        previous = 0
        line = 1
        for match in _CALL.finditer(masked):
            line += text.count("\n", previous, match.start())
            previous = match.start()
            if len(calls) >= MAX_BUS_CALLS:
                limitations.add("Software-bus call limit reached.")
                return BusCalls("partial", tuple(calls), tuple(sorted(limitations)))
            start = match.end()
            index = start
            depth = 1
            parts: list[str] = []
            part_start = start
            while index < len(masked) and index - start <= MAX_BUS_ARGUMENT_CHARS:
                char = masked[index]
                if char == "(":
                    depth += 1
                    if depth > MAX_BUS_CALL_DEPTH:
                        break
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        parts.append(text[part_start:index].strip())
                        break
                elif char == "," and depth == 1:
                    parts.append(text[part_start:index].strip())
                    part_start = index + 1
                index += 1
            if depth != 0:
                limitations.add("At least one call was malformed or exceeded a parsing limit.")
                continue
            calls.append(BusCall(name, line, match.group(1), tuple(parts)))
    # shortcut: C preprocessing and control flow are unresolved, upgrade before complete graphs.
    return BusCalls("partial", tuple(calls), tuple(sorted(limitations)))
