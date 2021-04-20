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
"""Imports and executes all tests."""

import importlib
import inspect
import os
import subprocess
import sys

# Add search paths for all modules.
_SERVICE_MODULE_PATHS = ['data_store', 'log', 'learner', 'learner/brains']
sys.path.extend(
    [os.path.join(os.path.dirname(__file__), p) for p in _SERVICE_MODULE_PATHS]
)

# Modules required to execute service modules and tests.
_REQUIRED_PYTHON_MODULES = [
    'absl-py',
    'tensorflow',
    'tensorflow_graphics',
    'tf-agents',
]

_TEST_MODULES = [
    'data_store.data_store_test',
    'learner.brains.egocentric_test',
    'learner.brains.imitation_loss_test',
    'learner.brains.layers_test',
    'learner.brains.numpy_replay_buffer_test',
    'learner.brains.policies_test',
    'learner.brains.weights_initializer_test',
    'learner.data_fetcher_test',
    'log.falken_logging_test',
]


def install_dependencies():
  """Install all Python module dependencies."""
  for m in _REQUIRED_PYTHON_MODULES:
    subprocess.check_call([sys.executable, '-m', 'pip', '-q', 'install', m])


def _add_module_test_classes_to_global_namespace(test_classes, module):
  """Add test classes from the specified modules to this global namespace.

  Args:
    test_classes: Tuple of base classes for tests.
    module: Module to search for test classes.
  """
  for name, value in vars(module).items():
    if inspect.isclass(value):
      if issubclass(value, test_classes):
        globals()[name] = value


def run_absltests():
  """Run all absl tests in the current module."""
  # Can't import absl at the top of this file as it needs to be installed first.
  # pylint: disable=g-import-not-at-top.
  from absl.testing import absltest
  from absl.testing import parameterized
  # Import test modules.
  for module_name in _TEST_MODULES:
    _add_module_test_classes_to_global_namespace(
        (absltest.TestCase, parameterized.TestCase),
        importlib.import_module(module_name))
  absltest.main()


if __name__ == '__main__':
  install_dependencies()
  run_absltests()