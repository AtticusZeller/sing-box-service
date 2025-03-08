import pytest

from sing_box_service.config import show_diff_config


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
