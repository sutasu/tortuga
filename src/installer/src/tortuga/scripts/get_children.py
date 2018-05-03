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

# pylint: disable=no-member

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.node.nodeApiFactory import getNodeApi
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest


class GetChildrenCli(TortugaCli):
    """
    Get the idle children of a software profile
    """

    def __init__(self):
        TortugaCli.__init__(self)


    def parseArgs(self, usage=None):
        softwareProfileAttrGroup = _('Idle Children Attribute Options')

        self.addOptionGroup(
            softwareProfileAttrGroup,
            _('Software Profile name must be specified.'))

        self.addOptionToGroup(softwareProfileAttrGroup, '--node',
                              metavar='NAME', required=True,
                              dest='nodeName', help=_('node name'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Returns all nodes that have the given node as a parent.
"""))
        nodeName = self.getArgs().nodeName

        napi = getNodeApi(self.getUsername(), self.getPassword())

        nodeList = napi.getChildrenList(nodeName)

        if not nodeList:
            raise SystemExit(1)

        print('\n'.join([node.getName() for node in nodeList]))


def main():
    GetChildrenCli().run()
