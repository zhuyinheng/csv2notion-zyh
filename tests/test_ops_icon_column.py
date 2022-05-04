import os

import pytest

from csv2notion.cli import cli
from csv2notion.notion_db import NotionError


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_missing(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\na,b,c\n")

    test_db = db_maker.from_csv_head("a,b,c")

    with pytest.raises(NotionError) as e:
        cli(
            [
                "--token",
                os.environ.get("NOTION_TEST_TOKEN"),
                "--url",
                test_db.url,
                "--icon-column",
                "icon file",
                str(test_file),
            ]
        )

    assert "Icon column 'icon file' not found in csv file" in str(e.value)


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_file_not_found(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,icon file\na,b,test_image.jpg\n")

    test_db = db_maker.from_csv_head("a,b,icon file")

    with pytest.raises(NotionError) as e:
        cli(
            [
                "--token",
                os.environ.get("NOTION_TEST_TOKEN"),
                "--url",
                test_db.url,
                "--icon-column",
                "icon file",
                str(test_file),
            ]
        )

    assert "test_image.jpg does not exist" in str(e.value)


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_empty(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,icon file\na,b,\n")

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--icon-column",
            "icon file",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert len(table_rows[0].children) == 0
    assert table_rows[0].icon is None


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_ok(tmp_path, smallest_gif, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,icon file\na,b,test_image.gif\n")

    test_image = tmp_path / "test_image.gif"
    test_image.write_bytes(smallest_gif)

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--icon-column",
            "icon file",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert len(table_rows[0].children) == 0
    assert test_image.name in table_rows[0].icon


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_url_ok(tmp_path, db_maker):
    test_icon_url = "https://via.placeholder.com/100"

    test_file = tmp_path / "test.csv"
    test_file.write_text(f"a,b,icon url\na,b,{test_icon_url}\n")

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--icon-column",
            "icon url",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert len(table_rows[0].children) == 0
    assert table_rows[0].icon == test_icon_url


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_emoji_ok(tmp_path, db_maker):
    test_icon_emoji = "🤔"

    test_file = tmp_path / "test.csv"
    test_file.write_text(f"a,b,icon emoji\na,b,{test_icon_emoji}\n", encoding="utf-8")

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--icon-column",
            "icon emoji",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert len(table_rows[0].children) == 0
    assert table_rows[0].icon == test_icon_emoji


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_keep_missing(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b\na,b\n")

    test_db = db_maker.from_csv_head("a,b,icon url")

    with pytest.raises(NotionError) as e:
        cli(
            [
                "--token",
                os.environ.get("NOTION_TEST_TOKEN"),
                "--url",
                test_db.url,
                "--icon-column",
                "icon url",
                "--icon-column-keep",
                str(test_file),
            ]
        )

    assert "Icon column 'icon url' not found in csv file" in str(e.value)


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_icon_column_keep_ok(tmp_path, db_maker):
    test_icon_url = "https://via.placeholder.com/100"

    test_file = tmp_path / "test.csv"
    test_file.write_text(f"a,b,icon url\na,b,{test_icon_url}\n")

    test_db = db_maker.from_csv_head("a,b,icon url")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--icon-column",
            "icon url",
            "--icon-column-keep",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows

    assert table_header == {"a", "b", "icon url"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert getattr(table_rows[0], "icon url") == test_icon_url
    assert len(table_rows[0].children) == 0
    assert table_rows[0].icon == test_icon_url