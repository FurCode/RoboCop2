import sys

# check python version
if sys.version_info < (3, 4, 0):
    print("RoboCop 2 requires Py3.4 or newer, use Classic RoboCop for Python 2.x")
    sys.exit(1)

import json
import logging.config
import logging
import os

__version__ = "2.0.0-production"

__all__ = ["util", "bot", "connection", "config", "permissions", "plugin", "event", "hook", "dev_mode", "log_dir"]


def _setup():
    default_developer_mode = {"plugin_reloading": False, "config_reloading": True,
                              "console_debug": False, "file_debug": True}
    if os.path.exists(os.path.abspath("config.json")):
        with open(os.path.abspath("config.json")) as config_file:
            json_conf = json.load(config_file)
        developer_mode = json_conf.get("developer_mode", default_developer_mode)
    else:
        developer_mode = default_developer_mode

    if "config_reloading" not in developer_mode:
        developer_mode["config_reloading"] = default_developer_mode["config_reloading"]
    if "plugin_reloading" not in developer_mode:
        developer_mode["plugin_reloading"] = default_developer_mode["plugin_reloading"]
    if "console_debug" not in developer_mode:
        developer_mode["console_debug"] = default_developer_mode["console_debug"]
    if "file_debug" not in developer_mode:
        developer_mode["file_debug"] = default_developer_mode["file_debug"]

    global log_dir
    log_dir = os.path.join(os.path.abspath(os.path.curdir), "logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    dict_config = {
        "version": 1,
        "formatters": {
            "brief": {
                "format": "[%(asctime)s] [%(levelname)s] %(message)s",
                "datefmt": "%H:%M:%S"
            },
            "full": {
                "format": "[%(asctime)s] [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d][%H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief",
                "level": "INFO",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "full",
                "level": "INFO",
                "encoding": "utf-8",
                "filename": os.path.join(log_dir, "bot.log")
            }
        },
        "loggers": {
            "cloudbot": {
                "level": "DEBUG",
                "handlers": ["console", "file"]
            }
        }
    }

    if developer_mode["console_debug"]:
        dict_config["handlers"]["console"]["level"] = "DEBUG"

    if developer_mode["file_debug"]:
        dict_config["handlers"]["debug_file"] = {
            "class": "logging.FileHandler",
            "formatter": "full",
            "encoding": "utf-8",
            "level": "DEBUG",
            "filename": os.path.join(log_dir, "debug.log")
        }
        dict_config["loggers"]["cloudbot"]["handlers"].append("debug_file")

    logging.config.dictConfig(dict_config)

    return developer_mode


dev_mode = _setup()
