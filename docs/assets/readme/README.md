# README visual provenance

These assets document source commit `bfdbc758fa30445d4b8c322c6c2524664a172c7f` of ShivuXD/FUSE (source version 0.5.1). Captured on Windows with Python 3.14.0. Scanner behavior and evidence were not modified.

## CLI capture

`fuse-cli.png` is a faithful terminal-frame rendering of excerpts from real stdout, not a literal OS screenshot. `$` command prompts and the frame are presentation only; `...` marks omitted report lines. Complete stdout with those command prompts is in [fuse-cli.txt](fuse-cli.txt). The image preserves the two-finding count and the first finding's evidence and uncertainty.

Reproduce from an installed checkout in a neutral working directory:

1. Create a directory named `firmware`.
2. Copy [FUSE004-vulnerable.fixture](../../../tests/fixtures/rules/FUSE004-vulnerable.fixture) byte-for-byte to `firmware/main.c`.
3. Run:

```sh
vigil-fuse --version
vigil-fuse scan firmware --target-label demo/firmware
```

The capture invoked the same entry point with `python -m vigil_fuse`, loading this checkout's `src` via `PYTHONPATH`. Only the command spelling in the frame uses the installed console entry point. No target code or networked analyzer was executed. The fixture contains test endpoint strings, not real credentials or third-party vulnerability evidence. No privacy redactions were necessary: the target label avoids personal absolute paths.

## Archify preview

`fuse-archify-pipeline.png` is a browser raster capture of the existing SVG inside [site/diagrams/fuse-scan.html](../../../site/diagrams/fuse-scan.html), with its dark theme, embedded font and unchanged nodes/edges/legend. Motion was disabled for capture. PNG freezes fonts and colors for predictable GitHub light/dark rendering and avoids exporting interactive scripts or styles.

The source is an overview, not an exhaustive integration list. Its optional-tool lane names Syft, OSV-Scanner and Binwalk; the README separately documents Gitleaks, Ghidra and Clang. The inherited “Agent logic” legend is a diagram role label, not an AI runtime claim.

Interactive workflow visualization generated with Archify. Archify is not a FUSE runtime dependency. Original notices remain in the standalone HTML and [third-party credits](../../THIRD_PARTY_CREDITS.md).

The README links the verified deployed viewer at `https://sathack-vigil-fuse.vercel.app/diagrams/fuse-scan.html`, with the repository source alongside it. A relative GitHub HTML link opens source rather than an interactive page. The older package-homepage domain returned HTTP 503 and GitHub Pages did not serve this diagram.

## Reused figures

The README reuses the existing dark/light finding-model pair and trust-boundary SVG unchanged. They are conceptual illustrations, not physical-device evidence.

## README verification record

Verified on 2026-11-22 against the base commit above, on branch `docs/flagship-readme`. The requested ShivuXD/FUSE repository was cloned separately because the starting workspace belonged to the older VIGIL-IoT remote and contained ongoing CLI edits. Those files were left untouched. The new branch starts from the freshly fetched local `main`; no merge or push was performed.

State audit:

- **MERGED / CURRENT:** source 0.5.1, core scanner, CLIUI, firmware/hardware adapters, passive planning models, Clang evidence producer, probe-only Go operator, Java exporter and controlled C/C++ fixtures. Verified against files and Git ancestry, not inferred from branch names.
- **LOCAL VERIFIED:** documentation and CLI/contract checks below, native fixture scan, clean-wheel install and outputs, visual assets and Markdown preview.
- **LOCAL UNVERIFIED:** optional native Clang/Ghidra/tool installations, cluster and hardware behavior were not rerun for this documentation change.
- **IN DEVELOPMENT:** expansion is described as foundations with explicit limits. Unmerged local installer/policy/numerical research is not counted as main support.
- **FUTURE:** stronger applicability/correlation, protocol/trust evidence, fault injection and analyzer workers beyond the probe.
- **DEFERRED:** Rust acceleration without a measured need, general firmware extraction/execution and physical validation. No Zig runtime is claimed.

Observed checks:

| Check | Result |
| --- | --- |
| `python scripts/validate_docs.py` | Passed for 124 Markdown files; no broken local Markdown targets |
| `python -m pytest -q tests/test_docs_validation.py tests/test_cli_interactive.py tests/test_architecture_contracts.py tests/test_report_schema.py` | 27 passed, 16 subtests passed; one installed AnyIO plugin deprecation warning |
| `python -m build --wheel` | Built `vigil_fuse-0.5.1-py3-none-any.whl` |
| Fresh venv, wheel install with `--no-deps` | Passed; installed console entry point reports FUSE 0.5.1 |
| Installed `doctor`, `scan --plan`, fixture `scan --output-dir` | Passed; all three standard reports present; two findings and first endpoint/applicability checked in JSON |
| GitHub Markdown API, GFM mode | HTTP 200; rendered source used for previews |
| Rendered local links and image sources | 61 targets checked, including HTML `href`, `src` and `srcset`; README anchors and linked Markdown heading fragments checked |
| External README destinations | CI workflow, four badge images and deployed Archify viewer returned HTTP 200; deployed diagram content checked |
| Browser previews | Light/dark at 1280 px and 390 px; all 8 image elements loaded, no page-width overflow; desktop/mobile opening inspected |
| Mermaid pinned Docker renderer | Failed to complete: required image absent locally; fetch/run timed out after 120 seconds |
| Mermaid fallback | Mermaid 11.4.1 rendered the README diagram successfully in headless Chromium |
| Privacy and asset audit | No personal paths, emails, hostnames or secrets in capture; fixture strings preserved; PNGs total about 319 KiB |
| `git diff --check` | Passed |

The GFM response was previewed with GitHub-style Markdown CSS and local asset resolution, since unpublished images cannot load from GitHub main. This checks supported markup, assets, layout and Mermaid syntax; a published GitHub repository-page render remains unverified. The live CI badge displayed **failing** at preview time. No green hosted-CI claim is made.

Broken destinations avoided: the older homepage's diagram URL returned 503 and the GitHub Pages diagram URL returned 404. The README uses the verified deployed viewer instead. All selected final README targets passed.

Claims corrected or qualified: stale 0.4.0 source identity; maintenance-only wording; release-wide test totals from different commits; performance samples as a current speed ranking; fixture call recognition as vulnerability accuracy; automatic Clang verdicts; Go as a distributed analyzer; local research languages as merged runtime components. License and third-party notices were preserved.

Not rerun: full scanner suite, hosted CI, external analyzer installations, native compilation, live clusters and physical devices. No application code, rules, dependencies or version files changed.
