import enum
import os
import shlex
import subprocess
import logging
from typing import IO

logger = logging.getLogger(__name__)


# For now there is no reason to implement any different errors,
# but these are implemented ahead of time, in case that in the future
# we need to implement custom functionality.
ShellTimeout = subprocess.TimeoutExpired
ShellError = subprocess.CalledProcessError
CompletedProcess = subprocess.CompletedProcess


class Locales(enum.Enum):
    english = enum.auto()
    italian = enum.auto()


class Shell:
    """
    Object interfacing with the system shell to run commands.

    A default instance is provided to make some methods
    conveniently available at the module level.
    """

    KEYS = {
        "LOCALE_KEY": "LC_ALL",
    }

    def __init__(
        self, _locale: Locales = Locales.english, keys: dict[str, str] | None = None
    ):
        self.locale = _locale
        if keys is not None:
            self.KEYS.update(keys)

    def __repr__(self) -> str:
        return f"Shell(locale={self.locale}, keys={self.KEYS})"

    def __hash__(self) -> int:
        return hash((self.locale, tuple(self.KEYS.items())))

    def run(
        self,
        command: str,
        *,
        timeout: float = 60,
        stdout: int | IO | None = subprocess.PIPE,
        stderr: int | IO | None = subprocess.PIPE,
        env: dict[str, str] | None = None,
        check: bool = False,
        shell: bool = True,
        text: bool = True,
    ) -> CompletedProcess:
        """
        Execute a shell command from a string.

        It's a simple wrapper around the standard ``subprocess.run``
        method with some sane defaults.

        The locale is set in the ``env`` parameter, and the default is
        english.
        """
        env = env if env is not None else os.environ.copy()
        if self.KEYS["LOCALE_KEY"] not in env:
            env.update(self._get_locale_env())
        cmds = shlex.split(command)
        logger.debug(f"Running shell command '{command}'")
        res = subprocess.run(
            cmds,
            stdout=stdout,
            stderr=stderr,
            timeout=timeout,
            env=env,
            check=check,
            shell=shell,
            text=text,
        )
        logger.debug(f"Got result {res}")
        return res

    def _get_locale_env(self) -> dict[str, str]:
        _map = {
            Locales.english: "en_US",
            Locales.italian: "it_IT",
        }
        return {self.KEYS["LOCALE_KEY"]: _map[self.locale]}


_default_shell = Shell()
locale = _default_shell.locale
run = _default_shell.run


def set_locale(locale_: str) -> None:
    """
    Set the locale of the default shell.
    """
    logger.debug(f"Setting locale to {locale_}")
    lc = Locales[locale_]
    _default_shell.locale = lc
