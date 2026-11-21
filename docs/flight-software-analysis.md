# Flight software: initial cFE call extraction

The internal `extract_bus_calls` API accepts a mapping of source paths to UTF-8 C
source bytes. It records expressions using `CFE_SB_CreatePipe`,
`CFE_SB_Subscribe`, `CFE_SB_SubscribeEx`, `CFE_SB_TransmitMsg`,
`CFE_SB_TransmitBuffer` and `CFE_MSG_SetMsgId`, preserving arguments, file and line.
Comments and quoted strings are masked when finding calls. The parser never runs
target code or a preprocessor.

The limits are 512 files, 2 MiB per file, 10 MiB total, 10,000 calls, 4,096
characters per argument list and 64 nested parentheses. Exceeding a limit or
encountering malformed input is disclosed. Results are always `partial`: matching
expressions can be declarations or inactive code, and preprocessing, types, data
flow and application ownership are not evaluated. A transmit message pointer is
not assumed to be a message ID. No trust level or privilege is inferred. This
building block does not yet produce a bus graph, security findings or a CLI output.

The call interpretation is informed by NASA's [cFE Application Developers
Guide](https://github.com/nasa/cFE/blob/dev/docs/cFE%20Application%20Developers%20Guide.md),
which describes pipes, subscriptions and message transmission.
