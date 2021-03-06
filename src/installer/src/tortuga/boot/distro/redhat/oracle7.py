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
from typing import Dict
from .base import RedHatFamily, RedHatFamilyPrimitives


class Oracle7Primitives(RedHatFamilyPrimitives):
    """
    Represent locations of needed primitives
    from the Oracle 7 distributions.
    """
    def __new__(cls) -> Dict[str, str]:
        """
        :return: None
        """
        return super(Oracle7Primitives, cls).__new__(cls, rpm_gpg_key='RPM-GPG-KEY-oracle')


class Oracle7(RedHatFamily):
    """
    Represents a Oracle 7 distribution.
    """
    __abstract__: bool = False

    def __init__(self, source_path: str, architecture: str = 'x86_64') -> None:
        """
        :param source_path: String local path or remote uri
        :param architecture: String targeted architecture
        :returns: None
        """
        super(Oracle7, self).__init__(
            source_path,
            'oracle',
            7,
            0,
            architecture
        )

        self._primitives: Oracle7Primitives = Oracle7Primitives()

    @property
    def release_package(self) -> str:
        """
        :return: String
        """
        return 'oraclelinux-release'
