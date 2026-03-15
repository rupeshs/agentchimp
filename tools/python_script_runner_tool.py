import subprocess
import os
from tools.abstract_tool import AbstractTool
import sys
from loguru import logger


# Track skills that have already had their venv set up this session
_installed_skills: set[str] = set()


class ScriptRunnerTool(AbstractTool):
    @property
    def name(self) -> str:
        return "run_python_script"

    @property
    def description(self) -> str:
        return (
            "Executes a skill's Python script inside its own uv-managed venv. "
            "Use this when a skill's SKILL.md instructs you to call run_script. "
            "Automatically creates venv and installs dependencies from "
            "requirements.txt or pyproject.toml if present."
        )

    def get_parameters_schema(self) -> dict:
        return {
            "script_path": {
                "type": "string",
                "description": "Absolute path to the Python script to run.",
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of CLI arguments e.g. ['--city', 'Mumbai']",
            },
        }

    def execute(self, **kwargs) -> str:
        script_path: str = kwargs.get("script_path", "")
        args: list[str] = kwargs.get("args", [])
        logger.info(f"\nRunning script {script_path} with args {args}")

        if not script_path:
            return "Error: script_path is required."

        if not os.path.exists(script_path):
            return f"Error: script not found at {script_path}"

        if not os.path.isfile(script_path):
            return f"Error: script not found at {script_path}"

        skill_dir = os.path.dirname(os.path.abspath(script_path))

        # Resolve the venv python path for this skill
        venv_python = self._ensure_venv(skill_dir)
        if venv_python is None:
            if sys.platform == "win32":
                venv_python = "python"
            else:
                venv_python = "python3"

        result = subprocess.run(
            [venv_python, script_path, *args],
            capture_output=True,
            text=True,
            cwd=skill_dir,
        )

        if result.returncode != 0:
            return f"Error (exit {result.returncode}): {result.stderr.strip()}"

        return result.stdout.strip()

    def _ensure_venv(self, skill_dir: str) -> str | None:
        """
        Creates a uv venv and installs dependencies if requirements.txt or
        pyproject.toml is present. Returns path to venv python, or None if
        no dependency file found.
        """
        global _installed_skills

        has_requirements = os.path.exists(os.path.join(skill_dir, "requirements.txt"))
        has_pyproject = os.path.exists(os.path.join(skill_dir, "pyproject.toml"))

        if not has_requirements and not has_pyproject:
            return None

        venv_dir = os.path.join(skill_dir, ".venv")

        # OS-aware venv python path
        if sys.platform == "win32":
            venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(venv_dir, "bin", "python")

        # Already set up this session — just return the python path
        if skill_dir in _installed_skills:
            return venv_python

        # Create venv with uv if it doesn't exist
        if not os.path.exists(venv_dir):
            logger.info(f"[ScriptRunnerTool] Creating venv for {skill_dir}")
            result = subprocess.run(
                ["uv", "venv", ".venv"],
                capture_output=True,
                text=True,
                cwd=skill_dir,
            )
            if result.returncode != 0:
                logger.error(
                    f"[ScriptRunnerTool] Warning: uv venv failed: {result.stderr.strip()}"
                )
                return None

        # Set VIRTUAL_ENV so uv pip install targets the correct venv
        # This is more reliable than --python flag
        venv_env = {**os.environ, "VIRTUAL_ENV": venv_dir}

        # Install dependencies into the venv
        if has_requirements:
            logger.info(
                f"[ScriptRunnerTool] Installing requirements.txt for {skill_dir}"
            )
            result = subprocess.run(
                ["uv", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
                cwd=skill_dir,
                env=venv_env,
            )
        elif has_pyproject:
            logger.info(f"[ScriptRunnerTool] Installing pyproject.toml for {skill_dir}")
            result = subprocess.run(
                ["uv", "pip", "install", "."],
                capture_output=True,
                text=True,
                cwd=skill_dir,
                env=venv_env,
            )

        if result.returncode != 0:
            logger.warning(
                f"[ScriptRunnerTool] Warning: dep install failed: {result.stderr.strip()}"
            )
            return None

        _installed_skills.add(skill_dir)
        return venv_python
