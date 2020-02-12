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

from abc import ABC, abstractmethod
import os.path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from tortuga.db.models.node import Node
from tortuga.exceptions.configurationError import ConfigurationError


class UserDataMixin(ABC): \
        # pylint: disable=too-few-public-methods
    """
    Common methods used to process user-data for cloud instances. Currently
    only used by AWS resource adapter.

    Raises:
        ConfigurationError
    """

    def expand_cloud_init_user_data_template(
            self, configDict: dict,
            node: Optional[Node] = None,
            template=None) -> str:
        """
        Return cloud-init script template

        Raises:
            ConfigurationError
        """

        if 'cloud_init_script_template' not in configDict:
            raise ConfigurationError('cloud-init script template not defined')

        if template is None:
            srcpath, srcfile = os.path.split(
                configDict['cloud_init_script_template'])

            env = Environment(loader=FileSystemLoader(srcpath))

            template_ = env.get_template(srcfile)
        else:
            template_ = template

        tmpl_vars = {
            'installer': self.installer_public_hostname,
            'installer_ip_address': self.installer_public_ipaddress,
            'override_dns_domain': configDict.get('override_dns_domain',
                                                  False),
            'dns_domain': configDict.get('dns_domain', ''),
        }

        if node:
            tmpl_vars['fqdn'] = node.name

        return template_.render(tmpl_vars)

    @abstractmethod
    def generate_startup_script(self, config: dict,
                                node: Optional[Node] = None,
                                insertnode_request: Optional[bytes] = None) \
            -> str:
        """
        Build a node/instance-specific startup script that will initialize
        VPN, install Puppet, and bootstrap the instance.

        :param configDict: resource adapter configuration settings
        :param node: Node instance, optional
        :param insertnode_request: encrypted insertnode_request, optional

        :return: full startup script as a `str`
        """
        pass
