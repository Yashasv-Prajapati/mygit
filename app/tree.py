import os
import zlib
from cat import cat_object_type

'''
Function to print the tree

The format of tree is:
tree <size>\0
<mode> <name>\0<20_byte_sha>
<mode> <name>\0<20_byte_sha>
'''
def ls_tree(obj_hash:str):
    __path = os.getcwd() + f'/.git/objects/{obj_hash[:2]}/{obj_hash[2:]}'
    with open(__path, 'rb') as f:
        raw_object_content = zlib.decompress(f.read())

    # first we have to extract the header, then the content
    header, content = raw_object_content.split(b'\x00', maxsplit=1)

    object_type, _ = header.decode().split()

    if object_type != 'tree':
        return "Not a tree object"

    '''
    So now the content is in the format:
    <mode> <name>\0<20_byte_sha><mode> <name>\0<20_byte_sha> (repeated)
    20 bytes because the sha is 40 characters long, and each character is 2 bytes long
    '''

    entries = []
    '''
        Find the first space, then find the first null byte
        The mode is from the start to the first space
        The name is from the first space to the first null byte
        The sha is from the first null byte to the next 20 bytes
        Repeat
    '''
    while content:
        space_pos = content.index(b' ')
        null_pos = content.index(b'\x00')

        mode = content[:space_pos].decode()
        name = content[space_pos+1:null_pos].decode()
        sha = content[null_pos+1:null_pos+21].hex()
        entries.append((mode, name, sha))

        content = content[null_pos+21:]

    formatted_string = ''
    for mode, name, sha in entries:
        object_type = cat_object_type(sha)
        formatted_string += f'{mode} {object_type} {sha}\t{name}\n'

    return formatted_string