# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
from typing import Any, Dict, List, Optional

import yaml

from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.objects.osInfo import OsInfo


class ParseOperatingSystemArgAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        osValues = values.split('-', 3)

        if len(osValues) != 3:
            raise InvalidCliRequest(
                _('Error: Incorrect operating system specification.'
                  '\n\n--os argument should be in'
                  ' OSNAME-OSVERSION-OSARCH format'))

        name = osValues[0]
        version = osValues[1]
        arch = osValues[2]

        setattr(namespace, 'osInfo', OsInfo(name, version, arch))


class FilterTagsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        tags = {}
        vals = values.split('=', 1)

        if len(vals) == 2:
            tags[vals[0]] = vals[1]

        else:
            tags[vals[0]] = None

        current_tags = getattr(namespace, self.dest) \
            if hasattr(namespace, self.dest) else None

        if current_tags is None:
            setattr(namespace, self.dest, tags)

        else:
            current_tags.update(tags)


def parse_tags(string_list: List[str]) -> Dict[str, str]:
    """
    Parses a list of strings into a dict of tags.

    :param string_list: a list of strings, each in the form of
                        key=value[,key=value...]

    :return: a dictionary of tags

    """
    result = {}

    for string in string_list:
        for tag_list in string.split(','):
            try:
                key, value = tag_list.split('=', 1)
                result[key] = value

            except ValueError:
                raise Exception('Malformed tags')

    return result


def pretty_print(data: Any, fmt: Optional[str] = None) -> None:
    """
    Outputs data in specified format (default is nicely formatted YAML).
    'json' is currently the only non-default supported format.

    :param Any data:          a Python data structure
    :param Optional[str] fmt: the output format

    """
    if fmt and fmt == 'json':
        print(json.dumps(data, indent=2))

        return

    # fallback to default
    print(yaml.safe_dump(data, default_flow_style=False))
