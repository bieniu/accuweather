"""Set up some common test helper things."""

from pathlib import Path
from typing import Any

import orjson
import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.amber import AmberSnapshotExtension
from syrupy.location import PyTestLocation


@pytest.fixture
def location_data() -> dict[str, Any]:
    """Location data fixture."""
    with open("tests/fixtures/location_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.fixture
def current_condition_data() -> dict[str, Any]:
    """Weather current condition data fixture."""
    with open("tests/fixtures/current_condition_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.fixture
def daily_forecast_data() -> dict[str, Any]:
    """Daily forecast data fixture."""
    with open("tests/fixtures/daily_forecast_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.fixture
def hourly_forecast_data() -> list[dict[str, Any]]:
    """Hourly forecast data fixture."""
    with open("tests/fixtures/hourly_forecast_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture."""
    return snapshot.use_extension(SnapshotExtension)


class SnapshotExtension(AmberSnapshotExtension):
    """Extension for Syrupy."""

    @classmethod
    def dirname(cls, *, test_location: PyTestLocation) -> str:
        """Return the directory for the snapshot files."""
        test_dir = Path(test_location.filepath).parent
        return str(test_dir.joinpath("snapshots"))
