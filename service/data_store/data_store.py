# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Reads and writes data from storage."""

import hashlib
import os
import os.path
import time
from typing import List, Optional, Union, Tuple, Type

# pylint: disable=g-bad-import-order
import common.generate_protos  # pylint: disable=unused-import
from data_store import resource_id
import data_store_pb2
from data_store import file_system

# Map resource collection IDs to proto type of the resource.
_PROTO_BY_COLLECTION_ID = {
    'projects': data_store_pb2.Project,
    'brains': data_store_pb2.Brain,
    'snapshots': data_store_pb2.Snapshot,
    'sessions': data_store_pb2.Session,
    'chunks': data_store_pb2.EpisodeChunk,
    'online_evaluations': data_store_pb2.OnlineEvaluation,
    'assignments': data_store_pb2.Assignment,
    'models': data_store_pb2.Model,
    'serialized_models': data_store_pb2.SerializedModel,
    'offline_evaluations': data_store_pb2.OfflineEvaluation,
}

DatastoreProto = Union[
    data_store_pb2.Assignment,
    data_store_pb2.Brain,
    data_store_pb2.EpisodeChunk,
    data_store_pb2.Model,
    data_store_pb2.OfflineEvaluation,
    data_store_pb2.OnlineEvaluation,
    data_store_pb2.Project,
    data_store_pb2.Session,
    data_store_pb2.SerializedModel,
    data_store_pb2.Snapshot,
]


class NotFoundError(Exception):
  """Raised when datastore cannot find a requested object."""
  pass


class InternalError(Exception):
  """Raised when filesystem is not in the expected state."""
  pass


class _FalkenResourceEncoder:
  """Encodes/decodes protos to/from bytes based on resource id."""

  def _get_proto_type(self,
                      res_id: resource_id.ResourceId) -> Type[DatastoreProto]:
    """Determines the protobuf type from a resource id."""
    assert len(res_id.parts) >= 2  # Valid resource ids have at least 2 parts.
    collection_id = res_id.parts[-2]
    try:
      return _PROTO_BY_COLLECTION_ID[collection_id]
    except KeyError:
      raise ValueError(f'Not a supported resource type: {res_id}')

  def encode_resource(self,
                      res_id: resource_id.ResourceId,
                      resource: DatastoreProto) -> str:
    """Typecheck and encode a resource into a bytes-like string.

    Args:
      res_id: The resource id of resource.
      resource: A proto representing the resource data.

    Returns:
      A bytes-like object that can be written to a file.
    """
    expected_type = self._get_proto_type(res_id)

    if not isinstance(resource, expected_type):
      raise ValueError(
          f'Resource has type {type(resource)}, but it should have type '
          f'{expected_type}.')

    return resource.SerializeToString()

  def decode_resource(self,
                      res_id: resource_id.ResourceId,
                      data: Union[str, bytes]) -> DatastoreProto:
    """Decode a resource from bytes to proto based on its resource ID.

    Args:
      res_id: The resource id of the resource.
      data: A bytes-like object representing the resource data
    Returns:
      A proto representation of the resource.
    """
    proto_type = self._get_proto_type(res_id)
    return proto_type.FromString(data)


class FalkenResourceHandler:
  """Handles and parses the underlying resource type for ResourceID usage."""

  # Map resource type to key_field_name -> collection name mapping
  _KEY_FIELD_MAP = {
      data_store_pb2.Project: {
          'project_id': 'project',
      },
      data_store_pb2.Brain: {
          'project_id': 'project',
          'brain_id': 'brain',
      },
      data_store_pb2.Snapshot: {
          'project_id': 'project',
          'brain_id': 'brain',
          'snapshot_id': 'snapshot',
      },
      data_store_pb2.Session: {
          'project_id': 'project',
          'brain_id': 'brain',
          'session_id': 'session',
      },
      data_store_pb2.EpisodeChunk: {
          'project_id': 'project',
          'brain_id': 'brain',
          'session_id': 'session',
          'episode_id': 'episode',
          'chunk_id': 'chunk',
      },
      data_store_pb2.OnlineEvaluation: {
          'project_id': 'project',
          'brain_id': 'brain',
          'session_id': 'session',
          'episode_id': 'online_evaluation',
      },
      data_store_pb2.Assignment: {
          'project_id': 'project',
          'brain_id': 'brain',
          'session_id': 'session',
          'assignment_id': 'assignment',
      },
      data_store_pb2.Model: {
          'project_id': 'project',
          'brain_id': 'brain',
          'session_id': 'session',
          'model_id': 'model',
      },
      data_store_pb2.SerializedModel: {
          'project_id': 'project',
          'brain_id': 'brain',
          'session_id': 'session',
          'model_id': 'serialized_model',
      },
      data_store_pb2.OfflineEvaluation: {
          'project_id': 'project',
          'brain_id': 'brain',
          'session_id': 'session',
          'model_id': 'model',
          'offline_evaluation_id': 'offline_evaluation',
      },
  }

  def get_timestamp_micros(self, resource: DatastoreProto) -> int:
    """Determine timestamp in microseconds from resource object."""
    return resource.created_micros or None  # return 0s as Nones

  def set_timestamp_micros(self,
                           resource: DatastoreProto,
                           timestamp_micros: int):
    """Set timestamp to given value in resource object (not in storage)."""
    resource.created_micros = timestamp_micros

  @classmethod
  def to_resource_id(cls, resource: DatastoreProto) -> resource_id.ResourceId:
    """Determine resource id from the resource data object."""
    try:
      field_map = cls._KEY_FIELD_MAP[type(resource)]
    except KeyError:
      raise ValueError(f'Not a valid resource type: {type(resource)}')
    accessor_map = {}
    for field_name, accessor_name in field_map.items():
      value = getattr(resource, field_name)
      if field_name == 'assignment_id':
        # We hash assignment_ids since they can get pretty long.
        value = hashlib.sha256(value.encode('utf-8')).hexdigest()
      accessor_map[accessor_name] = value
    return resource_id.FalkenResourceId(**accessor_map)


class ResourceStore:
  """Stores resources with ResourceIDs in a filesystem."""

  _RESOURCE_PREFIX = 'resource.'

  def __init__(self, fs: file_system.FileSystem,
               resource_encoder: _FalkenResourceEncoder,
               resource_resolver: FalkenResourceHandler,
               resource_id_type: Type[resource_id.ResourceId]):
    self._fs = fs
    self._encoder = resource_encoder
    self._resolver = resource_resolver
    self._resource_id_type = resource_id_type

  def _get_filename(self, timestamp_micros: int) -> str:
    """Returns file name from microsecond timestamp."""
    # 16 leading zeros should have us covered until year 3.16e8.
    return f'{self._RESOURCE_PREFIX}{timestamp_micros:016d}'

  def _get_path(self, res_id: resource_id.ResourceId,
                timestamp_micros: int) -> str:
    """Returns path from a resource ID and a microsecond timestamp."""
    return os.path.join(str(res_id), self._get_filename(timestamp_micros))

  def write(self, resource) -> resource_id.ResourceId:
    """Writes the resource to an appropriately chosen path."""
    res_id = self._resolver.to_resource_id(resource)
    timestamp_micros = self._resolver.get_timestamp_micros(resource)
    try:
      # Try to read the timestamp from the filesystem.
      read_timestamp = self.read_timestamp_micros(res_id)
    except NotFoundError:
      # If the resource does not exist, set the read_timestamp to None.
      read_timestamp = None

    if not timestamp_micros:
      # Caller did not provide an explicit timestamp.
      if read_timestamp:
        # If this is an existing object in the filesystem, use its timestamp.
        timestamp_micros = read_timestamp
      else:
        # Create a new timestamp
        timestamp_micros = int(time.time() * 1e6)
      self._resolver.set_timestamp_micros(resource, timestamp_micros)
    else:
      # If the user-provided timestamp and timestamp read from the file system
      # disagree, raise an error.
      if read_timestamp and read_timestamp != timestamp_micros:
        raise ValueError(
            'Resource already exists with a different timestamp: \n'
            f'resource: {resource}\nexisting timestamp: {read_timestamp}')

    data = self._encoder.encode_resource(res_id, resource)
    self._fs.write_file(self._get_path(res_id, timestamp_micros), data)
    return res_id

  def read_timestamp_micros(self, res_id: resource_id.ResourceId) -> int:
    """Read the timestamp of a resource from the filesystem."""
    files = self._fs.glob(os.path.join(str(res_id),
                                       f'{self._RESOURCE_PREFIX}*'))
    if not files:
      raise NotFoundError(f'Could not find resource "{res_id}"')
    if len(files) > 1:
      raise InternalError(
          f'Found more than one file for resource id "{res_id}"')
    (file,) = files
    try:
      return int(os.path.basename(file)[len(self._RESOURCE_PREFIX):])
    except ValueError:
      raise InternalError(
          f'Could not translate filename to microsecond timestamp: "{file}"')

  def read(self, res_id: resource_id.ResourceId) -> DatastoreProto:
    """Reads a resource by resource id and returns it.

    Args:
      res_id: The id of the resource to read.
    Returns:
      A datastore proto representing the resource.
    Raises:
      NotFoundError: If the resource does not exist.
    """
    timestamp_micros = self.read_timestamp_micros(res_id)
    try:
      data = self._fs.read_file(self._get_path(res_id, timestamp_micros))
    except FileNotFoundError:
      raise NotFoundError(f'Could not find resource "{res_id}"')
    return self._encoder.decode_resource(res_id, data)

  def _decode_token(self, token):
    """Decodes a pagination token.

    Args:
      token: A string with the form "timestamp:resource_id", or None.

    Returns:
      A pair (timestamp, resource_id), where timestamp is an integer, and
      resource_id a string.
    """
    if token is None:
      return -1, ''

    pair = token.split(':')
    if len(pair) != 2:
      raise ValueError(f'Invalid token {token}.')
    return int(pair[0]), pair[1]

  def _encode_token(self, timestamp_micros: int,
                    res_id: resource_id.ResourceId) -> str:
    """Encodes a pagination token.

    Args:
      timestamp_micros: The microsecond timestamp of the most recently read
          token for the page.
      res_id: The resource id of the last token on the page.

    Returns:
      The encoded string with the form "timestamp:resource_id".
    """
    return f'{timestamp_micros}:{res_id}'

  def list(self,
           res_id_glob: resource_id.ResourceId,
           min_timestamp_micros: int = 0,
           page_token: Optional[str] = None,
           page_size: Optional[int] = None) -> Tuple[List[str], str]:
    """Lists all resource_ids that match the provided pattern.

    Args:
      res_id_glob: A resource ID glob, containing '*' and brace components of
        the form '{a,b,c}' that are resolved in a shell-style fashion.
      min_timestamp_micros: Only return res_ids at least as recent as this
        timestamp.
      page_token: The token for the previous page if any.
      page_size: The size of the page or None to return all IDs.

    Returns:
      A tuple of a list of resource ID strings and pagination token.
    """
    glob_path = os.path.join(str(res_id_glob), '*')
    files = self._fs.glob(glob_path)
    paths = [os.path.dirname(f) for f in files]
    timestamps = [
        int(os.path.basename(f)[len(self._RESOURCE_PREFIX):]) for f in files]
    by_timestamp = sorted(zip(timestamps, paths))

    combined_min_timestamp = min_timestamp_micros
    if page_token:
      page_token_timestamp, page_token_res_id = self._decode_token(page_token)
      combined_min_timestamp = max(page_token_timestamp, combined_min_timestamp)
    else:
      page_token_res_id = None

    page = []
    last_timestamp_micros = 0
    last_read_index = -1
    for last_read_index, (timestamp_micros, res_id_string) in enumerate(
        by_timestamp):
      if timestamp_micros < combined_min_timestamp:
        continue
      if (timestamp_micros == combined_min_timestamp and
          page_token_res_id and
          res_id_string <= page_token_res_id):
        continue

      page.append(res_id_string)
      last_timestamp_micros = timestamp_micros
      if page_size and len(page) == page_size:
        break

    if last_read_index == len(by_timestamp) - 1:
      return page, ''
    else:
      token = self._encode_token(last_timestamp_micros, page[-1])
    return page, token


class DataStore(ResourceStore):
  """Reads and writes data from storage."""

  def __init__(self, fs):
    """Initializes the data store with a given root path.

    Args:
      fs: A FileSystem or MockFileSystem object.
    """
    super().__init__(
        fs,
        _FalkenResourceEncoder(),
        FalkenResourceHandler(),
        resource_id.FalkenResourceId)
    self._callbacks = {}

  def __del__(self):
    self.remove_all_assignment_callbacks()

  def to_resource_id(self, resource: DatastoreProto) -> resource_id.ResourceId:
    return self._resolver.to_resource_id(resource)

  def _get_most_recent(self, res_id_glob: Union[str, resource_id.ResourceId]):
    """Returns the most recent ID matching the glob or None if not found."""
    resource_ids, _ = self.list(res_id_glob, page_size=None)
    return resource_ids[-1] if resource_ids else None

  def get_most_recent_snapshot(
      self,
      project_id: str,
      brain_id: str) -> data_store_pb2.Snapshot:
    """Returns the most recent snapshot for the specified project/brain."""
    return self._get_most_recent(
        resource_id.FalkenResourceId(
            project=project_id, brain=brain_id, snapshot='*'))

  def add_assignment_callback(self, callback):
    """Adds a callback function for newly created assignments.

    Args:
      callback: A function that will be called with a single argument, an
        assignment id.
    """

    def file_callback(file_name):
      # TODO(b/185940506): check file matches assignment, read file,
      # and return the parsed id.
      callback(file_name)

    if callback in self._callbacks:
      raise ValueError('Added assignment callback twice.')

    self._callbacks[callback] = file_callback
    self._fs.add_file_callback(file_callback)

  def remove_assignment_callback(self, callback):
    """Removes a function from the assignment callbacks.

    Args:
      callback: The callback function to remove.
    """
    self._fs.remove_file_callback(self._callbacks.pop(callback))

  def remove_all_assignment_callbacks(self):
    """Removes all assignment callbacks."""
    while self._callbacks:
      self.remove_assignment_callback(next(iter(self._callbacks)))
