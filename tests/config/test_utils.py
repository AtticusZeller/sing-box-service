import json
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

from sing_box_cli.config.utils import load_json_asdict, request_get, show_diff_config


# config.utils tests
## show_diff_config
def test_show_diff_config(capsys: pytest.CaptureFixture[str]) -> None:
    # Test with complex configs and sensitive data changes
    current = """{
      "outbounds": [
        {
          "type": "vless",
          "tag": "🌟Server WS",
          "server": "104.19.255.210",
          "uuid": "old-uuid-value",
          "tls": {
            "server_name": "cdn.example.com"
          }
        }
      ]
    }"""

    new = """{
      "outbounds": [
        {
          "type": "vless",
          "tag": "🌟Server WS",
          "server": "104.19.255.210",
          "uuid": "new-uuid-value",
          "tls": {
            "server_name": "cdn.example.com"
          }
        }
      ]
    }"""

    # Call function
    show_diff_config(current, new)

    # Get printed output
    captured = capsys.readouterr()
    output = captured.out

    # Verify output contains key elements
    assert "📄 Configuration differences:" in output
    assert "---" in output  # unified diff header
    assert "+++" in output  # unified diff header
    assert '-          "uuid": "old-uuid-value",' in output
    assert '+          "uuid": "new-uuid-value",' in output


def test_show_diff_config_no_changes(capsys: pytest.CaptureFixture[str]) -> None:
    # Test with identical configs
    config = """{"key": "value"}"""

    show_diff_config(config, config)

    captured = capsys.readouterr()
    output = captured.out

    assert "📄 Configuration differences:" in output
    assert len(output.splitlines()) == 1  # Only header line


def test_show_diff_config_empty(capsys: pytest.CaptureFixture[str]) -> None:
    # Test with empty configs
    show_diff_config("", "")

    captured = capsys.readouterr()
    output = captured.out

    assert "📄 Configuration differences:" in output
    assert len(output.splitlines()) == 1  # Only header line


## load_json
def test_load_json_success(tmp_path: Path) -> None:
    # Arrange
    data = {"key": "value", "nested": {"key": "value"}}
    file = tmp_path / "config.json"
    file.write_text(json.dumps(data))
    # Act
    result = load_json_asdict(file)

    # Assert
    assert result == data


@pytest.mark.parametrize(
    "filename,content",
    [
        ("empty.json", ""),  # Empty file
        ("incomplete.json", "{"),  # Incomplete JSON object
        ("missing_quotes.json", "{key: value}"),  # Missing quotes around keys/values
        ("trailing_comma.json", '{"key": "value",}'),  # Trailing comma
        ("unquoted_value.json", '{"key": value}'),  # Unquoted value
    ],
)
def test_load_json_invalid_format(
    tmp_path: Path, filename: str, content: str, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    file = tmp_path / filename
    file.write_text(content)

    # Act & Assert
    result = load_json_asdict(file)

    # Assert
    captured = capsys.readouterr()
    assert "❌ Failed to load configuration" in captured.out
    assert result == {}


## request_get
@pytest.mark.parametrize(
    "url,token",
    [
        ("https://api.example.com/data", "valid_token"),
        ("https://api.example.com/users", "another_token"),
    ],
)
def test_request_get_success(
    url: str, token: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    # Create a mock for httpx.get that returns our mock response
    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr(httpx, "get", mock_get)

    # Act
    result = request_get(url, token)

    # Assert
    mock_get.assert_called_once_with(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    assert result == mock_response


def test_request_get_http_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    url = "https://api.example.com/error"
    token = "valid_token"

    # Create a mock response that raises an HTTPStatusError when raise_for_status is called
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=MagicMock()
    )

    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr(httpx, "get", mock_get)

    # Act
    result = request_get(url, token)

    # Assert
    assert result is None
    captured = capsys.readouterr()
    assert f"❌ Failed to get from {url}" in captured.out
    assert "404 Not Found" in captured.out
