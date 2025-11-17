import pytest
from engine.dataframe import DataFrame


def test_header_and_length():
    data = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"}
    ]
    df = DataFrame(data)

    assert df.get_header() == ["id", "name"]
    assert len(df) == 2


def test_project_columns():
    data = [
        {"id": 1, "name": "A", "age": 20},
        {"id": 2, "name": "B", "age": 30},
    ]
    df = DataFrame(data)
    projected = df.project(["name", "age"])

    assert projected == [
        {"name": "A", "age": 20},
        {"name": "B", "age": 30}
    ]


def test_filter_rows():
    data = [
        {"id": 1, "score": 50},
        {"id": 2, "score": 90},
    ]
    df = DataFrame(data)

    filtered = df.filter(lambda r: r["score"] > 60)
    assert len(filtered) == 1
    assert filtered.data[0]["id"] == 2


def test_groupby_and_aggregate():
    data = [
        {"dept": "HR", "salary": 100},
        {"dept": "HR", "salary": 200},
        {"dept": "ENG", "salary": 300}
    ]

    df = DataFrame(data)
    groups = df.groupby("dept")
    agg = df.aggregate(groups, {"salary": "sum"})

    assert agg["HR"]["salary"] == 300
    assert agg["ENG"]["salary"] == 300


def test_join_operation():
    left = DataFrame([
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ])

    right = DataFrame([
        {"uid": 1, "age": 20},
        {"uid": 2, "age": 30},
    ])

    joined = left.join(right, left_on="id", right_on="uid")

    assert len(joined) == 2
    assert joined.data[0]["age"] == 20
    assert joined.data[1]["age"] == 30


def test_infer_types():
    data = [
        {"a": "10", "b": "1.5", "c": "hello"},
        {"a": "20", "b": "2.0", "c": "world"}
    ]

    df = DataFrame(data)
    types = df.get_column_types()

    assert types["a"] == "int"
    assert types["b"] == "float"
    assert types["c"] == "str"
