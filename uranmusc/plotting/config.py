from pathlib import Path
from typing import Optional

import tomli


class Config:
    """
    Load config.toml and retrieve any config related to a given field
    """

    def __init__(self, config_file, field: str):
        self.config_path = Path(config_file)
        self.field = field
        self.config = None

    def load_config(self):
        """
        Load config.toml file
        """
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, "rb") as f:
            self.config = tomli.load(f)

    def get_section_config(
        self, section="general", sub_path: Optional[str] = None
    ) -> dict:
        """
        Return section config information
        """

        self.load_config()
        section_config = self.config.get(section, {})

        if not section_config:
            raise KeyError(f"Section {section} not found in {self.config_path}")

        if not sub_path:
            return section_config

        result = section_config
        for key in sub_path.split("."):
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                raise KeyError(
                    f"Sub_path {sub_path} not found for section {section}"
                    f" in {self.config_path}"
                )

        return result

    def get_field_config(self, sub_path: Optional[str] = None) -> dict:
        """
        Return config information for field
        """

        self.load_config()
        field_config = self.config.get("field", {}).get(self.field, {})

        if not field_config:
            raise KeyError(
                f"Field {self.field} not found for field {self.field} "
                f"in {self.config_path}"
            )

        if not sub_path:
            return field_config

        result = field_config
        for key in sub_path.split("."):
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                raise KeyError(
                    f"Sub_path {sub_path} not found for field {self.field} "
                    f"in {self.config_path}"
                )

        return result


# more
