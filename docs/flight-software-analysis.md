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
building block does not yet produce security findings or a CLI output.

`build_bus_graph` consumes the call records and a caller-supplied mapping from file
paths to application names. It exports deterministic JSON with application, pipe,
symbolic message-expression and transmitted message-object nodes. Create-pipe,
subscribe and transmit relationships retain source file, line and API. It preserves
duplicate observations. File ownership is not inferred; calls without assignments
are omitted. Graphs are capped at 30,000 nodes and 20,000 edges and remain partial.
The same message expression in two files is only a symbolic match and does not
establish an identical runtime ID. Transmit object expressions are not linked to
message IDs. Unhandled expressions and calls are disclosed in limitations.

The call interpretation is informed by NASA's [cFE Application Developers
Guide](https://github.com/nasa/cFE/blob/dev/docs/cFE%20Application%20Developers%20Guide.md),
which describes pipes, subscriptions and message transmission.
