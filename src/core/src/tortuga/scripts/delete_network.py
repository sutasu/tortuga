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

from tortuga.network.networkCli import NetworkCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.networkInUse import NetworkInUse
from tortuga.exceptions.deleteNetworkFailed import DeleteNetworkFailed


class DeleteNetworkCli(NetworkCli):
    """
    Delete network command line interface.
    """

    def parseArgs(self, usage=None):
        # The delete command can take only the network option
        self.addOption('--network',
                       dest='network', required=True,
                       help=_('Network identifier (ADDRESS/NETMASK)'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Remove network from the system'))

        # Parse --network argument if it exists
        networkAddress, networkSubnet = self.parseNetworkParameter(
            self.getArgs().network)

        # If we don't have a network and a netmask its an error
        if networkAddress is not None and networkSubnet is not None:
            network = self.getNetworkApi().getNetwork(
                networkAddress, networkSubnet)
        else:
            raise InvalidCliRequest(
                _('--network argument must be specified.'))

        # Delete the network
        try:
            self.getNetworkApi().deleteNetwork(network.getId())
        except DeleteNetworkFailed as ex:
            raise NetworkInUse(
                _('Unable to delete network [{0}].\nReason: {1}').format(
                    network, ex))
        except NetworkInUse:
            raise NetworkInUse(
                _('Network [{0}] contains nodes.  It cannot be'
                  ' deleted.').format(network))


def main():
    DeleteNetworkCli().run()
