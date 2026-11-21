# FUSE operator foundation

Experimental controller for immutable `FuseScan` plans. It schedules only the deterministic
`probe` worker. Python remains responsible for validating the plan, envelope and evidence.
Job `Completed` means process success, never security success.

Requires Go 1.26+, Kubernetes and a CNI that enforces NetworkPolicy. These are optional
for the Python package. This implementation has not been compiled or exercised on a
cluster in its development environment because Go and a running Docker daemon were absent.

Run `go mod tidy`, `go test ./...`, `go vet ./...` and `gofmt -w cmd internal` here.
Review and commit the generated go.sum before deployment. Dependencies are not yet locked.

Use a dedicated namespace with restricted Pod Security admission and no untrusted resource
writers. Apply `config/crd.yaml` as a cluster administrator, then `config/rbac.yaml` within
that namespace. Build the probe image using `cluster/workers/native/Dockerfile`, publish
it explicitly, and obtain its digest. The controller rejects image tags without a digest.

Run with `FUSE_NAMESPACE` and `FUSE_WORKER_IMAGE` set, using the namespace-scoped
`fuse-operator` ServiceAccount (or equivalent local credentials). The image should be
`registry/image@sha256:<digest>`. No deployment manifest is supplied before compilation
and cluster validation have succeeded.

Create a resource with `apiVersion: fuse.vigil.dev/v1alpha1`, `kind: FuseScan` and a
Python-generated plan under `spec.plan`, with `execution_mode: kubernetes`. Observe
status and Jobs using `fuse.vigil.dev/scan` labels. Delete the FuseScan to garbage-collect
its owned Job, plan ConfigMap and NetworkPolicy. Completed Jobs remain for evidence retrieval.

The Job name and expected worker identifier are `fuse-<FuseScan UID>`. Retrieve stdout
from the owned Job's worker container, enforce the Python message byte limit, then call
`decode_message` and `validate_result(result, original_plan, expected_worker_id)`.
Evidence handoff currently requires this explicit caller step; no scanner CLI backend
or automatic log importer is advertised. ConfigMaps and stdout contain identity metadata
only. There is no target volume, secret volume or target analyzer in the probe.

Pending includes unavailable worker images and scheduling problems. Deadline/OOM/process
failure is Failed. Policy rejection is Blocked. A malformed or mismatched envelope is
rejected in Python even when Kubernetes reports Completed. None grants NOT_AFFECTED,
SAFE or NO_VULNERABILITY. Live timeout, OOM, killed worker, image failure and CNI enforcement
checks remain required before deployment. Namespace permissions and CNI policy enforcement
must be supplied by the cluster operator.
