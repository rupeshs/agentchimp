import os
from importlib.util import module_from_spec, spec_from_file_location

from paths import get_application_path
from tools.abstract_tool import AbstractTool

TOOLS_DIR = os.path.join(get_application_path(), "tools")


def load_tools() -> dict[str, AbstractTool]:
    tool_instances = {}

    for filename in os.listdir(TOOLS_DIR):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue

        module_path = os.path.join(TOOLS_DIR, filename)
        module_name = filename[:-3]

        spec = spec_from_file_location(module_name, module_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        # Find all subclasses of AbstractTool in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, AbstractTool)
                and attr is not AbstractTool
            ):
                tool_instance = attr()  # instantiate
                tool_instances[tool_instance.name] = tool_instance

    return tool_instances
