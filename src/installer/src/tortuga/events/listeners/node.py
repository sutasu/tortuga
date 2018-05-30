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

from .base import BaseListener
from ..types import NodeStateChanged


class NodeProvisioningListener(BaseListener):
    """
    The purpose of this event listener is to listen for events where the
    node state has changed to "Provisioned", wait for 10 minutes, then
    check if the node is in the "Installed" state. If it is not in the
    "Installed" state, then it is assumed that the node has a problem, and
    thus it's state is changed to "Unresponsive".

    """
    event_types = [NodeStateChanged]
    countdown = 600  # 10 minutes

    @classmethod
    def should_run(cls, event: NodeStateChanged):
        if not super().should_run(event):
            return False

        #
        # This listener should only run if the node state is
        # provisioned
        #
        return event.node['state'] == 'Provisioned'

    def run(self, event: NodeStateChanged):
        from tortuga.node.nodeManager import NodeManager

        manager: NodeManager = NodeManager()
        node = manager.getNodeById(event.node['id'])

        if node.getState() != NodeManager.NODE_STATE_INSTALLED:
            manager.updateNodeStatus(node.getName(),
                                     NodeManager.NODE_STATE_UNRESPONSIVE)
