import logging
import re

import pytest

from csv2notion.cli import cli
from csv2notion.utils_exceptions import NotionError


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_file_empty(tmp_path, caplog, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b\na,")

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--custom-types",
                "file",
                "--max-threads=1",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    table_rows = test_db.rows
    table_header = test_db.header

    assert test_db.schema_dict["b"]["type"] == "file"

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == []


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_file_banned(tmp_path, caplog, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b\na,banned.exe")

    banned_file = tmp_path / "banned.exe"
    banned_file.touch()

    with pytest.raises(NotionError) as e:
        with caplog.at_level(logging.INFO, logger="csv2notion"):
            cli(
                [
                    "--token",
                    db_maker.token,
                    "--custom-types",
                    "file",
                    str(test_file),
                ]
            )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]
    db_maker.from_url(url)

    assert "File extension '*.exe' is not allowed to upload on Notion." in str(e.value)


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_file_embed(tmp_path, caplog, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(
        "a,b\n"
        "a1,https://via.placeholder.com/100\n"
        'a2,"https://via.placeholder.com/100, https://via.placeholder.com/200"'
    )

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--custom-types",
                "file",
                "--max-threads=1",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    table_rows = test_db.rows
    table_header = test_db.header

    assert test_db.schema_dict["b"]["type"] == "file"

    assert table_header == {"a", "b"}
    assert len(table_rows) == 2

    assert getattr(table_rows[0].columns, "a") == "a1"
    assert getattr(table_rows[0].columns, "b") == ["https://via.placeholder.com/100"]
    assert getattr(table_rows[1].columns, "a") == "a2"
    assert getattr(table_rows[1].columns, "b") == [
        "https://via.placeholder.com/100",
        "https://via.placeholder.com/200",
    ]


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_file_duplicate(tmp_path, caplog, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(
        'a,b\na,"https://via.placeholder.com/100, https://via.placeholder.com/100"'
    )

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--custom-types",
                "file",
                "--max-threads=1",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    table_rows = test_db.rows
    table_header = test_db.header

    assert test_db.schema_dict["b"]["type"] == "file"

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == ["https://via.placeholder.com/100"]


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_file_multi_column(tmp_path, caplog, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(
        "a,b,c\na,https://via.placeholder.com/100,https://via.placeholder.com/200"
    )

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--custom-types",
                "file,file",
                "--max-threads=1",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    table_rows = test_db.rows
    table_header = test_db.header

    assert test_db.schema_dict["b"]["type"] == "file"
    assert test_db.schema_dict["c"]["type"] == "file"

    assert table_header == {"a", "b", "c"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == ["https://via.placeholder.com/100"]
    assert getattr(table_rows[0].columns, "c") == ["https://via.placeholder.com/200"]


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_file_upload(tmp_path, caplog, db_maker, smallest_gif):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b\na,test_image.gif")

    test_image = tmp_path / "test_image.gif"
    test_image.write_bytes(smallest_gif)

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--custom-types",
                "file",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    table_rows = test_db.rows
    table_header = test_db.header

    assert test_db.schema_dict["b"]["type"] == "file"

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert "test_image.gif" in getattr(table_rows[0].columns, "b")[0]