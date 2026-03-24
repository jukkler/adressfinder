import pytest
from unittest.mock import Mock


def make_response(json_data, status_code=200):
    resp = Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.fixture
def mock_httpx(monkeypatch):
    """Returns a function to set up httpx.get mock with given responses."""
    import httpx

    def _setup(responses):
        call_count = {"n": 0}

        def mock_get(url, **kwargs):
            if isinstance(responses, list):
                resp = responses[call_count["n"]]
                call_count["n"] += 1
                return resp
            if callable(responses) and not hasattr(responses, "json"):
                return responses(url, **kwargs)
            return responses

        monkeypatch.setattr(httpx, "get", mock_get)

    return _setup
