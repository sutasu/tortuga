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

import os
from typing import List

from celery import Celery
from celery.contrib.testing.app import TestApp

from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_all_kit_installers


#
# This environment variable is set by the test runner (in our case tox
# through tox.ini). When it is set, it allows us to use a test version of
# the Celery app that does not depend on an external broker.
#
if 'TORTUGA_TEST' in os.environ:
    app = TestApp(
        include=[
            'tortuga.events.tasks',
            'tortuga.resourceAdapter.tasks',
        ]
    )

#
# In regular mode, we also want to load the kits, and include any tasks
# they may have as well.
#
else:
    load_kits()
    kits_task_modules: List[str] = []
    for kit_installer in get_all_kit_installers():
        kits_task_modules += kit_installer.task_modules

    app = Celery(
        'tortuga.tasks.queue',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=[
            'tortuga.events.tasks',
            'tortuga.resourceAdapter.tasks',
        ] + kits_task_modules
    )


if __name__ == '__main__':
    app.start()
