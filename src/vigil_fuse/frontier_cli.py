"""Noninteractive entry points for experimental cyber-physical evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .build_context import _read_bounded, _select_project_file
from .digital_twin import synthesize_digital_twin
from .flight_bus import (
    MAX_BUS_FILE_BYTES,
    MAX_BUS_FILES,
    MAX_BUS_TOTAL_BYTES,
    build_bus_graph,
    extract_bus_calls,
)
from .hardware_bom import inspect_hardware_bom
from .json_limits import bounded_json
from .seu_analysis import MAX_SEU_BYTES, inspect_critical_state
from .svd import MAX_SVD_BYTES, parse_svd
from .text_safety import safe_terminal_text


def register_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    twin = commands.add_parser("digital-twin", help="describe selected local SVD peripherals")
    twin.add_argument("target", type=Path, help="root containing the selected inputs")
    twin.add_argument("--svd", required=True, help="local CMSIS-SVD file inside target")
    twin.add_argument("--peripheral", action="append", default=[], help="select a peripheral by name")
    twin.add_argument("--hardware-bom", help="optional CSV or TSV BOM inside target")
    bus = commands.add_parser("flight-bus", help="extract partial cFE bus evidence")
    bus.add_argument("target", type=Path, help="root containing selected C source files")
    bus.add_argument("--source", action="append", required=True, metavar="APP=PATH",
                     help="assign a local C file to an application; repeat as needed")
    seu = commands.add_parser("seu", help="observe selected resilience indicators")
    seu.add_argument("target", type=Path, help="root containing the selected C file")
    seu.add_argument("--source", required=True, help="local C source file inside target")


def run_command(args: argparse.Namespace) -> int:
    try:
        if args.command == "flight-bus":
            if len(args.source) > MAX_BUS_FILES:
                raise ValueError("Software-bus file limit exceeded")
            files: dict[str, bytes] = {}
            applications: dict[str, str] = {}
            total = 0
            for assignment in args.source:
                app, separator, supplied = assignment.partition("=")
                if not separator or not app or not supplied:
                    raise ValueError("Each --source must be APP=PATH")
                path, display = _select_project_file(args.target, supplied, "--source")
                if display in files:
                    raise ValueError("A source file cannot be assigned more than once")
                data = _read_bounded(path, MAX_BUS_FILE_BYTES, "C source")
                total += len(data)
                if total > MAX_BUS_TOTAL_BYTES:
                    raise ValueError("Software-bus total byte limit exceeded")
                files[display] = data
                applications[display] = app
            sys.stdout.write(build_bus_graph(extract_bus_calls(files), applications).to_json())
            return 1
        if args.command == "seu":
            path, display = _select_project_file(args.target, args.source, "--source")
            seu_result = inspect_critical_state(_read_bounded(path, MAX_SEU_BYTES, "C source"))
            payload = {"source": display, "status": seu_result.status,
                       "states": seu_result.states, "limitations": seu_result.limitations}
            sys.stdout.write(bounded_json(payload, 4 * 1024 * 1024, indent=2))
            return 1
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
