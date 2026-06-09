from __future__ import annotations


from fastvk.exceptions import (
    FastVKError,
    FilterError,
    HandlerNotFoundError,
    PollingError,
    StorageError,
    VKAPIError,
)


class TestFastVKError:
    def test_is_base_exception(self) -> None:
        err = FastVKError("base error")
        assert isinstance(err, Exception)

    def test_str(self) -> None:
        err = FastVKError("something went wrong")
        assert str(err) == "something went wrong"

    def test_str_no_args(self) -> None:
        err = FastVKError()  # type: ignore[call-arg]
        assert str(err) == "FastVKError"


class TestVKAPIError:
    def test_error_code_and_message(self) -> None:
        err = VKAPIError({"error_code": 5, "error_msg": "Authorization failed"})
        assert err.code == 5
        assert err.message == "Authorization failed"

    def test_str_format(self) -> None:
        err = VKAPIError({"error_code": 5, "error_msg": "Authorization failed"})
        assert "[5]" in str(err)
        assert "Authorization failed" in str(err)

    def test_repr(self) -> None:
        err = VKAPIError({"error_code": 5, "error_msg": "Authorization failed"})
        r = repr(err)
        assert "VKAPIError" in r
        assert "5" in r

    def test_missing_fields_default(self) -> None:
        err = VKAPIError({})
        assert err.code == 0
        assert err.message == "Unknown error"

    def test_request_params(self) -> None:
        err = VKAPIError({"error_code": 5, "error_msg": "E", "request_params": [{"key": "v"}]})
        assert err.request_params == [{"key": "v"}]

    def test_is_fastvk_error(self) -> None:
        err = VKAPIError({"error_code": 5, "error_msg": "E"})
        assert isinstance(err, FastVKError)


class TestHandlerNotFoundError:
    def test_event_type_stored(self) -> None:
        err = HandlerNotFoundError("photo_new")
        assert err.event_type == "photo_new"

    def test_str_contains_event_type(self) -> None:
        err = HandlerNotFoundError("photo_new")
        assert "photo_new" in str(err)

    def test_is_fastvk_error(self) -> None:
        assert isinstance(HandlerNotFoundError("x"), FastVKError)


class TestFilterError:
    def test_filter_name_stored(self) -> None:
        err = FilterError("MyFilter")
        assert err.filter_name == "MyFilter"

    def test_str_with_cause(self) -> None:
        cause = ValueError("bad value")
        err = FilterError("MyFilter", cause=cause)
        assert "MyFilter" in str(err)
        assert "bad value" in str(err)

    def test_str_without_cause(self) -> None:
        err = FilterError("MyFilter")
        assert "MyFilter" in str(err)
        assert err.cause is None

    def test_repr(self) -> None:
        err = FilterError("MyFilter")
        assert "FilterError" in repr(err)


class TestStorageError:
    def test_operation_stored(self) -> None:
        err = StorageError("get_state")
        assert err.operation == "get_state"

    def test_with_key(self) -> None:
        err = StorageError("set_state", key="(1, 2)")
        assert "1, 2" in str(err)

    def test_with_cause(self) -> None:
        cause = ConnectionError("DB down")
        err = StorageError("get_state", cause=cause)
        assert "DB down" in str(err)

    def test_is_fastvk_error(self) -> None:
        assert isinstance(StorageError("op"), FastVKError)


class TestPollingError:
    def test_failed_1_reason(self) -> None:
        err = PollingError(failed=1)
        assert "outdated" in str(err)

    def test_failed_2_reason(self) -> None:
        err = PollingError(failed=2)
        assert "expired" in str(err)

    def test_failed_3_reason(self) -> None:
        err = PollingError(failed=3)
        assert "lost" in str(err)

    def test_unknown_failed_code(self) -> None:
        err = PollingError(failed=9)
        assert "unknown" in str(err)

    def test_ts_included_in_str(self) -> None:
        err = PollingError(failed=1, ts=12345)
        assert "12345" in str(err)

    def test_ts_optional(self) -> None:
        err = PollingError(failed=1)
        assert err.ts is None

    def test_repr(self) -> None:
        err = PollingError(failed=2, ts=100)
        assert "PollingError" in repr(err)
        assert "2" in repr(err)

    def test_is_fastvk_error(self) -> None:
        assert isinstance(PollingError(failed=1), FastVKError)
