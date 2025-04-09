import os
import platform
import shutil
from pathlib import Path

import typer
from rich import print

from ..common import StrOrNone
from .utils import load_json_asdict, request_get, show_diff_config


class SingBoxConfig:
    def __init__(self) -> None:
        # Initialize config directories and files based on properties
        self._config_dir = (
            Path(typer.get_app_dir("sing-box", roaming=True))
            if self.is_windows
            else Path(f"~{self.user}/.config/sing-box").expanduser()
        )
        self._config_file = self._config_dir / "config.json"
        self._subscription_file = self._config_dir / "subscription.txt"
        self._token_file = self._config_dir / "token.txt"
        self._cache_db = self._config_dir / "cache.db"

        print(self)

    def init_directories(self) -> bool:
        """Initialize necessary directories and files for sing-box."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            # Create files if they don't exist
            for file_info in [
                (self.config_file, "{}", "config"),
                (self.subscription_file, "", "subscription"),
                (self.token_file, "", "token"),
            ]:
                file, content, name = file_info
                if not file.exists():
                    file.write_text(content)
                    print(f"📁 Created {name} file: {file}")
                # For Linux/Unix systems only - Windows will ignore this
                if not self.is_windows:
                    shutil.chown(file, user=self.user, group=self.user)

            # For Linux/Unix systems only - Windows will ignore this
            if not self.is_windows:
                shutil.chown(self.config_dir, user=self.user, group=self.user)
        except Exception as e:
            print(f"❌ Failed to initialize directories: {e}")
            return False
        return True

    @property
    def user(self) -> str:
        """Get the current username from environment variables."""
        user = (
            os.environ.get("SUDO_USER")
            or os.environ.get("USER")
            or os.environ.get("USERNAME")
        )
        if not user:
            raise ValueError("❌ Unable to detect user name")
        return user

    @property
    def bin_path(self) -> Path:
        """Get the path of the sing-box binary."""
        # sing-box-beta for linux beta version
        bin_path: Path | str | None = shutil.which("sing-box") or shutil.which(
            "sing-box-beta"
        )

        if not bin_path:
            bin_dir = Path(__file__).parents[1] / "bin"
            bin_path = (
                bin_dir / "sing-box"
                if not self.is_windows
                else bin_dir / "sing-box.exe"
            )
        return Path(bin_path).absolute()

    @property
    def is_windows(self) -> bool:
        """Check if the current platform is Windows."""
        return platform.system() == "Windows"

    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return self._config_dir.absolute()

    @property
    def config_file(self) -> Path:
        """Get the configuration file path."""
        return self._config_file

    @property
    def subscription_file(self) -> Path:
        """Get the subscription file path."""
        return self._subscription_file

    @property
    def token_file(self) -> Path:
        """Get the token file path."""
        return self._token_file

    @property
    def cache_db(self) -> Path:
        """Get the cache database path."""
        return self._cache_db

    @property
    def sub_url(self) -> str:
        """Get the subscription URL from the subscription file."""
        if not self.subscription_file.exists():
            return ""
        return self.subscription_file.read_text().strip()

    @sub_url.setter
    def sub_url(self, value: str) -> None:
        """Set the subscription URL in the subscription file."""
        self.subscription_file.write_text(value.strip())
        print("📁 Subscription updated successfully.")

    @property
    def api_base_url(self) -> str:
        """Get the API base URL from the configuration file."""
        config = load_json_asdict(self.config_file)
        url = (
            config.get("experimental", {})
            .get("clash_api", {})
            .get("external_controller", "")
        )
        if isinstance(url, str) and url:
            if not url.startswith("http"):
                url = f"http://{url}"
            return url
        return ""

    @property
    def api_secret(self) -> str:
        """Get the API secret from the configuration file."""
        config = load_json_asdict(self.config_file)
        token = config.get("experimental", {}).get("clash_api", {}).get("secret", "")
        if isinstance(token, str) and token:
            return token
        return ""

    @property
    def config_file_content(self) -> str:
        """Get the content of the configuration file."""
        return (
            self.config_file.read_text(encoding="utf-8")
            if self.config_file.exists()
            else "{}"
        )

    @config_file_content.setter
    def config_file_content(self, value: str) -> None:
        """Set the content of the configuration file."""
        self.config_file.write_text(value, encoding="utf-8")
        print("📁 Configuration updated successfully.")

    @property
    def token_content(self) -> str:
        """Get the token from the token file."""
        return self.token_file.read_text().strip() if self.token_file.exists() else ""

    @token_content.setter
    def token_content(self, value: str) -> None:
        """Set the token in the token file."""
        self.token_file.write_text(value.strip())
        print("🔑 Token added successfully.")

    def update_config(self, sub_url: StrOrNone = None, token: StrOrNone = None) -> bool:
        """Download configuration from subscription URL and show differences."""
        try:
            if sub_url is None:
                # load from file
                if not self.sub_url:
                    print("❌ No subscription URL found.")
                    return False
                sub_url = self.sub_url
            if token is None:
                # load from file
                token = self.token_content
            print(f"⌛ Updating configuration from {sub_url}")
            response = request_get(sub_url, token)
            if response is None:
                print("❌ Failed to get configuration.")
                return False

            new_config = response.text

            if not self.is_windows:
                shutil.chown(self.config_file, user=self.user, group=self.user)

            if self.config_file_content == new_config:
                print("📄 Configuration is up to date.")
            else:
                # update and show differences
                show_diff_config(self.config_file_content, new_config)
                self.config_file_content = new_config

            # update subscription url file
            if sub_url != self.sub_url:
                self.sub_url = sub_url
            if token != self.token_content:
                self.token_content = token
            return True
        except Exception as e:
            print(f"❌ Failed to update configuration: {e}")
            return False

    def show_subscription(self) -> None:
        """Display the current subscription URL."""
        if self.sub_url:
            print(f"🔗 Current subscription URL: {self.sub_url}")
        else:
            print("❌ No subscription URL found.")

    def clean_cache(self) -> None:
        """Remove the cache database file."""
        try:
            self.cache_db.unlink()
            print("🗑️ Cache database removed.")
        except FileNotFoundError:
            print("❌ Cache database not found.")
        except PermissionError:
            print(
                "❌ Permission denied to remove cache database. Stop the service first."
            )
        except Exception as e:
            print(f"❌ Failed to remove cache database: {e}")

    def __str__(self) -> str:
        """Return a string representation of the configuration."""
        info = (
            f"🔧 Using binary: {self.bin_path}\n"
            f"📄 Using configuration: {self.config_file}"
        )

        if self.is_windows:
            info += f"\n📁 Using installation directory: {self.config_dir}"
        return info


def get_config() -> SingBoxConfig:
    """Get a cached SingBoxConfig instance."""
    config = SingBoxConfig()
    if not config.init_directories():
        raise FileNotFoundError("❌ Failed to initialize directories")
    return config
