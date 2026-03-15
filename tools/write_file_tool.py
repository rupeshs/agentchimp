from pathlib import Path
from tools.abstract_tool import AbstractTool
from paths import get_output_path, is_safe_path


class WriteFileTool(AbstractTool):
    """Tool to write content to a file."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write text content to a file. Creates the file if it does not exist."

    def get_parameters_schema(self) -> dict:
        return {
            "path": {
                "type": "string",
                "description": "Relative path of the file to write",
            },
            "content": {
                "type": "string",
                "description": "Text content to write into the file",
            },
        }

    def execute(self, **kwargs) -> str:
        try:
            path = kwargs.get("path")
            content = kwargs.get("content")

            if is_safe_path(path):
                if not path:
                    return "Error: file path is required"

                file_path = get_output_path() / Path(path)

                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                return f"File written successfully: {file_path}"
            else:
                return f"You don't have permission to write file at {path}"

        except Exception as e:
            return f"Error writing file: {str(e)}"
