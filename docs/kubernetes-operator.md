# Kubernetes operator

The experimental Go controller lives in [cluster/fuse-operator](../cluster/fuse-operator/README.md).
It accepts immutable namespaced FuseScan resources and creates owned ConfigMaps,
NetworkPolicies and disposable Jobs. The controller image setting is supplied by the
operator and must use a digest. Scan authors cannot choose worker commands or images.

The only enabled worker is the deterministic Python identity probe. A Job's completion
is an execution observation. Python must validate captured stdout against the original
plan and scheduled worker identity before accepting evidence. Network denial requires a
supporting CNI; creation of a NetworkPolicy alone is not proof of enforcement.

Worker security: UID 65532, non-root, no privilege escalation, read-only root filesystem,
all capabilities dropped, RuntimeDefault seccomp, no service-account token, no host
network, no host volumes, no secrets and bounded CPU/memory/time. Use a dedicated
namespace and restricted Pod Security admission. Namespace administrators remain trusted.

The supplied Role has namespaced access to FuseScans/status, Jobs, ConfigMaps and
NetworkPolicies. It has no Secret access. Apply CRDs separately with administrator
authorization. Deleting a FuseScan cancels execution through Kubernetes owner cleanup.
Pending, Running, Completed, Failed and Blocked are operational phases; Partial is
reserved for future evidence-aware workers. A worker log is the current evidence handoff,
so retrieve it before deleting the resource.

Go compilation, fake-client reconciliation and live Kubernetes integration remain
unverified in this environment. Go is absent, Docker daemon is unavailable and kind is
absent. No cluster was created. Do not deploy until module resolution, Go checks and live
tests succeed. See the operator README for exact prerequisites and commands.
