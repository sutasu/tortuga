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

import pytest

from tortuga.db.resourceAdapterConfigDbHandler import \
    ResourceAdapterConfigDbHandler
from tortuga.exceptions.resourceAdapterNotFound import ResourceAdapterNotFound
from tortuga.exceptions.resourceNotFound import ResourceNotFound


def test_get(dbm):
    """
    Get 'default' resource adapter configuration for resource adapter 'aws'
    """

    with dbm.session() as session:
        result = ResourceAdapterConfigDbHandler().get(
            session, 'aws', 'default')

        assert result


def test_get_failed(dbm):
    with dbm.session() as session:
        with pytest.raises(ResourceNotFound):
            ResourceAdapterConfigDbHandler().get(
                session, 'nonexistent', 'default')


def test_get_profile_names(dbm):
    with dbm.session() as session:
        result = ResourceAdapterConfigDbHandler().get_profile_names(
            session, 'aws'
        )

        assert isinstance(result, list) and 'default' in result


def test_get_profile_names_failed(dbm):
    with dbm.session() as session:
        with pytest.raises(ResourceAdapterNotFound):
            ResourceAdapterConfigDbHandler().get_profile_names(
                session, 'nonexistent'
            )
