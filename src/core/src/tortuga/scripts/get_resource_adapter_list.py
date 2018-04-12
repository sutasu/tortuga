#!/usr/bin/env python

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

import yaml

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.resourceAdapterWsApi import ResourceAdapterWsApi


class GetResourceAdapterListCli(TortugaCli):
    def __init__(self):
        super().__init__()
        self.addOption(
            '--settings',
            action='store_true',
            default=False,
            dest='show_settings',
            help='Show available settings for each resource adapter'
        )

    def runCommand(self):
        self.parseArgs()

        api = ResourceAdapterWsApi(
                username=self.getUsername(),
                password=self.getPassword(),
                baseurl=self.getUrl())

        output = []

        for ra in api.getResourceAdapterList():
            data = {
                'name': ra['name']
            }
            if self.getArgs().show_settings:
                data['settings'] = ra['settings']
            output.append(data)

        print(yaml.safe_dump(output))


def main():
    GetResourceAdapterListCli().run()
