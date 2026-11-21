# Radiation-resilience observations

The internal `inspect_critical_state` API accepts one UTF-8 C source file as bytes.
It recognizes a narrow set of integer, boolean and `_t` declarations with selected
flight-state, arming, watchdog, thruster, heater, power-state, reset-counter and
mission-timer names. It looks for same-line checksum/parity calls, bound comparisons
and comparisons with identifiers containing `copy`, `backup` or `redundant`.
Evidence includes the observed line and a bounded, masked excerpt.

The result is always partial and confidence is low. `PROTECTION_OBSERVED` means
only that a selected syntactic indicator appeared; it does not establish that the
check protects the state or works correctly. `NO_PROTECTION_OBSERVED` means only
that these checks did not find a selected indicator, not that no protection exists.
Repeated names in different scopes produce `UNKNOWN`. Truncation or malformed input
can produce `PARTIAL`. The checks do not prove radiation safety, and they do not
model data flow, preprocessing, interrupts, hardware ECC or protection elsewhere.

Processing is limited to 2 MiB per file, 512 state names, 4,096 characters per
line and 20,000 state-use checks. This is an internal API, not yet a CLI or scan
stage; it never executes target code.
