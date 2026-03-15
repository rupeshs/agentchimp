# Implementation as per Agent Skills Specification
# https://agentskills.io/client-implementation/adding-skills-support

import xml.etree.ElementTree as ET
from pathlib import Path

from frontmatter import load
from loguru import logger


class Skills:
    def __init__(
        self,
        skills_root_folder: str,
    ):
        self.skill_root_folder = Path(skills_root_folder)
        self.valid_skills = []
        self._discover_skills()
        self.skill_map = {}

    def _discover_skills(self):
        directories = [p for p in self.skill_root_folder.iterdir() if p.is_dir()]
        for directory in directories:
            skill_md_file = directory / "SKILL.md"
            if skill_md_file.exists():
                self.valid_skills.append(directory)

    def _load_skills(self) -> dict:
        for skill in self.valid_skills:
            skill_md_file = skill / "SKILL.md"
            skill_data = load(skill_md_file)

            if skill_data.metadata:
                if not skill_data.metadata.get("name"):
                    logger.warning(f"No name in SKILL.md file :{skill_md_file}")
                    continue
                if not skill_data.metadata.get("description"):
                    logger.warning(f"No description in SKILL.md file :{skill_md_file}")
                    continue

                self.skill_map[skill_data.metadata.get("name")] = {
                    "name": skill_data.metadata.get("name"),
                    "description": skill_data.metadata.get("description"),
                    "location": str(skill_md_file),
                }
            else:
                logger.warning(f"Invalid SKILL.md file:{skill_md_file}")

    def get_skill_catalog(self) -> str:
        self._load_skills()
        if not self.skill_map:
            return ""
        root = ET.Element("available_skills")
        for _, skill in self.skill_map.items():
            el = ET.SubElement(root, "skill")
            ET.SubElement(el, "name").text = skill.get("name")
            ET.SubElement(el, "description").text = skill.get("description")
            ET.SubElement(el, "location").text = skill.get("location")

        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode")

    def get_skills(self) -> dict:
        if not self.skill_map:
            self._load_skills()
        return self.skill_map
