# Digital twin: SVD inventory foundation

The internal `parse_svd` API accepts a single explicitly supplied UTF-8 CMSIS-SVD
document as bytes and a source label. It records the SHA-256 digest, device name
and version, peripheral base addresses, interrupts, registers, access and reset
values, fields and enumerated values. Device and peripheral defaults are applied
to literal registers. It rejects DTDs and entity declarations and never downloads
vendor descriptions or runs firmware.

Inputs are capped at 10 MiB, 100,000 XML elements, 128 levels, 2,048 peripherals,
10,000 registers, 50,000 fields and 1,024 characters per extracted text field or
source label. Malformed XML, duplicate peripheral, register
or field names, and limit violations return `invalid`. Numeric literals are limited
to decimal, hexadecimal and binary values without wildcard bits. Results are
`partial`: derived definitions, arrays and register clusters are omitted; some
field range encodings, vendor extensions and other semantics are not interpreted.
No SVD schema validation or device identity matching is performed. A reset value
does not mean every bit is defined: consult the recorded reset mask.

`synthesize_digital_twin` creates a deterministic JSON-ready description of
selected peripherals and retains SVD provenance and unknown reset values. When a
BOM is supplied, exact component-name or part-number matches to the SVD device
name are recorded as candidates, not verified identity. Output is capped at 4 MiB.
The description adds no synthetic behavior and does not run firmware. Emulator
export and emulation are not yet implemented; no CLI or scan stage invokes this
API yet.

See Arm's [CMSIS-SVD register specification](https://arm-software.github.io/CMSIS_5/SVD/html/elem_registers.html)
for inheritance, fields, clusters and arrays.
