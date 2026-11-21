# Physical reachability: device-tree parsing foundation

The experimental `vigil_fuse.device_tree.parse_device_tree` API accepts bytes from a
single UTF-8 `.dts` or `.dtsi` file. It records literal node paths, labels and raw
property values, including `compatible`, `reg`, interrupts, aliases and pinctrl
references. Inputs are limited to 2 MiB, 10,000 nodes, 50,000 statements and 128
levels. It does not run `dtc`, build tooling or target code.

The parser does not resolve includes, preprocessor conditions or macros, overlays,
phandles, address cells, pin encodings or board wiring. Consequently every
otherwise successful result is `partial`: a literal property may be superseded or
excluded by configuration. Malformed or over-limit input is `invalid`. Unsupported
syntax can stop extraction early and is reported as partial. Callers must not
interpret an absent node or property as proof that a device or physical path is
absent. In particular, this parser alone does not establish physical reachability,
exploitability, severity or hardware behavior.

This is an internal building block; it is not yet integrated into scanning or a CLI
command. Use a trusted, separately built device-tree artifact and board-specific
documentation for decisions until those later stages exist and are validated.
