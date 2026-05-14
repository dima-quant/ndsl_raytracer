# Python NDSL Raytracer
# Copyright (c) 2025 Dmytro Makogon, see LICENSE (MIT or Apache 2.0, as an option)
# The project is mostly a port of Trace of Radiance (https://github.com/mratsim/trace-of-radiance, see below)
# /// nimic
#
# ///

from __future__ import annotations
from nimic.ntypes import *

from nimic.std.os import *
from nimic.std.strformat import *
from nimic.system.ansi_c import *
from nimic.std.syncio import read_file, write_buffer, set_file_pos
from minimp4 import MP4E_mux_t, mp4_h26x_writer_t, MP4E_close, mp4_h26x_write_close, MP4E_STATUS_OK, mp4_h26x_write_nal, MP4E_open, mp4_h26x_write_init

class MP4Muxer(Object):
    _muxer: ptr[MP4E_mux_t]
    _writer: ptr[mp4_h26x_writer_t]

def close(m: mut@MP4Muxer):
    _ = MP4E_close(m._muxer)
    m._muxer = None
    mp4_h26x_write_close(m._writer)
    c_free(m._writer)

def writeToFile(offset: int64, buffer: pointer, size: csize_t, token: pointer) -> cint:
    """{.cdecl, gcsafe.}"""
    with let:
        file = cast[File](token)
    set_file_pos(file, offset)
    with let:
        bytesWritten = write_buffer(file, buffer, size)

    if csize_t(bytesWritten) != size:
        return -50
    return 0

def writeMP4_from(self: mut@MP4Muxer, src: string):
    with let:
        _buffer = read_file(src)
        data = cast[ptr[UncheckedArray[uint8]]](addr(_buffer[0]))
        dataLen = len(_buffer)
    with let:
        ok = mp4_h26x_write_nal(self._writer, data, dataLen, uint32(90000 // 30))
    doAssert(ok == MP4E_STATUS_OK, "error: mp4_h26x_write_nal failed, code=" + str(ok))

def initialize(self: mut@MP4Muxer, file: File, width: int32, height: int32):
    doAssert(self._muxer.is_nil, "Already initialized")
    doAssert(self._writer.is_nil, "Already initialized")
    self._muxer = MP4E_open(0, 0, cast[pointer](file), writeToFile)
    doAssert(self._muxer.is_nil == False, "MP4E_open returned NULL! muxer init failed!")
    self._writer = cast[ptr[mp4_h26x_writer_t]](c_malloc(csize_t(sizeof(mp4_h26x_writer_t))))
    with let:
        ok = mp4_h26x_write_init(self._writer, self._muxer, nint(width), nint(height), 0)
    doAssert(ok == MP4E_STATUS_OK, "error: mp4_h26x_write_init failed")

if comptime(__name__ == "__main__"):
    def main():
        with let:
            exeName = extractFilename(getAppFilename())
        with var:
            source: string
            destination: string
        if paramCount() != 2:
            print(f"Usage: {exeName} <source> <destination>")
            quit(1)
        else:
            source = paramStr(1)
            destination = paramStr(2)

        with var:
            mP4Muxer = MP4Muxer()
        with let:
            dst = open(destination, fmWrite)
        mP4Muxer.initialize(dst, 576, 324)
        mP4Muxer.writeMP4_from(source)
        mP4Muxer.close()
        dst.close()

    main()


# Trace of Radiance
# Copyright (c) 2020 Mamy André-Ratsimbazafy
# Licensed and distributed under either of
#   * MIT license (license terms in the root directory or at http://opensource.org/licenses/MIT).
#   * Apache v2 license (license terms in the root directory or at http://www.apache.org/licenses/LICENSE-2.0).
# at your option. This file may not be copied, modified, or distributed except according to those terms.

# import
#   std/[strutils, os],
#   system/ansi_c

# const
#   mp4Path = currentSourcePath.rsplit(DirSep, 1)[0]
#   backendsPath = mp4Path & DirSep & "backends"

# {.localPassC: "-DMINIMP4_IMPLEMENTATION -I" & backendsPath.}
# {.pragma: minimp4, importc, header: backendsPath / "minimp4.h".}

# # C API
# # ------------------------------------------------------

# type
#   mp4_h26x_writer_t {.minimp4.} = object
#   MP4E_mux_t {.minimp4.} = object

#   MP4Status {.size: sizeof(cint).} = enum
#     MP4E_STATUS_ONLY_ONE_DSI_ALLOWED = -4
#     MP4E_STATUS_FILE_WRITE_ERROR = -3
#     MP4E_STATUS_NO_MEMORY = -2
#     MP4E_STATUS_BAD_ARGUMENTS = -1
#     MP4E_STATUS_OK = 0

# proc mp4_h26x_write_init(
#        h: ptr mp4_h26x_writer_t,
#        mux: ptr MP4E_mux_t,
#        width: cint,
#        height: cint,
#        isHEVC: cint
#      ): MP4Status {.minimp4, noDecl.}
# proc mp4_h26x_write_nal(
#        h: ptr mp4_h26x_writer_t,
#        nal: ptr UncheckedArray[byte], length: cint,
#        timeStamp90kHz_next: cuint
#      ): MP4Status {.minimp4, noDecl.}
# proc mp4_h26x_write_close(w: ptr mp4_h26x_writer_t) {.minimp4, noDecl.}


# proc MP4E_open(
#        sequential_mod_flag: cint,
#        enable_fragmentation: cint,
#        token: pointer,
#        write_callback: proc(
#          offset: int64,
#          buffer: pointer,
#          size: csize_t,
#          token: pointer
#        ): cint{.cdecl, gcsafe.}
#      ): ptr MP4E_mux_t {.minimp4, noDecl.}

# proc MP4E_close(mux: ptr MP4E_mux_t) {.minimp4, noDecl.}

# # Helpers
# # ------------------------------------------------------

# func get_nal_size(buf: ptr UncheckedArray[byte], size: csize_t): csize_t =
#   var pos: csize_t = 3
#   while size-pos > 3:
#     if buf[pos] == 0 and buf[pos+1] == 0 and buf[pos+2] == 1:
#       return pos
#     if buf[pos] == 0 and buf[pos+1] == 0 and buf[pos+2] == 0 and buf[pos+3] == 1:
#       return pos
#     inc pos
#   return size

# template `+=`*(p: var ptr, offset: csize_t) =
#   ## Pointer increment
#   {.emit:[p," += ", offset, ";"].}

# proc write_mp4(
#        mp4wr: ptr mp4_h26x_writer_t,
#        fps: cint,
#        data: ptr byte,
#        data_size: csize_t) =

#   var data_size = data_size
#   var data = cast[ptr UncheckedArray[byte]](data)
#   while data_size > 0:
#     let nal_size = get_nal_size(data, data_size)
#     if nal_size < 4:
#       data += 1
#       data_size -= 1
#       continue
#     let ok = mp4_h26x_write_nal(
#       mp4wr, data, nal_size.cint, cuint(90000 div fps.int)
#     )
#     doAssert ok == MP4E_STATUS_OK, "error: mp4_h26x_write_nal failed"
#     data += nal_size
#     data_size -= nal_size

# # High-Level API
# # ------------------------------------------------------

# type MP4Muxer* = object
#   muxer: ptr MP4E_mux_t
#   writer: ptr mp4_h26x_writer_t

# proc `=`*(dst: var MP4Muxer, src: MP4Muxer) {.error: "An MP4Muxer cannot be copied".}

# proc close*(m: var MP4Muxer) =
#   m.muxer.MP4E_close()
#   m.muxer = nil
#   m.writer.mp4_h26x_write_close()
#   m.writer.c_free()

# {.push stackTrace: off.}
# proc writeToFile(
#        offset: int64,
#        buffer: pointer,
#        size: csize_t,
#        token: pointer
#      ): cint {.cdecl, gcsafe.} =
#   let file = cast[File](token)
#   file.setFilePos(offset)
#   let bytesWritten = file.writeBuffer(buffer, size)
#   return cint(bytesWritten.csize_t != size)
# {.pop.}

# proc writeMP4_from*(
#        self: var MP4Muxer,
#        src: string
#      ) =
#   let buffer = src.readFile()
#   self.writer.write_mp4(
#     fps = 30,
#     data = cast[ptr byte](buffer[0].unsafeAddr),
#     data_size = csize_t buffer.len
#   )

# proc initialize*(
#        self: var MP4Muxer,
#        file: File,
#        width, height: int32
#      ) =
#   doAssert self.muxer.isNil, "Already initialized"
#   doAssert self.writer.isNil, "Already initialized"
#   self.muxer = MP4E_open(
#     sequential_mod_flag = 0,
#     enable_fragmentation = 0,
#     token = pointer(file),
#     write_callback = writeToFile
#   )

#   self.writer = cast[typeof self.writer](
#     c_malloc(csize_t sizeof(mp4_h26x_writer_t))
#   )

#   let ok = self.writer.mp4_h26x_write_init(
#     self.muxer,
#     width.cint, height.cint,
#     is_hevc = 0
#   )
#   doAssert ok == MP4E_STATUS_OK, "error: mp4_h26x_write_init failed"

# # Sanity checks
# # ------------------------------------------------------

# when isMainModule:
#   import strformat

#   proc main() =
#     let exeName = getAppFilename().extractFilename()
#     var source, destination: string
#     if paramCount() != 2:
#       echo &"Usage: {exeName} <source> <destination>"
#       quit 1
#     else:
#       source = paramStr(1)
#       destination = paramStr(2)

#     var mP4Muxer: MP4Muxer
#     let dst = open(destination, fmWrite)
#     mP4Muxer.initialize(dst, 576, 324)
#     mP4Muxer.writeMP4(source)
#     mP4Muxer.close()
#     dst.close()

#   main()
