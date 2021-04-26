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

class ReverseSequenceOptions(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsReverseSequenceOptions(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ReverseSequenceOptions()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def ReverseSequenceOptionsBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # ReverseSequenceOptions
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ReverseSequenceOptions
    def SeqDim(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # ReverseSequenceOptions
    def BatchDim(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

def ReverseSequenceOptionsStart(builder): builder.StartObject(2)
def ReverseSequenceOptionsAddSeqDim(builder, seqDim): builder.PrependInt32Slot(0, seqDim, 0)
def ReverseSequenceOptionsAddBatchDim(builder, batchDim): builder.PrependInt32Slot(1, batchDim, 0)
def ReverseSequenceOptionsEnd(builder): return builder.EndObject()


class ReverseSequenceOptionsT(object):

    # ReverseSequenceOptionsT
    def __init__(self):
        self.seqDim = 0  # type: int
        self.batchDim = 0  # type: int

    @classmethod
    def InitFromBuf(cls, buf, pos):
        reverseSequenceOptions = ReverseSequenceOptions()
        reverseSequenceOptions.Init(buf, pos)
        return cls.InitFromObj(reverseSequenceOptions)

    @classmethod
    def InitFromObj(cls, reverseSequenceOptions):
        x = ReverseSequenceOptionsT()
        x._UnPack(reverseSequenceOptions)
        return x

    # ReverseSequenceOptionsT
    def _UnPack(self, reverseSequenceOptions):
        if reverseSequenceOptions is None:
            return
        self.seqDim = reverseSequenceOptions.SeqDim()
        self.batchDim = reverseSequenceOptions.BatchDim()

    # ReverseSequenceOptionsT
    def Pack(self, builder):
        ReverseSequenceOptionsStart(builder)
        ReverseSequenceOptionsAddSeqDim(builder, self.seqDim)
        ReverseSequenceOptionsAddBatchDim(builder, self.batchDim)
        reverseSequenceOptions = ReverseSequenceOptionsEnd(builder)
        return reverseSequenceOptions