
from jidouteki.spec.website import Website

import yaml
from pathlib import Path
from typing import List

class Jidouteki():
    def __init__(self, proxy: None) -> None:
        self.proxy = proxy
    
    def load(self, path) -> Website:
        """Load YAML config from given path

        Args:
            path (str): The path to the config file.

        Returns:
            Website: The loaded config file.
        """
        
        # Parse yaml file
        obj = None    
        with open(path, "r") as f:
            obj = yaml.safe_load(f.read())
        return Website(arglist=obj, _context=self)
    
    def load_all(self, path: str | Path, exclude=["_", "."]) -> List[Website]:
        """Load YAML configs from folder
        
        Args:
            path (str | Path): The path to the config folder.
            exclude (List[str]): Exclude files starting with specified strings.
            
        Returns:
            List[Website]: List of all loaded config files
        """
        websites = []
        for item in Path(path).iterdir():
            if item.is_file() and item.suffix in [".yaml", ".yml"]:
                if not any(item.name.startswith(c) for c in exclude):
                    websites.append(self.load(item.resolve()))
        return websites