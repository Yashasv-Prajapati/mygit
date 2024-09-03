from collections import namedtuple
from utils.reader import read_file
import os
import struct
from hash import hash_object

IndexEntry = namedtuple("IndexEntry", [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode',
    'uid', 'gid', 'size', 'sha1', 'path',
])

def read_index()->list[IndexEntry]:

    try:
        data = read_file(os.path.join('.git', 'index'))

        signature, version_number, num_of_entries = struct.unpack('!4sLL', data[:12])

        assert signature == b'DIRC' , f'Invalid signature: {signature}'
        assert version_number == 2, f'Invalid version number: {version_number}'

        index_entries = []
        data_entries = data[12:]
        start = 0
        while start+62 < len(data_entries):
            # Each entry is of 62 bytes(fixed) + additional bytes for storing filepath name
            end = start+62

            # Extracting first 62 bytes of the entry
            ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1 = struct.unpack('!LLLLLLLLLL20sH', data_entries[start:end])
            
            # start from end index and search for first \x00 - this will mark the end index of the filepath of each entry
            filepath_end_index = data_entries.index('\x00', end)
            
            # Extract the filepath name from the index entry 
            filepath = data_entries[end: filepath_end_index].decode()
            filepath_bytes = filepath_end_index - end

            index_entries.append(IndexEntry(ctime_s,ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1, filepath))
            start += 62 + filepath_bytes
            print(start) 

        assert len(index_entries) == num_of_entries
        return index_entries
            
    except FileNotFoundError as f:
        print('File not found')
        exit(0)
    
def upsert_on_index_entries(filename:str, entries: list[IndexEntry]):
    try:
        filepath = os.path.join(os.getcwd(), filename)
        file_stat = os.stat(filepath)
        
        # Extract this file's index entry metadata
        ctime_s = int(file_stat.st_birthtime)
        ctime_n = int(file_stat.st_birthtime_ns % 1e9)
        mtime_s = int(file_stat.st_mtime)
        mtime_n = int(file_stat.st_mtime_ns %1e9)
        dev = int(file_stat.st_dev) & 0xFFFFFFFF # device id
        ino = int(file_stat.st_ino) & 0xFFFFFFFF # inode number
        mode = file_stat.st_mode # mode - file permissions
        uid = file_stat.st_uid # user id of the owner
        gid = file_stat.st_gid # group id of the owner
        size = file_stat.st_size # size of the file in bytes

        # sha1 hash of the file
        sha1_hash = hash_object('unknown', filename)

        entry_to_upsert = IndexEntry(ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1_hash, filename)

        # entries = read_index()

        to_update = not any(filename == entry.path for entry in entries)

        if to_update:
            for index in entries:
                if entries[index].path == filename:
                    entries[index] = entry_to_upsert
                    return True
        entries.append(entry_to_upsert)
        return True
    except FileNotFoundError as fnf:
        print(f"File not Found -> {filename} -> upsert_on_index_entries")
        exit(0)
    except Exception as e:
        print("Something went wrong -> upsert_on_index_entries: ", e)
        exit(0)                    

def write_to_index(entries: list[IndexEntry]):
    try:
        data = read_file(os.path.join('.git', 'index'))

        signature, version_number, num_of_entries = struct.unpack('!4sLL', data[:12])

        assert signature == b'DIRC', f'Invalid signature: {signature}'
        assert version_number == 2, f'Invalid version number: {version_number}'

        #TODO - Add the header and Iterate over the entries and put it on the index file
        with open (os.path.join('.git', 'index'), 'wb') as f:
            f.write(data[:12])
            for entry in entries:
                # Pack the metadata fields
                print(entry)

                metadata = struct.pack(
                    '!LLLLLLLLLL20sH',
                    entry.ctime_s, entry.ctime_n, entry.mtime_s, entry.mtime_n,
                    entry.dev, entry.ino, entry.mode, entry.uid, entry.gid, entry.size, entry.sha1, 0
                )
                # Write the metadata to the file
                f.write(metadata)
                
                # Convert the path to bytes
                path_bytes = entry.path.encode('utf-8')  # Encode the path as bytes
                f.write(path_bytes)
                
                # Write a null byte (0x00) to terminate the path
                f.write(b'\x00')
                
                # Pad to align to the next 8-byte boundary
                # padding_size = (8 - (len(metadata) + len(path_bytes) + 1) % 8) % 8
                # f.write(b'\x00' * padding_size)
        return
    except Exception as e:
        print('Something went wrong -> write_to_index: ', e)
        exit(0)

def update_index(flag: str, filename: str):

    entries = read_index()
    if flag == '--add':
        upsert_done = upsert_on_index_entries(filename, entries)
        if upsert_done:
            write_to_index(entries)
    elif flag == '--remove':
        print('Not yet supported')

            
        
