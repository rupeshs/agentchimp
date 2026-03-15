from config import WORKSPACE_DIRECTORY
from pathlib import Path
from constants import SHORT_TERM_MEMORY_FILE, SOUL_FILE, AGENT_FILE
import sys
from os.path import dirname, abspath


def get_application_path() -> str:
    if getattr(sys, "frozen", False):
        application_path = dirname(sys.executable)
    else:
        application_path = dirname(abspath(__file__))

    return application_path


def get_short_term_memory_file_path() -> Path:
    if WORKSPACE_DIRECTORY.lower() == "workspace":
        return get_application_path() / Path(f"workspace/{SHORT_TERM_MEMORY_FILE}")
    return Path(WORKSPACE_DIRECTORY) / SHORT_TERM_MEMORY_FILE


def get_workspace_path() -> Path:
    if WORKSPACE_DIRECTORY.lower() == "workspace":
        return get_application_path() / Path("workspace")
    return Path(WORKSPACE_DIRECTORY)


def get_agent_file_path() -> Path:
    return get_workspace_path() / AGENT_FILE


def get_soul_file_path() -> Path:
    return get_workspace_path() / SOUL_FILE


def get_output_path() -> Path:
    output_path = get_workspace_path() / "output"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def is_safe_path(user_path: str) -> bool:
    workspace = get_workspace_path().resolve()
    path = Path(user_path)

    # If relative → attach to workspace
    if not path.is_absolute():
        path = workspace / path

    target = path.resolve()

    return workspace in target.parents or target == workspace
