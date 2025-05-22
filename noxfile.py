"""Nox file to run all utils at once."""

from __future__ import annotations

import nox
from nox.sessions import Session

TEST_DIR = "tests"
COVERAGE_FILE = ".coverage"

PACKAGE = "interpolation"

nox.options.sessions = ["format", "lint", "tests", "typechecks"]

LOCATIONS = [
    PACKAGE,
    "tests",
    "noxfile.py",
]


# Common dependencies for all sessions
def install_with_poetry(session: Session, *args: str) -> None:
    """Run poetry install."""
    session.run("poetry", "install", "--no-interaction", "--only", "main", external=True)
    if args:
        session.run("poetry", "add", "--no-interaction", *args, external=True)


@nox.session(python="3.11")
def format(session: Session) -> None:
    """Format codestyle Ruff."""
    install_with_poetry(session, "ruff")
    session.run("ruff", "format", *LOCATIONS)


@nox.session(python="3.11")
def lint(session: Session) -> None:
    """Check codestyle Ruff."""
    install_with_poetry(session, "ruff")
    session.run("ruff", "check", "--fix", *LOCATIONS)


@nox.session(python="3.11")
def tests(session: Session) -> None:
    """Run pytest tests."""
    install_with_poetry(session, "pytest", "pytest-cov")
    session.run(
        "pytest",
        TEST_DIR,
        f"--cov={PACKAGE}",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
        env={"COVERAGE_FILE": COVERAGE_FILE},
    )


@nox.session(python="3.11")
def coverage_report(session: Session) -> None:
    """Create tests report."""
    install_with_poetry(session, "coverage[toml]")
    session.run("coverage", "report", "-m")
    session.run("coverage", "html", "-d", "htmlcov")


@nox.session(python="3.11")
def typechecks(session: Session) -> None:
    """Typecheck using mypy."""
    install_with_poetry(session, "mypy")
    session.run("mypy", "--explicit-package-bases", PACKAGE)
