from kensho.trace import TraceLogger


def test_trace_logger_assigns_step_indices_in_order() -> None:
    logger = TraceLogger()
    logger.log("first", {"n": 1})
    logger.log("second", {"n": 2})
    logger.log("third")

    events = logger.list_events()
    assert [event.step_index for event in events] == [0, 1, 2]
    assert [event.event_type for event in events] == ["first", "second", "third"]
    assert events[0].payload == {"n": 1}
    assert events[1].payload == {"n": 2}
    assert events[2].payload == {}


def test_trace_event_to_dict() -> None:
    logger = TraceLogger()
    event = logger.log("task_loaded", {"task_id": "demo"})
    payload = event.to_dict()
    assert payload["step_index"] == 0
    assert payload["event_type"] == "task_loaded"
    assert payload["timestamp"]
    assert payload["payload"] == {"task_id": "demo"}
