import configparser
import os

from {{cookiecutter.project_slug}}.lib.collections import update

LOCAL_SETTINGS_PATH = '../../local-settings.ini'
UPDATE_RECURSION_EXCLUDED = ['formatter_generic']
settings = dict()


def init_settings(settings_):
    global settings
    updated_settings = update(settings, _get_local_config(),
                              UPDATE_RECURSION_EXCLUDED)
    updated_settings = update(updated_settings, settings_,
                              UPDATE_RECURSION_EXCLUDED)
    settings = updated_settings


def _get_local_config():
    here = os.path.dirname(__file__)
    return read_config(os.path.join(here, LOCAL_SETTINGS_PATH))


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config
