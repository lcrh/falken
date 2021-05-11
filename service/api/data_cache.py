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
"""Handles caching for falken data_store objects."""

import functools

_MAXCACHE = 512


def get_brain_spec(data_store, project_id, brain_id):
  """Get cached brain's brain_spec.

  Args:
    data_store: data_store.DataStore to read from if the brain is not cached.
    project_id: Project ID associated with the requested brain spec.
    brain_id: Brain ID associated with the requested brain spec.

  Returns:
    brain_pb2.BrainSpec instance.
  """
  return get_brain(data_store, project_id, brain_id).brain_spec


@functools.lru_cache(maxsize=_MAXCACHE)
def get_brain(data_store, project_id, brain_id):
  """Get cached brain or read brain from data_store.

  Args:
    data_store: data_store.DataStore to read from if the brain is not cached.
    project_id: Project ID associated with the requested brain.
    brain_id: Brain ID associated with the requested brain.

  Returns:
    data_store_pb2.Brain instance.
  """
  return data_store.read_brain(project_id, brain_id)