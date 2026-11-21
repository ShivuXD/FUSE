# Expected findings

All are static, native checks; no optional analyzer is required. Confidence is high for every row. These are review signals, not proof of a deployed vulnerability.

| Rule | File | Signal | Severity |
| --- | --- | --- | --- |
| FUSE001 | main/network_config.py | Fake credential literal | medium |
| FUSE002 | certs/demo_private.pem | Unusable PEM marker | high |
| FUSE003 | main/telemetry.py | TLS verification disabled | high |
| FUSE004 | main/network_config.py | Plaintext HTTP endpoint | medium |
| FUSE005 | main/network_config.py | Plaintext MQTT URI | medium |
| FUSE006 | sdkconfig | Always skip boot validation | medium |
| FUSE007 | sdkconfig | Skip deep-sleep boot validation | medium |
| FUSE-GHA-001 | .github/workflows/insecure-build.yml | write-all permissions | medium |
| FUSE-GHA-002 | .github/workflows/insecure-build.yml | Floating action ref | info |
| FUSE-GHA-003 | .github/workflows/insecure-build.yml | Privileged pull request head checkout | medium |
| FUSE-GHA-004 | .github/workflows/insecure-build.yml | Event data in shell command | medium |

The secure controls in main/safe_controls.py should not yield findings. Markdown is not selected by the profile.
