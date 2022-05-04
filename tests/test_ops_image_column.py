import os

import pytest

from csv2notion.cli import cli
from csv2notion.notion_db import NotionError


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_missing(tmp_path, db_maker):
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
                "--image-column",
                "image file",
                str(test_file),
            ]
        )

    assert "Image column 'image file' not found in csv file" in str(e.value)


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_file_not_found(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,image file\na,b,test_image.jpg\n")

    test_db = db_maker.from_csv_head("a,b,image file")

    with pytest.raises(NotionError) as e:
        cli(
            [
                "--token",
                os.environ.get("NOTION_TEST_TOKEN"),
                "--url",
                test_db.url,
                "--image-column",
                "image file",
                str(test_file),
            ]
        )

    assert "test_image.jpg does not exist" in str(e.value)


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_empty(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,image file\na,b,\n")

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--image-column",
            "image file",
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


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_ok(tmp_path, smallest_gif, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,image file\na,b,test_image.gif\n")

    test_image = tmp_path / "test_image.gif"
    test_image.write_bytes(smallest_gif)

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--image-column",
            "image file",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows
    image = table_rows[0].children[0]

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert len(table_rows[0].children) == 1
    assert image.type == "image"
    assert image.caption == "cover"
    assert test_image.name in image.display_source


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_url_ok(tmp_path, db_maker):
    test_image_url = "https://via.placeholder.com/100"

    test_file = tmp_path / "test.csv"
    test_file.write_text(f"a,b,image url\na,b,{test_image_url}\n")

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--image-column",
            "image url",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows
    image = table_rows[0].children[0]

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert len(table_rows[0].children) == 1
    assert image.type == "image"
    assert image.display_source == test_image_url


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_cover_mode_ok(tmp_path, smallest_gif, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,image file\na,b,test_image.gif\n")

    test_image = tmp_path / "test_image.gif"
    test_image.write_bytes(smallest_gif)

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--image-column",
            "image file",
            "--image-column-mode",
            "cover",
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
    assert test_image.name in table_rows[0].cover


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_cover_mode_url_ok(tmp_path, db_maker):
    test_image_url = "https://via.placeholder.com/100"

    test_file = tmp_path / "test.csv"
    test_file.write_text(f"a,b,image url\na,b,{test_image_url}\n")

    test_db = db_maker.from_csv_head("a,b")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--image-column",
            "image url",
            "--image-column-mode",
            "cover",
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
    assert table_rows[0].cover == test_image_url


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_keep_missing(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b\na,b\n")

    test_db = db_maker.from_csv_head("a,b,image file")

    with pytest.raises(NotionError) as e:
        cli(
            [
                "--token",
                os.environ.get("NOTION_TEST_TOKEN"),
                "--url",
                test_db.url,
                "--image-column",
                "image file",
                "--image-column-keep",
                str(test_file),
            ]
        )

    assert "Image column 'image file' not found in csv file" in str(e.value)


@pytest.mark.skipif(not os.environ.get("NOTION_TEST_TOKEN"), reason="No notion token")
@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_image_column_keep_ok(tmp_path, db_maker):
    test_image_url = "https://via.placeholder.com/100"

    test_file = tmp_path / "test.csv"
    test_file.write_text(f"a,b,image url\na,b,{test_image_url}\n")

    test_db = db_maker.from_csv_head("a,b,image url")

    cli(
        [
            "--token",
            os.environ.get("NOTION_TEST_TOKEN"),
            "--url",
            test_db.url,
            "--image-column",
            "image url",
            "--image-column-keep",
            str(test_file),
        ]
    )

    table_header = {c["name"] for c in test_db.schema}
    table_rows = test_db.rows
    image = table_rows[0].children[0]

    assert table_header == {"a", "b", "image url"}
    assert len(table_rows) == 1
    assert getattr(table_rows[0], "a") == "a"
    assert getattr(table_rows[0], "b") == "b"
    assert getattr(table_rows[0], "image url") == test_image_url
    assert len(table_rows[0].children) == 1
    assert image.type == "image"
    assert image.caption == "cover"
    assert image.display_source == test_image_url