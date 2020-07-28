#!/usr/bin/env python3

"""
    ext4extract - Ext4 data extracting tool
    Copyright (C) 2017, HexEdit (IFProject)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import argparse
from struct import unpack
from collections import namedtuple
import os


class Ext4(object):
    __SUPERBLOCK_PACK__ = "<IIIIIIIIIIIIIHHHHHHIIIIHHIHHIII16s16s64sIBBH16sIII16sBBH"
    __GROUP_DESCRIPTOR_PACK__ = "<IIIHHHHIHHHH"
    __INODE_PACK__ = "<HHIIIIIHHII4s60sIIII12s"
    __EXTENT_HEADER_PACK__ = "<HHHHI"
    __EXTENT_INDEX_PACK__ = "<IIHH"
    __EXTENT_ENTRY_PACK__ = "<IHHI"
    __DIR_ENTRY_PACK__ = "<IHH"
    __DIR_ENTRY_V2_PACK__ = "<IHBB"
    __XATTR_HEADER_PACK__ = "<IIIII12s"
    __XATTR_ENTRY_PACK__ = "<BBHIII"

    __SuperBlock__ = namedtuple('Ext4SuperBlock', """
        s_inodes_count
        s_blocks_count_lo
        s_r_blocks_count_lo
        s_free_blocks_count_lo
        s_free_inodes_count
        s_first_data_block
        s_log_block_size
        s_log_cluster_size
        s_blocks_per_group
        s_clusters_per_group
        s_inodes_per_group
        s_mtime
        s_wtime
        s_mnt_count
        s_max_mnt_count
        s_magic
        s_state
        s_errors
        s_minor_rev_level
        s_lastcheck
        s_checkinterval
        s_creator_os
        s_rev_level
        s_def_resuid
        s_def_resgid
        s_first_ino
        s_inode_size
        s_block_group_nr
        s_feature_compat
        s_feature_incompat
        s_feature_ro_compat
        s_uuid
        s_volume_name
        s_last_mounted
        s_algorithm_usage_bitmap
        s_prealloc_blocks
        s_prealloc_dir_blocks
        s_reserved_gdt_blocks
        s_journal_uuid
        s_journal_inum
        s_journal_dev
        s_last_orphan
        s_hash_seed
        s_def_hash_version
        s_jnl_backup_type
        s_desc_size
    """)

    __GroupDescriptor__ = namedtuple('Ext4GroupDescriptor', """
        bg_block_bitmap_lo
        bg_inode_bitmap_lo
        bg_inode_table_lo
        bg_free_blocks_count_lo
        bg_free_inodes_count_lo
        bg_used_dirs_count_lo
        bg_flags
        bg_exclude_bitmap_lo
        bg_block_bitmap_csum_lo
        bg_inode_bitmap_csum_lo
        bg_itable_unused_lo
        bg_checksum
    """)

    __Inode__ = namedtuple('Ext4Inode', """
        i_mode
        i_uid
        i_size_lo
        i_atime
        i_ctime
        i_mtime
        i_dtime
        i_gid
        i_links_count
        i_blocks_lo
        i_flags
        i_osd1
        i_block
        i_generation
        i_file_acl_lo
        i_size_high
        i_obso_faddr
        i_osd2
    """)

    __ExtentHeader__ = namedtuple('Ext4ExtentHeader', """
        eh_magic
        eh_entries
        eh_max
        eh_depth
        eh_generation
    """)

    __ExtentIndex__ = namedtuple('Ext4ExtentIndex', """
        ei_block
        ei_leaf_lo
        ei_leaf_hi
        ei_unused
    """)

    __ExtentEntry__ = namedtuple('Ext4ExtentEntry', """
        ee_block
        ee_len
        ee_start_hi
        ee_start_lo
    """)

    __DirEntry__ = namedtuple('Ext4DirEntry', """
        inode
        rec_len
        name_len
    """)

    __DirEntryV2__ = namedtuple('Ext4DirEntryV2', """
        inode
        rec_len
        name_len
        file_type
    """)

    __XattrHeader__ = namedtuple('Ext4XattrHeader', """
        h_magic
        h_refcount
        h_blocks
        h_hash
        h_checksum
        h_reserved
    """)
    
    __XattrEntry__ = namedtuple('Ext4XattrEntry', """
        e_name_len
        e_name_index
        e_value_offs
        e_value_inum
        e_value_size
        e_hash
    """)

    class DirEntry:
        def __init__(self, inode=0, name=None, entry_type=0):
            self._inode = inode
            self._name = name
            self._type = entry_type

        def __str__(self):
            entry_type = [
                "Unknown",
                "Regular file",
                "Directory",
                "Character device file",
                "Block device file",
                "FIFO",
                "Socket",
                "Symbolic link"
            ][self._type]
            return "{name:24} ({type}, inode {inode})".format(inode=self._inode, name=self._name, type=entry_type)

        @property
        def inode(self):
            return self._inode

        @property
        def name(self):
            return self._name

        @property
        def type(self):
            return self._type

        @inode.setter
        def inode(self, x):
            self._inode = x

        @name.setter
        def name(self, x):
            self._name = x

        @type.setter
        def type(self, x):
            self._type = x

    def make_superblock(data):
        return __SuperBlock__._make(unpack(__SUPERBLOCK_PACK__, data))


    def make_group_descriptor(data):
        return __GroupDescriptor__._make(unpack(__GROUP_DESCRIPTOR_PACK__, data))


    def make_inode(data):
        return __Inode__._make(unpack(__INODE_PACK__, data))


    def make_extent_header(data):
        return __ExtentHeader__._make(unpack(__EXTENT_HEADER_PACK__, data))


    def make_extent_index(data):
        return __ExtentIndex__._make(unpack(__EXTENT_INDEX_PACK__, data))


    def make_extent_entry(data):
        return __ExtentEntry__._make(unpack(__EXTENT_ENTRY_PACK__, data))


    def make_dir_entry(data):
        return __DirEntry__._make(unpack(__DIR_ENTRY_PACK__, data))


    def make_dir_entry_v2(data):
        return __DirEntryV2__._make(unpack(__DIR_ENTRY_V2_PACK__, data))


    def make_xattr_header(data):
        return __XattrHeader__._make(unpack(__XATTR_HEADER_PACK__, data))


    def make_xattr_entry(data):
        return __XattrEntry__._make(unpack(__XATTR_ENTRY_PACK__, data))

    def __init__(self, filename=None):
        self._ext4 = None
        self._superblock = None
        self._block_size = 1024

        if filename is not None:
            self.load(filename)

    def __str__(self):
        if self._superblock is None:
            return "Not loaded"
        else:
            volume_name = self._superblock.s_volume_name.decode('utf-8').rstrip('\0')
            mounted_at = self._superblock.s_last_mounted.decode('utf-8').rstrip('\0')
            if not mounted_at:
                mounted_at = "not mounted"
            return "Volume name: {}, last mounted at: {}".format(volume_name, mounted_at)

    def _read_group_descriptor(self, bg_num):
        gd_offset = (self._superblock.s_first_data_block + 1) * self._block_size \
                    + (bg_num * self._superblock.s_desc_size)
        self._ext4.seek(gd_offset)
        return make_group_descriptor(self._ext4.read(32))

    def _read_inode(self, inode_num):
        inode_bg_num = (inode_num - 1) // self._superblock.s_inodes_per_group
        bg_inode_idx = (inode_num - 1) % self._superblock.s_inodes_per_group
        group_desc = self._read_group_descriptor(inode_bg_num)
        inode_offset = \
            (group_desc.bg_inode_table_lo * self._block_size) \
            + (bg_inode_idx * self._superblock.s_inode_size)
        self._ext4.seek(inode_offset)
        return make_inode(self._ext4.read(128))

    def _read_extent(self, data, extent_block):
        hdr = make_extent_header(extent_block[:12])
        if hdr.eh_magic != 0xf30a:
            raise RuntimeError("Bad extent magic")

        for eex in range(0, hdr.eh_entries):
            raw_offset = 12 + (eex * 12)
            entry_raw = extent_block[raw_offset:raw_offset + 12]
            if hdr.eh_depth == 0:
                entry = make_extent_entry(entry_raw)
                _start = entry.ee_block * self._block_size
                _size = entry.ee_len * self._block_size
                self._ext4.seek(entry.ee_start_lo * self._block_size)
                data[_start:_start + _size] = self._ext4.read(_size)
            else:
                index = make_extent_index(entry_raw)
                self._ext4.seek(index.ei_leaf_lo * self._block_size)
                lower_block = self._ext4.read(self._block_size)
                self._read_extent(data, lower_block)

    def _read_data(self, inode):
        data = b''

        if inode.i_size_lo == 0:
            pass
        elif inode.i_flags & 0x10000000 or (inode.i_mode & 0xf000 == 0xa000 and inode.i_size_lo <= 60):
            data = inode.i_block
        elif inode.i_flags & 0x80000:
            data = bytearray(inode.i_size_lo)
            self._read_extent(data, inode.i_block)
        else:
            raise RuntimeError("Mapped Inodes are not supported")

        return data

    def load(self, filename):
        self._ext4 = open(filename, "rb")
        self._ext4.seek(1024)
        self._superblock = make_superblock(self._ext4.read(256))
        if self._superblock.s_magic != 0xef53:
            raise RuntimeError("Bad superblock magic")
        incompat = self._superblock.s_feature_incompat
        for f_id in [0x1, 0x4, 0x10, 0x80, 0x1000, 0x4000, 0x10000]:
            if incompat & f_id:
                raise RuntimeError("Unsupported feature ({:#x})".format(f_id))
        self._block_size = 2 ** (10 + self._superblock.s_log_block_size)

    def read_dir(self, inode_num):
        inode = self._read_inode(inode_num)
        dir_raw = self._read_data(inode)
        dir_data = list()
        offset = 0
        while offset < len(dir_raw):
            entry_raw = dir_raw[offset:offset + 8]
            entry = DirEntry()
            if self._superblock.s_feature_incompat & 0x2:
                dir_entry = make_dir_entry_v2(entry_raw)
                entry.type = dir_entry.file_type
            else:
                dir_entry = make_dir_entry(entry_raw)
                entry_inode = self._read_inode(dir_entry.inode)
                inode_type = entry_inode.i_mode & 0xf000
                if inode_type == 0x1000:
                    entry.type = 5
                elif inode_type == 0x2000:
                    entry.type = 3
                elif inode_type == 0x4000:
                    entry.type = 2
                elif inode_type == 0x6000:
                    entry.type = 4
                elif inode_type == 0x8000:
                    entry.type = 1
                elif inode_type == 0xA000:
                    entry.type = 7
                elif inode_type == 0xC000:
                    entry.type = 6
            entry.inode = dir_entry.inode
            entry.name = dir_raw[offset + 8:offset + 8 + dir_entry.name_len].decode('utf-8')
            dir_data.append(entry)
            offset += dir_entry.rec_len
        return dir_data

    def read_file(self, inode_num):
        inode = self._read_inode(inode_num)
        return self._read_data(inode)[:inode.i_size_lo], inode.i_atime, inode.i_mtime

    def read_link(self, inode_num):
        inode = self._read_inode(inode_num)
        return self._read_data(inode)[:inode.i_size_lo].decode('utf-8')

    def read_xattr(self, inode):
        if inode.i_file_acl_lo == 0:
            return {}

        self._ext4.seek(inode.i_file_acl_lo * self._block_size)
        xattr_hdr = make_xattr_header(self._ext4.read(32))
        if xattr_hdr.h_magic != 0xea020000:
            raise RuntimeError("Bad xattr magic")
        xattr_data = self._ext4.read((self._block_size * xattr_hdr.h_blocks) - 32)

        xattr_prefix = [
            "",
            "user.",
            "system.posix_acl_access",
            "system.posix_acl_default",
            "trusted.",
            "security.",
            "system.",
            "system.richacl"
        ]

        xattr = {}
        offset = 0
        while offset < len(xattr_data):
            entry = make_xattr_entry(xattr_data[offset:offset + 16])
            if (entry.e_name_len, entry.e_name_index, entry.e_value_offs, entry.e_value_inum) == (0, 0, 0, 0):
                break
            offset += 16

            name = xattr_data[offset:offset + entry.e_name_len].decode('utf-8')
            offset += entry.e_name_len

            key = xattr_prefix[entry.e_name_index] + name
            value = xattr_data[entry.e_value_offs:entry.e_value_offs + entry.e_value_size]
            if value == b'':
                value = None
            xattr[key] = value

        return xattr

    def read_meta(self, inode_num):
        inode = self._read_inode(inode_num)
        return Metadata(
            inode=inode_num,
            itype=inode.i_mode >> 12 & 0xf,
            size=inode.i_size_lo,
            ctime=inode.i_ctime,
            mtime=inode.i_mtime,
            uid=inode.i_uid,
            gid=inode.i_gid,
            mode=inode.i_mode & 0xfff,
            xattr=self.read_xattr(inode))

    @property
    def root(self):
        return self.read_dir(2)

class Metadata:
    def __init__(self, inode, itype, size, ctime, mtime, uid=0, gid=0, mode=0, xattr={}):
        self._attr = {
            'inode': inode,
            'type': itype,
            'size': size,
            'ctime': ctime,
            'mtime': mtime,
            'uid': uid,
            'gid': gid,
            'mode': mode
        }
        self._xattr = xattr

    def __str__(self):
        attr_s = []
        for attr in self._attr:
            attr_s.append("{key}=\"{value}\"".format(key=attr, value=self._attr[attr]))
        for attr in self._xattr:
            attr_s.append(attr if self._xattr[attr] is None
                          else "{key}=\"{value}\"".format(key=attr, value=self._xattr[attr]))
        return " ".join(attr_s)

class Application(object):
    def __init__(self):
        self._args = None
        self._ext4 = None
        self._symltbl = None
        self._metatbl = None

    def _parse_args(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("-v", "--verbose", dest='verbose', help="verbose output",
                            action='store_true')
        parser.add_argument("-D", "--directory", dest='directory', type=str, help="set output directory", default=".")
        parser.add_argument("-S", "--dump-symlink-table", dest='symlinks', type=str, help="Generate symlink table")
        parser.add_argument("-M", "--dump-metadata", dest='metadata', type=str, help="Generate inode metadata table")
        parser.add_argument("filename", type=str, help="EXT4 device or image")

        group = parser.add_mutually_exclusive_group()
        group.add_argument("--save-symlinks", help="save symlinks as is (default)", action='store_true')
        group.add_argument("--text-symlinks", help="save symlinks as text file", action='store_true')
        group.add_argument("--empty-symlinks", help="save symlinks as empty file", action='store_true')
        group.add_argument("--skip-symlinks", help="do not save symlinks", action='store_true')

        try:
            self._args = parser.parse_args()
        except SystemExit:
            sys.exit(2)

    def _extract_dir(self, dir_data, path, name=None):
        assert self._ext4 is not None
        if name is not None:
            path = os.path.join(path, name)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        for de in dir_data:
            processed = False
            if self._metatbl is not None:
                self._write_meta(de, path)
            if de.type == 1:  # regular file
                data, atime, mtime = self._ext4.read_file(de.inode)
                file = open(os.path.join(path, de.name), 'w+b')
                file.write(data)
                file.close()
                os.utime(file.name, (atime, mtime))
                processed = True
            elif de.type == 2:  # directory
                if de.name == '.' or de.name == '..':
                    continue
                self._extract_dir(self._ext4.read_dir(de.inode), path, de.name)
            elif de.type == 7:  # symlink
                link = os.path.join(path, de.name)
                link_to = self._ext4.read_link(de.inode)
                if self._symltbl is not None:
                    self._write_symlink(link, link_to)
                if self._args.skip_symlinks:
                    continue
                if self._args.text_symlinks:
                    link = open(link, "w+b")
                    link.write(link_to.encode('utf-8'))
                    link.close()
                elif self._args.empty_symlinks:
                    open(link, "w+").close()
                else:
                    os.symlink(link_to, link + ".tmp")
                    os.rename(link + ".tmp", link)
                processed = True
            if processed and self._args.verbose:
                print(os.path.join(os.path.sep, path.lstrip(self._args.directory), de.name))

    def _write_symlink(self, link, link_to):
        self._symltbl.write(
            "path=\"{link}\" target=\"{target}\"".format(
                link=link,
                target=link_to
            ) + os.linesep)

    def _write_meta(self, direntry, path):
        meta = self._ext4.read_meta(direntry.inode)
        self._metatbl.write(
            "inode=\"{inode}\" path=\"{path}\" {meta}".format(
                inode=direntry.inode,
                meta=meta,
                path=os.path.join(path, direntry.name)
            ) + os.linesep)

    def _do_extract(self):
        self._ext4 = Ext4(self._args.filename)
        self._extract_dir(self._ext4.root, self._args.directory)

    def run(self):
        self._parse_args()

        if self._args.symlinks is not None:
            self._symltbl = open(self._args.symlinks, "w+")
        if self._args.metadata is not None:
            self._metatbl = open(self._args.metadata, "w+")

        self._do_extract()

        if self._symltbl is not None:
            self._symltbl.close()
        if self._metatbl is not None:
            self._metatbl.close()


def exception_handler(exception_type, exception, traceback):
    del traceback
    sys.stderr.write("{}: {}\n".format(exception_type.__name__, exception))


if __name__ == '__main__':
    sys.excepthook = exception_handler
    Application().run()
