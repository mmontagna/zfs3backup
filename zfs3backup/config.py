import ConfigParser
import os
import os.path

import zfs3backup


_settings = None
_onion_dict_guard = object()


class OnionDict(object):
    """Wrapps multiple dictionaries. Tries to read data from each dict
    in turn.
    Used to implement a fallback mechanism.
    """
    def __init__(self, dictionaries, sections=None):
        self.__dictionaries = dictionaries
        self.__sections = sections or {}

    def _get(self, key, section=None, default=_onion_dict_guard):
        """Try to get the key from each dict in turn.
        If you specify the optional section it looks there first.
        """
        if section is not None:
            section_dict = self.__sections.get(section, {})
            if key in section_dict:
                return section_dict[key]
        for d in self.__dictionaries:
            if key in d:
                return d[key]
        if default is _onion_dict_guard:
            raise KeyError(key)
        else:
            return default

    def __contains__(self, key):
        for d in self.__dictionaries:
            if key in d:
                return True
        return False

    def __getitem__(self, key):
        return self._get(key)

    def get(self, key, default=None, section=None):
        return self._get(key, section=section, default=default)


def get_config():
    global _settings
    if _settings is None:
        _config = ConfigParser.ConfigParser()
        default = os.path.join(zfs3backup.__path__[0], "zfs3backup.conf")
        _config.read(default)
        if os.environ.get('SKIP_CONFIG_FILE', 'false').lower() != 'true':
            _config.read("/etc/zfs3backup_backup/zfs3backup.conf")
        layers = [
            os.environ,  # env variables take precedence
            dict((k.upper(), v) for k, v in _config.items("main")),
        ]
        sections = {}
        for section in _config.sections():
            if section != 'main':
                section_dict = dict(
                    (k.upper(), v)
                    for k, v in _config.items(section)
                )
                sections[section] = section_dict
        _settings = OnionDict(layers, sections)

    return _settings
