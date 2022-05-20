import datetime
import logging
import re

import pytest
from dateutil.tz import tz

from csv2notion.cli import cli


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_created_time(tmp_path, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b\na,2001-12-01\nb,bad")

    test_db = db_maker.from_cli(
        "--token",
        db_maker.token,
        "--custom-types",
        "created_time",
        "--max-threads=1",
        str(test_file),
    )

    test_client = test_db.page._client

    table_rows = test_db.rows
    table_header = test_db.header

    cur_timezone = tz.gettz(
        test_client.get_record_data("user_settings", test_client.current_user.id)[
            "settings"
        ]["time_zone"]
    )
    test_time = datetime.datetime(2001, 12, 1).replace(tzinfo=cur_timezone)
    test_time = test_time.astimezone(tz.tzutc())
    test_time = test_time.replace(tzinfo=None)

    assert test_db.schema_dict["b"]["type"] == "created_time"

    assert table_header == {"a", "b"}
    assert len(table_rows) == 2

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == test_time
    assert table_rows[0].created_time == test_time
    assert getattr(table_rows[1].columns, "a") == "b"
    # this one will be set to now, but it's generated by server so we can't check it
    assert isinstance(getattr(table_rows[1].columns, "b"), datetime.datetime)


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_created_time_multi(tmp_path, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(
        "a,b,c\na,2001-11-01,2001-12-01\nb,2001-12-01,bad\nc,bad,2001-12-01"
    )

    test_db = db_maker.from_cli(
        "--token",
        db_maker.token,
        "--custom-types",
        "created_time,created_time",
        "--max-threads=1",
        str(test_file),
    )

    test_client = test_db.page._client

    table_rows = test_db.rows
    table_header = test_db.header

    cur_timezone = tz.gettz(
        test_client.get_record_data("user_settings", test_client.current_user.id)[
            "settings"
        ]["time_zone"]
    )
    test_time = datetime.datetime(2001, 12, 1).replace(tzinfo=cur_timezone)
    test_time = test_time.astimezone(tz.tzutc())
    test_time = test_time.replace(tzinfo=None)

    assert test_db.schema_dict["b"]["type"] == "created_time"
    assert test_db.schema_dict["c"]["type"] == "created_time"

    assert table_header == {"a", "b", "c"}
    assert len(table_rows) == 3

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == test_time
    assert getattr(table_rows[0].columns, "c") == test_time
    assert table_rows[0].created_time == test_time
    assert getattr(table_rows[1].columns, "a") == "b"
    assert getattr(table_rows[1].columns, "b") == test_time
    assert getattr(table_rows[1].columns, "c") == test_time
    assert table_rows[1].created_time == test_time
    assert getattr(table_rows[2].columns, "a") == "c"
    assert getattr(table_rows[2].columns, "b") == test_time
    assert getattr(table_rows[2].columns, "c") == test_time
    assert table_rows[2].created_time == test_time


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_last_edited_time(tmp_path, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b\na,2001-12-01\nb,bad")

    test_db = db_maker.from_cli(
        "--token",
        db_maker.token,
        "--custom-types",
        "last_edited_time",
        "--max-threads=1",
        str(test_file),
    )

    test_client = test_db.page._client

    table_rows = test_db.rows
    table_header = test_db.header

    cur_timezone = tz.gettz(
        test_client.get_record_data("user_settings", test_client.current_user.id)[
            "settings"
        ]["time_zone"]
    )
    test_time = datetime.datetime(2001, 12, 1).replace(tzinfo=cur_timezone)
    test_time = test_time.astimezone(tz.tzutc())
    test_time = test_time.replace(tzinfo=None)

    assert test_db.schema_dict["b"]["type"] == "last_edited_time"

    assert table_header == {"a", "b"}
    assert len(table_rows) == 2

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == test_time
    assert table_rows[0].last_edited_time == test_time
    assert getattr(table_rows[1].columns, "a") == "b"
    # this one will be set to now, but it's generated by server so we can't check it
    assert isinstance(getattr(table_rows[1].columns, "b"), datetime.datetime)


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_custom_types_last_edited_time_multi(tmp_path, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(
        "a,b,c\na,2001-11-01,2001-12-01\nb,2001-12-01,bad\nc,bad,2001-12-01"
    )

    test_db = db_maker.from_cli(
        "--token",
        db_maker.token,
        "--custom-types",
        "last_edited_time,last_edited_time",
        "--max-threads=1",
        str(test_file),
    )

    test_client = test_db.page._client

    table_rows = test_db.rows
    table_header = test_db.header

    cur_timezone = tz.gettz(
        test_client.get_record_data("user_settings", test_client.current_user.id)[
            "settings"
        ]["time_zone"]
    )
    test_time = datetime.datetime(2001, 12, 1).replace(tzinfo=cur_timezone)
    test_time = test_time.astimezone(tz.tzutc())
    test_time = test_time.replace(tzinfo=None)

    assert test_db.schema_dict["b"]["type"] == "last_edited_time"
    assert test_db.schema_dict["c"]["type"] == "last_edited_time"

    assert table_header == {"a", "b", "c"}
    assert len(table_rows) == 3

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == test_time
    assert getattr(table_rows[0].columns, "c") == test_time
    assert table_rows[0].last_edited_time == test_time
    assert getattr(table_rows[1].columns, "a") == "b"
    assert getattr(table_rows[1].columns, "b") == test_time
    assert getattr(table_rows[1].columns, "c") == test_time
    assert table_rows[1].last_edited_time == test_time
    assert getattr(table_rows[2].columns, "a") == "c"
    assert getattr(table_rows[2].columns, "b") == test_time
    assert getattr(table_rows[2].columns, "c") == test_time
    assert table_rows[2].last_edited_time == test_time
