"""
Simple single-user authentication for RabbitMirror.

This replaces the complex multi-user authentication system with a basic
password protection suitable for single-user tools.
"""

import configparser
import hashlib
import os
import secrets
from pathlib import Path
from typing import Optional


class SimpleAuth:
    """Simple password-based authentication for single-user mode."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize simple authentication with config file."""
        self.config_file = config_file or os.path.expanduser("~/.rabbitmirror_auth")
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Load authentication configuration from file."""
        if Path(self.config_file).exists():
            self.config.read(self.config_file)
        else:
            # Create default config if none exists
            self._create_default_config()

    def _create_default_config(self):
        """Create a default configuration file."""
        self.config["auth"] = {"password_hash": "", "salt": "", "enabled": "true"}

        print(f"Creating default auth config at {self.config_file}")
        print("Use set_password() method to set up authentication")
        self._save_config()

    def _save_config(self):
        """Save configuration to file."""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w") as f:
            self.config.write(f)

        # Set restrictive permissions on config file
        config_path.chmod(0o600)

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def set_password(self, password: str):
        """Set the authentication password."""
        if not password or len(password) < 4:
            raise ValueError("Password must be at least 4 characters long")

        # Generate random salt
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)

        self.config["auth"]["password_hash"] = password_hash
        self.config["auth"]["salt"] = salt
        self.config["auth"]["enabled"] = "true"

        self._save_config()
        print(f"Password set successfully. Config saved to {self.config_file}")

    def verify_password(self, password: str) -> bool:
        """Verify the provided password."""
        if not self.is_enabled():
            return True  # No authentication required

        stored_hash = self.config.get("auth", "password_hash", fallback="")
        salt = self.config.get("auth", "salt", fallback="")

        if not stored_hash or not salt:
            return False  # No password configured

        provided_hash = self._hash_password(password, salt)
        return provided_hash == stored_hash

    def is_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return self.config.getboolean("auth", "enabled", fallback=True)

    def disable_auth(self):
        """Disable authentication (no password required)."""
        self.config["auth"]["enabled"] = "false"
        self._save_config()
        print("Authentication disabled")

    def enable_auth(self):
        """Enable authentication."""
        self.config["auth"]["enabled"] = "true"
        self._save_config()
        print("Authentication enabled")

    def has_password(self) -> bool:
        """Check if a password has been configured."""
        return bool(self.config.get("auth", "password_hash", fallback=""))


# Global instance for the application
simple_auth = SimpleAuth()


def setup_simple_auth():
    """Interactive setup for simple authentication."""
    print("RabbitMirror Simple Authentication Setup")
    print("=" * 40)

    if simple_auth.has_password():
        print("Authentication is already configured.")
        choice = input("Do you want to change the password? (y/N): ").lower()
        if choice != "y":
            return

    print("\nChoose authentication mode:")
    print("1. Set password protection")
    print("2. Disable authentication (no password required)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        import getpass

        while True:
            password = getpass.getpass("Enter password (min 4 characters): ")
            if len(password) >= 4:
                confirm = getpass.getpass("Confirm password: ")
                if password == confirm:
                    simple_auth.set_password(password)
                    break
                else:
                    print("Passwords don't match. Try again.")
            else:
                print("Password must be at least 4 characters long.")

    elif choice == "2":
        simple_auth.disable_auth()
        print("Authentication disabled. Anyone can access the application.")

    else:
        print("Invalid choice. Setup cancelled.")


if __name__ == "__main__":
    setup_simple_auth()
