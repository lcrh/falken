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
#
# automatically generated by the FlatBuffers compiler, do not modify

# namespace: tflite

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class SquareOptions(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsSquareOptions(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = SquareOptions()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def SquareOptionsBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # SquareOptions
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

def SquareOptionsStart(builder): builder.StartObject(0)
def SquareOptionsEnd(builder): return builder.EndObject()


class SquareOptionsT(object):

    # SquareOptionsT
    def __init__(self):
        pass

    @classmethod
    def InitFromBuf(cls, buf, pos):
        squareOptions = SquareOptions()
        squareOptions.Init(buf, pos)
        return cls.InitFromObj(squareOptions)

    @classmethod
    def InitFromObj(cls, squareOptions):
        x = SquareOptionsT()
        x._UnPack(squareOptions)
        return x

    # SquareOptionsT
    def _UnPack(self, squareOptions):
        if squareOptions is None:
            return

    # SquareOptionsT
    def Pack(self, builder):
        SquareOptionsStart(builder)
        squareOptions = SquareOptionsEnd(builder)
        return squareOptions