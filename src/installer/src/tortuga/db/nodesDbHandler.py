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

# pylint: disable=not-callable,no-member,multiple-statements,no-self-use

from typing import Dict, List, NoReturn, Optional, Tuple, Union

from sqlalchemy import and_, func, or_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.nicsDbHandler import NicsDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.softwareUsesHardwareDbHandler import \
    SoftwareUsesHardwareDbHandler
from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.events.types import NodeStateChanged
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.operationFailed import OperationFailed
from tortuga.objects.node import Node as TortugaNode
from tortuga.resourceAdapter import resourceAdapterFactory

from .models.hardwareProfile import HardwareProfile
from .models.nic import Nic
from .models.node import Node
from .models.softwareProfile import SoftwareProfile

Tags = List[Tuple[str, str]]


class NodesDbHandler(TortugaDbObjectHandler):
    """
    This class handles nodes table.
    """

    def __init__(self):
        TortugaDbObjectHandler.__init__(self)

        self._softwareProfilesDbHandler = SoftwareProfilesDbHandler()

    def getNode(self, session: Session, name: str) -> Node:
        """
        Return node.

        Raises:
            NodeNotFound
        """

        try:
            if '.' in name:
                # Attempt exact match on fully-qualfied name
                return session.query(Node).filter(
                    func.lower(Node.name) == name.lower()).one()

            # 'name' is short host name; attempt to match on either short
            # host name or any host starting with same host name
            return session.query(Node).filter(
                or_(func.lower(Node.name) == name.lower(),
                    func.lower(Node.name).like(name.lower() + '.%'))).one()
        except NoResultFound:
            raise NodeNotFound("Node [%s] not found" % (name))

    def getNodesByTags(self, session: Session,
                       tags: Optional[Tags] = None):
        """'tags' is a list of (key, value) tuples representing tags.
        tuple may also contain only one element (key,)
        """

        searchspec = []

        # iterate over list of tag tuples making SQLAlchemy search
        # specification
        for tag in tags:
            if len(tag) == 2:
                # Match tag 'name' and 'value'
                searchspec.append(and_(Node.tags.any(name=tag[0]),
                                       Node.tags.any(value=tag[1])))
            else:
                # Match tag 'name' only
                searchspec.append(Node.tags.any(name=tag[0]))

        return session.query(Node).filter(or_(*searchspec)).all()

    def getNodesByAddHostSession(self, session: Session, ahSession: str) \
            -> List[Node]:
        """
        Get nodes by add host session
        Returns a list of nodes
        """

        self.getLogger().debug(
            'getNodesByAddHostSession(): ahSession [%s]' % (ahSession))

        return session.query(Node).filter(
            Node.addHostSession == ahSession).order_by(Node.name).all()

    def getNodesByNameFilter(self, session: Session,
                             filter_spec: Union[str, list]) -> List[Node]:
        """
        Filter follows SQL "LIKE" semantics (ie. "something%")

        Returns a list of Node
        """

        filter_spec_list = [filter_spec] \
            if not isinstance(filter_spec, list) else filter_spec

        node_filter = []

        for filter_spec_item in filter_spec_list:
            if '.' not in filter_spec_item:
                # Match exactly (ie. "hostname-01")
                node_filter.append(Node.name.like(filter_spec_item))

                # Match host name only (ie. "hostname-01.%")
                node_filter.append(Node.name.like(filter_spec_item + '.%'))

                continue

            # Match fully-qualified node names exactly
            # (ie. "hostname-01.domain")
            node_filter.append(Node.name.like(filter_spec_item))

        return session.query(Node).filter(or_(*node_filter)).all()

    def getNodeById(self, session: Session, _id: int) -> Node:
        """
        Return node.

        Raises:
            NodeNotFound
        """

        self.getLogger().debug('Retrieving node by ID [%s]' % (_id))

        dbNode = session.query(Node).get(_id)

        if not dbNode:
            raise NodeNotFound('Node ID [%s] not found.' % (_id))

        return dbNode

    def getNodeByIp(self, session: Session, ip: str) -> Node:
        """
        Raises:
            NodeNotFound
        """

        self.getLogger().debug('Retrieving node by IP [%s]' % (ip))

        try:
            return session.query(Node).join(Nic).filter(Nic.ip == ip).one()
        except NoResultFound:
            raise NodeNotFound(
                'Node with IP address [%s] not found.' % (ip))

    def getNodeList(self, session: Session,
                    softwareProfile: Optional[str] = None,
                    tags: Tags = None) -> List[Node]:
        """
        Get sorted list of nodes from the db.

        Raises:
            SoftwareProfileNotFound
        """

        self.getLogger().debug('getNodeList()')

        if softwareProfile:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, softwareProfile)

            return dbSoftwareProfile.nodes

        searchspec = []

        if tags:
            # Build searchspec from specified tags
            for tag in tags:
                if len(tag) == 2:
                    searchspec.append(
                        and_(Node.tags.any(name=tag[0]),
                             Node.tags.any(value=tag[1])))
                else:
                    searchspec.append(Node.tags.any(name=tag[0]))

        return session.query(Node).filter(
            or_(*searchspec)).order_by(Node.name).all()

    def getNodeListByNodeStateAndSoftwareProfileName(
            self, session: Session, nodeState: str,
            softwareProfileName: str) -> List[Node]:
        """
        Get list of nodes from the db.
        """

        self.getLogger().debug(
            'Retrieving nodes with state [%s] from software'
            ' profile [%s]' % (nodeState, softwareProfileName))

        return session.query(Node).join(SoftwareProfile).filter(and_(
            SoftwareProfile.name == softwareProfileName,
            Node.state == nodeState)).all()

    def getNodesByNodeState(self, session: Session, state: str) -> List[Node]:
        return session.query(Node).filter(Node.state == state).all()

    def getNodesByMac(self, session: Session, usedMacList: List[str]) \
            -> List[Node]:
        if not usedMacList:
            return []

        return session.query(Node).join(Nic).filter(
            Nic.mac.in_(usedMacList)).all()

    def build_node_filterspec(self, nodespec):
        filter_spec = []

        for nodespec_token in nodespec.split(','):
            # Convert shell-style wildcards into SQL wildcards
            if '*' in nodespec_token or '?' in nodespec_token:
                filter_spec.append(
                    nodespec_token.replace('*', '%').replace('?', '_'))

                continue

            if '.' not in nodespec_token:
                filter_spec.append(nodespec_token)
                filter_spec.append(nodespec_token + '.%')

                continue

            # Add nodespec "AS IS"
            filter_spec.append(nodespec_token)

        return filter_spec

    def expand_nodespec(self, session: Session, nodespec: str) \
            -> List[Node]:
        return self.getNodesByNameFilter(session, self.build_node_filterspec(nodespec))
