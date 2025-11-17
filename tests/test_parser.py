import pytest
import tempfile
import os
from engine.parser import CsvParser


def create_temp_csv(content: str):
    """Utility to create a temporary CSV file for testing."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8")
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_header_parsing():
    csv = "id,name,age\n1,A,10\n2,B,20\n"
    filepath = create_temp_csv(csv)

    parser = CsvParser(filepath)

    assert parser.get_header() == ["id", "name", "age"]

    os.remove(filepath)


def test_row_parsing():
    csv = "id,name\n1,A\n2,B\n3,C\n"
    filepath = create_temp_csv(csv)

    parser = CsvParser(filepath)
    rows = list(parser.parse())

    assert len(rows) == 3
    assert rows[0] == {"id": "1", "name": "A"}
    assert rows[2] == {"id": "3", "name": "C"}

    os.remove(filepath)


def test_type_inference():
    csv = """id,score,comment
1,10.5,good
2,20.0,okay
3,30,best
"""
    filepath = create_temp_csv(csv)

    parser = CsvParser(filepath)
    types = parser.get_column_types()

    assert types["id"] == "int"
    assert types["score"] == "float"
    assert types["comment"] == "str"

    os.remove(filepath)


def test_skip_malformed_rows():
    csv = """id,name
1,A
2,B,EXTRA
3,C
"""
    filepath = create_temp_csv(csv)

    parser = CsvParser(filepath)
    rows = list(parser.parse())

    # Row 2 is malformed (3 columns instead of 2), should be skipped
    assert len(rows) == 2
    assert rows[0] == {"id": "1", "name": "A"}
    assert rows[1] == {"id": "3", "name": "C"}

    os.remove(filepath)


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        CsvParser("missing_file.csv")
