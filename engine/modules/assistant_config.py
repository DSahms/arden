import os
import yaml
from dpath import util as dpath_util

from modules.arden_env import get as arden_get

DEFAULT_CONFIG_PATH = arden_get("CONFIG", "assistant_config.yml")


_MISSING = object()  # Sentinel for missing default


def get_config(dot_path_key: str, config_path: str = DEFAULT_CONFIG_PATH, default=_MISSING):
    """
    Load a field from the YAML config file using dot notation path.

    Args:
        dot_path_key: The key path to look up in the config (e.g. 'parent.child.key')
        config_path: Path to the YAML config file, defaults to assistant_config.yml
        default: Default value to return if key not found. If not provided, raises KeyError.

    Returns:
        The value for the requested key path, or default if provided and key not found

    Raises:
        FileNotFoundError: If config file doesn't exist
        KeyError: If key path not found in config and no default provided
    """
    config_override = arden_get("CONFIG")
    if config_path == DEFAULT_CONFIG_PATH and config_override:
        config_path = config_override

    if os.path.isabs(config_path):
        abs_config_path = config_path
    else:
        abs_config_path = os.path.join(os.getcwd(), config_path)

    if not os.path.exists(abs_config_path):
        if default is not _MISSING:
            return default
        raise FileNotFoundError(f"Config file not found at {abs_config_path}")

    with open(abs_config_path) as f:
        config = yaml.safe_load(f)

    try:
        return dpath_util.get(config, dot_path_key, separator=".")
    except KeyError:
        if default is not _MISSING:
            return default
        raise KeyError(f"Key path '{dot_path_key}' not found in config")


def get_config_file(config_path: str = DEFAULT_CONFIG_PATH) -> str:
    """
    Get the config file as a string.
    """
    with open(config_path, "r") as f:
        return f.read()
