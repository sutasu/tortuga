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

from tortuga.kit.installer import ComponentInstallerBase


class ComponentInstaller(ComponentInstallerBase):
    name = 'core'
    version = '7.1.0'
    os_list = [
        {'family': 'rhel', 'version': '6', 'arch': 'x86_64'},
        {'family': 'rhel', 'version': '7', 'arch': 'x86_64'},
    ]

    compute_only = True

    def action_get_puppet_args(self, db_software_profile,
                               db_hardware_profile, *args, **kwargs):

        if self.kit_installer.config_manager.is_offline_installation():
            return {
                'offline_installation': True,
            }

        return {}
