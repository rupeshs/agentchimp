import os
from typing import Dict

from paths import get_workspace_path
from skills.skills import Skills
from tools.abstract_tool import AbstractTool


class ActivateSkillTool(AbstractTool):
    """Activate a skill and return its SKILL.md contents."""

    def __init__(
        self,
    ):
        skills = Skills(get_workspace_path() / "skills")
        self.skills = skills.get_skills()

    @property
    def name(self) -> str:
        return "activate_skill"

    @property
    def description(self) -> str:
        return (
            "Activate a skill by skill name "
            "Returns the SKILL.md instructions so the agent can follow them."
        )

    def get_parameters_schema(self) -> Dict:
        return {
            "skill_name": {
                "type": "string",
                "description": "Name of the skill to activate (from available_skills list)",
            }
        }

    def execute(self, **kwargs) -> str:
        skill_name = kwargs.get("skill_name")

        if not skill_name:
            return "Error: skill_name parameter is required."

        skill_path = self.skills.get(skill_name, {}).get("location")

        if not os.path.exists(skill_path):
            return f"Error: Skill '{skill_path}' not found."

        try:
            with open(skill_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading skill: {str(e)}"

        return content
