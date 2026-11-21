# Polyglot platform foundation

Python owns intelligence, findings, applicability, coverage, policies, RepoDNA, component
graphs, target models, analysis routing and serialization. The existing scanner remains
canonical. The new `execution_contract` and explicit `python -m vigil_fuse.execution`
handoff do not change scanner behavior or add runtime dependencies.

Go schedules disposable Kubernetes Jobs. It handles operational state and isolation;
it does not classify security evidence. Rust is reserved for demonstrated performance
bottlenecks. Java remains the existing Ghidra exporter. C/C++ remain firmware targets
and actual native adapters. Julia is numerical research and R is statistical validation.
The opt-in [Clang semantic stage](../cpp-semantic-analysis.md) now implements C++
LibTooling observations with strict Python validation and a controlled C/C++ corpus.
It does not add automatic security verdicts or a Kubernetes worker. Julia and R
implementations remain deferred.

The initial worker is an identity probe. It echoes a target identifier and digest and
explicitly states that no target analysis occurred. It cannot emit findings or security
coverage. This proves message interchange without introducing arbitrary commands or
target mounts. Syft is the next analyzer after the probe passes live cluster validation.

The cyber-physical branch was inspected without merging: it adds DTS, SVD, reachability,
cFE, resilience and Renode export. A future Python ModelDescription can be staged as a
bounded worker input, with observations returned to Python. Renode execution is deferred.
The CLIUI branch was inspected without merging. Future UI can observe execution state;
it has no scheduling or authorization authority. Adaptive analysis is already in main.

See [execution backends](execution-backends.md), [operator](../kubernetes-operator.md),
and [native strategy](../native-engine-strategy.md).
