from collections import namedtuple
from utils.reader import read_file
import os
import struct
from hash import hash_object
from utils.transformers import hex_to_binary, binary_to_hex, string_to_binary, binary_to_string

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
            ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1, flag = struct.unpack('!LLLLLLLLLL20sH', data_entries[start:end])
            
            # start from end index and search for first \x00 - this will mark the end index of the filepath of each entry
            filepath_end_index = data_entries.index(b'\x00', end)
            
            # Extract the filepath name from the index entry 
            filepath = binary_to_string(data_entries[end: filepath_end_index])
            filepath_bytes = filepath_end_index - end

            index_entries.append(IndexEntry(ctime_s,ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, binary_to_hex(sha1), filepath))
            
            length = ((62 + len(filepath) + 8) // 8) * 8
            start += length

        assert len(index_entries) == num_of_entries
        return index_entries
            
    except FileNotFoundError as f:
        print('File not found')
        exit(0)
    
def upsert_on_index_entries_list(filename:str, entries: list[IndexEntry]):
    try:
        # Get filepath and stat info
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

        # sha1 hash of the file - 40 character hexadecimal string
        sha1_hash = hash_object('unknown', filename)

        # create a new entry tuple
        entry_to_upsert = IndexEntry(ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, sha1_hash, filename)

        # check whether to update the index or add a new entry of the file
        to_update = any(filename == entry.path for entry in entries)

        if to_update:
            for index in range(len(entries)):
                if entries[index].path == filename:
                    entries[index] = entry_to_upsert
                    return True
        
        # if not update then create a new entry for the file
        entries.append(entry_to_upsert)
        return True
    except FileNotFoundError as fnf:
        print(f"File not Found -> {filename} -> upsert_on_index_entries")
        exit(0)
    except Exception as e:
        print("Something went wrong -> upsert_on_index_entries: ", e)
        exit(0)                    

def write_to_index_file(entries: list[IndexEntry]):
    try:
        # get binary data from index file
        data = read_file(os.path.join('.git', 'index'))

        # read important starting headers and verify them 
        signature, version_number, num_of_entries = struct.unpack('!4sLL', data[:12])

        assert signature == b'DIRC', f'Invalid signature: {signature}'
        assert version_number == 2, f'Invalid version number: {version_number}'

        # Now to update the index entries 
        with open (os.path.join('.git', 'index'), 'wb') as f:
            header = struct.pack('!4sLL', signature, version_number,len(entries))
            f.write(header)
            
            for entry in entries:
                # Pack the metadata fields
                sha1_binary = hex_to_binary(entry.sha1)
                metadata = struct.pack(
                    '!LLLLLLLLLL20sH',
                    entry.ctime_s, entry.ctime_n, entry.mtime_s, entry.mtime_n,
                    entry.dev, entry.ino, entry.mode, entry.uid, entry.gid, entry.size, sha1_binary, 0
                )
                # Write the metadata to the file
                f.write(metadata)
                
                # Convert the path to bytes
                path_bytes = string_to_binary(entry.path)  # Encode the path as bytes
                f.write(path_bytes)
                
                # Write a null byte (0x00) to terminate the path
                f.write(b'\x00')
                
                # Pad to align to the next 8-byte boundary
                padding_size = (8 - (len(metadata) + len(path_bytes) + 1) % 8) % 8
                f.write(b'\x00' * padding_size)
        return
    except Exception as e:
        print('Something went wrong -> write_to_index: ', e)
        exit(0)

def update_index(flag: str, filenames: list[str]):
    entries = read_index()
    if flag == '--add':
        '''
            -> Iterate over each file and add it to the index
            -> `upsert_on_index_entries_list` -> returns a boolean based on the status of upsert of a file
            -> If some file fails the upsert process, we get a False
            -> So then rollback the entire index update and exit
        '''
        for filename in filenames:
            if not upsert_on_index_entries_list(filename, entries):
                print("Upsert failed for file", filename, " Aborting entire update-index")
                exit(0)

        # Finally if everything is good, write entries to the index file
        write_to_index_file(entries)
    elif flag == '--remove':
        #TODO - remove_from_index_entries_list
        for filename in filenames:
            if not remove_from_index_entries_list(filename, entries):
                print("Deleting failed on file", filename, " Aborting entire update-index")
                exit(0)
        write_to_index_file(entries)

            
        
