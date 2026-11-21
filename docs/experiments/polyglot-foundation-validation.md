# Polyglot foundation validation

Repository: `https://github.com/ShivuXD/FUSE`, separate checkout `FUSE-polyglot`.
Branch: `feat/polyglot-platform-foundation`. Starting commit:
`63fb424ab262d1dc99ea4c0d872b7c9fe9cfe533`.
The original VIGIL-IoT checkout and its cyber-physical branch were left intact.

## Implemented boundary

Python: versioned AnalysisPlan and EvidenceEnvelope schemas, strict standard-library
validation, explicit plan and result file handoff commands, deterministic identity probe,
and rejection tests. The scanner CLI, router and findings APIs were not changed.
Python uses no new runtime dependencies. The probe has no security interpretation.

Go: module `github.com/ShivuXD/FUSE/cluster/fuse-operator`, controller-runtime v0.25.3,
immutable FuseScan CRD, controller, bounded Job builder, namespace Role/RoleBinding,
ServiceAccount and deny ingress/egress NetworkPolicy. Isolation and operational failure
tests plus a fake-client policy rejection test are supplied. Separate Go CI is supplied.
The [upstream module](https://github.com/kubernetes-sigs/controller-runtime/blob/v0.25.3/go.mod)
requires Go 1.26.0, matching the supplied go.mod.

Go compilation, vet, formatting and dependency locking are pending because Go is not
installed. No go.sum is fabricated. CI resolves dependencies before checking the module;
generate/review/commit go.sum before deployment. The operator remains experimental.

## Observed commands

Commands used the checkout's `.venv/Scripts/python` unless noted.

| Command | Observed result |
| --- | --- |
| `python -m pip install -e ".[dev]"` | Installed successfully |
| Baseline `python -m pytest -q` | 386 passed, 8 failed, 1 skipped; 184 subtests passed |
| Final `python -m pytest -q` | 403 passed, same 8 failed, 1 skipped; 184 subtests passed |
| `python -m pytest tests/test_execution_contract.py -q` | 17 passed |
| `python -m ruff check src tests scripts` | Passed |
| `python -m mypy src/vigil_fuse/execution_contract.py src/vigil_fuse/execution_worker.py src/vigil_fuse/execution.py` | Passed |
| `python -m mypy` | 13 existing terminal.py errors in isolated environment |
| `python scripts/validate_docs.py` | Passed for 117 Markdown files |
| `vigil-fuse --help` | Passed |
| `vigil-fuse doctor` | Exited successfully |
| `vigil-fuse scan . --plan` | Exited successfully without Go/Kubernetes |
| Existing synthetic scan benchmark | Completed; see benchmark record |
| `git diff --check` | Passed |
| `python -m build --wheel` | Built successfully; execution modules and both schemas verified in wheel |
| YAML parse of Kubernetes config manifests | Passed; API-server validation pending |

The same eight tests failed before and after implementation: freeze repeatability,
tracked/untracked documentation discovery, repository cohort RSS, separate provenance
manifest, dirty-scanner refusal and three terminal banner tests. They were not weakened
or altered. Isolated mypy reports eight missing prompt_toolkit imports and five annotation
errors in terminal.py. The earlier system-wide environment reported six terminal errors.

## Integration limits

No Kubernetes cluster was used and no image was built. kubectl client v1.34.1 exists,
but Docker daemon, Go, kind and Rust were unavailable. No system software was installed.
Go tests and live Job execution are unverified. NetworkPolicy enforcement, OOM, killed
workers, deadlines, missing image and cluster/CRD failures need live validation. The Go
unit tests describe bounded operational handling; they are not measured cluster results.
Captured envelopes reject invalid JSON, wrong schema, worker/plan mismatches and false
security coverage in Python tests. Partial execution remains an operational limitation.

The end-to-end cluster milestone is pending these prerequisites. Syft is intentionally
deferred until the deterministic cluster probe succeeds. Evidence handoff currently uses
captured Job stdout and explicit Python validation. No automatic Kubernetes scan backend
is advertised.

Rust: `NO_RUST_NEEDED_YET`; the measured small synthetic workload does not isolate a hot
path. No C/C++ adapters or fixtures, Java exporter changes, or Julia/R experiments were
needed. No empty language showcase projects were created.

## Git and next commands

Main directly modified: NO. Automatic merge: NO. Force push: NO. Remote push: NO.
Local commits only. For the final commit IDs and clean-tree status use `git log -3 --oneline`
and `git status` in this checkout.

With Go 1.26+ installed, run from `cluster/fuse-operator`:

```powershell
go mod tidy
gofmt -w cmd internal
go test ./...
go vet ./...
```

Then review module/format changes and follow the [operator guide](../../cluster/fuse-operator/README.md)
on an explicitly authorized test cluster. Once the branch is reviewed, the optional
publication command is `git push -u origin feat/polyglot-platform-foundation`. It was not run.
