# Observed demo scan

- FUSE 0.4.0, branch base `44039bf7eb3777bc232fc4bd489c90e4d974ccba`; scan performed on the uncommitted demo fixture based on that revision.
- Command: `python -m vigil_fuse scan demo/vulnerable-device --profile esp-idf --output-dir .fuse-demo-results --no-network --no-sbom --no-vulnerabilities --no-firmware --no-git-history` with the branch's `src` on PYTHONPATH.
- 11 findings: FUSE001 through FUSE007 and FUSE-GHA-001 through FUSE-GHA-004, one each. No expected signals failed.
- Eight selected files scanned; discovery complete, no limits reached. Native rules and GitHub Actions static analyzer completed. The profile reports basic support; source settings do not prove the active build or deployment.
- Optional external analyzers were deliberately disabled, so their availability was not assessed. No firmware, hardware netlist, dependency lock or selected build output was supplied.
- Generic profile does not select sdkconfig; use `--profile esp-idf`. Reports are static observations, not runtime validation.
