# INTENTIONALLY VULNERABLE DEMONSTRATION TARGET

This project exists solely to test and demonstrate FUSE. It must not be deployed, executed as a real service, or used as production firmware. All credentials, endpoints and key material are fake. The private addresses are static examples, not services; the PEM is not a valid key. No target code needs to run.

From the FUSE repository root in PowerShell:

```powershell
git switch demo/vulnerable-lab
py -m pip install -e .
vigil-fuse scan demo/vulnerable-device --plan --profile esp-idf --no-network --no-sbom --no-vulnerabilities --no-firmware --no-git-history
vigil-fuse scan demo/vulnerable-device --output-dir .fuse-demo-results --profile esp-idf --no-network --no-sbom --no-vulnerabilities --no-firmware --no-git-history
Get-Content .fuse-demo-results\findings.txt
.\scripts\run-vulnerable-demo.ps1
```

The helper performs no installations or downloads and disables optional external analyzers. Install the local package beforehand. The nested workflow is static data and is not a repository workflow. Repository self-scan excludes only this fixture; it must still scan FUSE source normally.

The explicit `esp-idf` profile is required: the default generic profile does not select sdkconfig or run FUSE006/007.
