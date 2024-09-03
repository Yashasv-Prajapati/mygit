from collections import namedtuple
from utils.reader import read_file
import os
import struct

IndexEntry = namedtuple("IndexEntry", [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode',
    'uid', 'gid', 'size', 'sha1', 'path',
])

def read_index():

    try:
        data = read_file(os.path.join('.git', 'index'))
        
        print(data[:12])

        signature, version_number, num_of_entries = struct.unpack('!4sLL', data[:12])

        assert signature == b'DIRC' , f'Invalid signature: {signature}'
        assert version_number == 2, f'Invalid version number: {version_number}'

        index_entries = []
        data = data[12:]
        start = 0
        for _ in range(num_of_entries):
            ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1 = struct.unpack('!LLLLLLLLLL20sH', start[start:start+62])
            start += 62
            index_entries.append(IndexEntry(ctime_s,ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1))

            
    except FileNotFoundError as f:
        print('File not found')
        exit(0)
    


def update_index(flag: str):

    if flag == '--add':
        
        read_index()

