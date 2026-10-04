"""Generate a bcrypt hash for protected local SEMS demo configuration."""

from __future__ import annotations

import getpass

import bcrypt


def main() -> None:
    password = getpass.getpass("Demo password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if not password or password != confirmation:
        raise SystemExit("Passwords are empty or do not match.")
    print(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"))


if __name__ == "__main__":
    main()

