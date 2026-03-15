from pathlib import Path
from tools.abstract_tool import AbstractTool


class ListFilesTool(AbstractTool):
    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List files inside a folder. Optionally filter by extension."

    def get_parameters_schema(self) -> dict:
        return {
            "path": {"type": "string", "description": "Folder path to list files from"},
            "extension": {
                "type": "string",
                "description": "Optional file extension filter like .yaml or .txt",
            },
        }

    def execute(self, **kwargs) -> str:
        path = kwargs.get("path")
        extension = kwargs.get("extension")

        folder = Path(path)

        if not folder.exists():
            return f"Error: folder does not exist: {path}"

        if not folder.is_dir():
            return f"Error: path is not a directory: {path}"

        files = []

        for item in folder.iterdir():
            if item.is_file():
                if extension and not item.name.endswith(extension):
                    continue

                files.append(item.name)

        if not files:
            return "No files found."

        return "\n".join(files)
