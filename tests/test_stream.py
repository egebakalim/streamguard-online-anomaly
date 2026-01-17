from src.stream import generate_stream


def test_generate_stream_length():
    events = list(generate_stream(n=50, seed=1))
    assert len(events) == 50
    assert events[0].t == 0
    assert events[-1].t == 49
