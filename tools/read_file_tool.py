import base64
from pathlib import Path
from tools.abstract_tool import AbstractTool
from paths import is_safe_path


class ReadFileTool(AbstractTool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Read the contents of a file. "
            "Returns text directly for text files and base64 for binary files."
        )

    def get_parameters_schema(self) -> dict:
        return {
            "file_path": {"type": "string", "description": "Path of the file to read"}
        }

    def execute(self, **kwargs) -> str:
        file_path = kwargs.get("file_path")

        if not file_path:
            return "Error: file_path required"
        if is_safe_path(file_path):
            try:
                path = Path(file_path)

                if not path.exists():
                    return f"Error: File '{file_path}' not found"

                with open(path, "rb") as f:
                    data = f.read()

                # try decode as text
                try:
                    return data.decode("utf-8")
                except UnicodeDecodeError:
                    return base64.b64encode(data).decode("utf-8")

            except Exception as e:
                return f"Error reading file: {str(e)}"
        else:
            return f"You don't have permission to read file at {file_path}"
