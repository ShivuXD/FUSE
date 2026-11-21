"""Noninteractive entry points for experimental cyber-physical evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .build_context import _read_bounded, _select_project_file
from .digital_twin import synthesize_digital_twin
from .hardware_bom import inspect_hardware_bom
from .svd import MAX_SVD_BYTES, parse_svd
from .text_safety import safe_terminal_text


def register_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    twin = commands.add_parser("digital-twin", help="describe selected local SVD peripherals")
    twin.add_argument("target", type=Path, help="root containing the selected inputs")
    twin.add_argument("--svd", required=True, help="local CMSIS-SVD file inside target")
    twin.add_argument("--peripheral", action="append", default=[], help="select a peripheral by name")
    twin.add_argument("--hardware-bom", help="optional CSV or TSV BOM inside target")


def run_command(args: argparse.Namespace) -> int:
    try:
        path, display = _select_project_file(args.target, args.svd, "--svd")
        data = _read_bounded(path, MAX_SVD_BYTES, "SVD")
        result = parse_svd(data, display)
        if result.device is None:
            raise ValueError("; ".join(result.limitations))
        bom = inspect_hardware_bom(args.target, args.hardware_bom) if args.hardware_bom else None
        twin = synthesize_digital_twin(result, tuple(args.peripheral), bom)
        sys.stdout.write(twin.to_json())
        return 1
    except (OSError, ValueError) as error:
        print(safe_terminal_text(f"vigil-fuse: {error}"), file=sys.stderr)
        return 2
