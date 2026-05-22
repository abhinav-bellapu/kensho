from graph_cycle import has_cycle


def test_empty_graph():
    assert has_cycle({}) is False


def test_no_edges():
    assert has_cycle({"a": [], "b": []}) is False


def test_simple_cycle():
    assert has_cycle({"a": ["b"], "b": ["a"]}) is True


def test_self_loop():
    assert has_cycle({"a": ["a"]}) is True


def test_dag_no_cycle():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    assert has_cycle(graph) is False


def test_diamond_dag():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    assert has_cycle(graph) is False


def test_cycle_with_tail():
    graph = {"a": ["b"], "b": ["c"], "c": ["a"], "d": []}
    assert has_cycle(graph) is True


def test_three_node_cycle():
    assert has_cycle({"x": ["y"], "y": ["z"], "z": ["x"]}) is True
