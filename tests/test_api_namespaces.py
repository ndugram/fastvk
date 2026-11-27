from __future__ import annotations

import pytest

from fastvk import FastVK
from fastvk.api.client import _APIMethod


@pytest.mark.parametrize("name", ["initialize_database", "extra_routes", "cron_jobs", "unknown"])
def test_optional_application_attributes_are_not_api_namespaces(name: str) -> None:
    app = FastVK(token="test-token")
    assert getattr(app, name, None) is None
    assert not hasattr(app, name)


@pytest.mark.parametrize("name", ["market", "board", "utils", "appWidgets"])
def test_known_generated_namespaces_are_available(name: str) -> None:
    app = FastVK(token="test-token")
    assert isinstance(getattr(app, name), _APIMethod)


def test_optional_application_hooks_can_be_set_explicitly() -> None:
    app = FastVK(token="test-token")
    hook = object()
    app.initialize_database = hook
    assert app.initialize_database is hook
