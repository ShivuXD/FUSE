from vigil_fuse.flight_bus import MAX_BUS_FILE_BYTES, extract_bus_calls


def test_extracts_calls_with_nested_arguments_and_ignores_comments_and_strings() -> None:
    source = b'''// CFE_SB_Subscribe(FAKE, fake)
        const char *s = "CFE_SB_CreatePipe(fake)";
        CFE_SB_CreatePipe(&app.pipe, DEPTH, "cmd,pipe");
        CFE_SB_Subscribe(CFE_SB_ValueToMsgId(CMD_MID), app.pipe);
        CFE_SB_TransmitMsg(CFE_MSG_PTR(app.Msg), true);
    '''
    result = extract_bus_calls({"app.c": source})
    assert result.status == "partial"
    assert [call.api for call in result.calls] == [
        "CFE_SB_CreatePipe", "CFE_SB_Subscribe", "CFE_SB_TransmitMsg"
    ]
    assert result.calls[0].arguments == ("&app.pipe", "DEPTH", '"cmd,pipe"')
    assert result.calls[1].arguments == ("CFE_SB_ValueToMsgId(CMD_MID)", "app.pipe")
    assert result.calls[1].line == 4


def test_bounded_and_malformed_sources_remain_partial() -> None:
    result = extract_bus_calls({"big.c": b'x' * (MAX_BUS_FILE_BYTES + 1),
                                "bad.c": b'CFE_SB_Subscribe(X, ('})
    assert result.status == "partial"
    assert not result.calls
    assert len(result.limitations) >= 3


def test_file_order_and_duplicate_calls_are_deterministic() -> None:
    call = b'CFE_SB_Subscribe(CMD_MID, pipe); CFE_SB_Subscribe(CMD_MID, pipe);'
    result = extract_bus_calls({"z.c": call, "a.c": call})
    assert [item.file for item in result.calls] == ["a.c", "a.c", "z.c", "z.c"]
