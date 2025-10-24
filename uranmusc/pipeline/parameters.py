from pathlib import Path
from typing import Optional

import luigi
import yaml
from pydantic import BaseModel

from uranmusc.config_parser import Config


def load_config(path_: str):
    path = Path(path_)
    if not path.exists():
        raise ValueError(f"The config file {path} does not exist.")

    with open(path, encoding="utf-8") as config_file:
        config = Config(**yaml.safe_load(config_file))
    return config


class PydanticModelParameter(luigi.Parameter):
    def __init__(self, default: Optional[str] = None, **kwargs):
        """Initialize class

        Args:
            exists (bool, optional): Whether to chech that the config file exists.
                Defaults to False.
        """
        super().__init__(**kwargs)
        self._default = load_config(default)

    def parse(self, x: str) -> Config:
        return load_config(x)

    def serialize(self, x: BaseModel | str) -> str:
        # if isinstance(x, str):
        #     return str(load_config(x).model_dump(mode="json"))
        return str(x.model_dump(mode="json"))
