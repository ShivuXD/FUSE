"""Deterministic, non-executable mock peripheral descriptions."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import json

from .model import HardwareBOMInventory
from .svd import MAX_SVD_PERIPHERALS, MAX_SVD_TEXT_CHARS, PeripheralModel, SvdResult

MAX_TWIN_JSON_BYTES = 4 * 1024 * 1024


@dataclass(frozen=True)
class DigitalTwinDescription:
    status: str
    device: str
    svd_source: str
    svd_sha256: str
    svd_version: str | None
    bom_source: str | None
    bom_sha256: str | None
    bom_identity_candidates: tuple[str, ...]
    peripherals: tuple[PeripheralModel, ...]
    limitations: tuple[str, ...]

    def to_json(self) -> str:
        """Serialize with a hard output bound; no executable adapter is produced."""
        class Encoder(json.JSONEncoder):
            def default(self, value: object) -> object:
                if is_dataclass(value) and not isinstance(value, type):
                    return {field.name: getattr(value, field.name) for field in fields(value)}
                return super().default(value)

        encoder = Encoder(ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        chunks: list[str] = []
        size = 0
        for chunk in encoder.iterencode(self):
            size += len(chunk)
            if size + 1 > MAX_TWIN_JSON_BYTES:
                raise ValueError("Digital-twin JSON size limit exceeded")
            chunks.append(chunk)
        return "".join(chunks) + "\n"


def synthesize_digital_twin(
    svd: SvdResult, selected: tuple[str, ...] = (), bom: HardwareBOMInventory | None = None
) -> DigitalTwinDescription:
    """Use selected SVD entries as a description, without inventing behavior."""
    if svd.device is None or svd.status not in {"parsed", "partial"}:
        raise ValueError("A parsed SVD device is required")
    if len(selected) > MAX_SVD_PERIPHERALS or any(
        not name or len(name) > MAX_SVD_TEXT_CHARS for name in selected
    ):
        raise ValueError("Peripheral selection exceeds the supported limits")
    device = svd.device
    names = set(selected)
    available = {peripheral.name for peripheral in device.peripherals}
    if names - available:
        raise ValueError("At least one selected peripheral is absent from the SVD inventory")
    peripherals = tuple(sorted(
        (peripheral for peripheral in device.peripherals if not names or peripheral.name in names),
        key=lambda peripheral: peripheral.name,
    ))
    limitations = list(svd.limitations)
    limitations.append("No synthetic or measured peripheral behavior has been generated.")
    candidates: tuple[str, ...] = ()
    if bom is not None:
        if len(bom.components) > 50_000:
            raise ValueError("BOM component limit exceeded")
        if bom.status not in {"imported", "partial"}:
            limitations.append("The supplied BOM is unavailable or invalid.")
        else:
            candidates = tuple(sorted(
                component.reference for component in bom.components
                if component.name == device.name or component.part_number == device.name
            ))
            limitations.append("Exact BOM name matches are candidates, not verified device identity.")
            limitations.extend(bom.limitations)
    return DigitalTwinDescription(
        "partial", device.name, device.source, device.sha256, device.version,
        bom.source_path if bom is not None else None, bom.sha256 if bom is not None else None,
        candidates, peripherals, tuple(sorted(set(limitations))),
    )
