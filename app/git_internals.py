import os
import zlib
import hashlib

def hash_object(flag:str, filename:str):
    # first open the file content and store it
    __pathname = os.getcwd()
    with open(__pathname + f'/{filename}') as f:
        content = f.read()

    # for blob file, the format of blob is  -> blob size<null>content
    # first we have to extract the header, then the content
    header = f'blob {len(content)}\x00'
    content = header + content

    #encoding is needed for compression and hashing
    encoded_content = content.encode('utf-8')

    # hashing to get 40 character sha1 hash
    sha1_hash = hashlib.sha1(encoded_content)
    sha1_hash = sha1_hash.hexdigest()

    # compress to store as blob object
    compressed_content = zlib.compress(encoded_content)

    # create dir and write object file
    if not os.path.isdir(__pathname + f'/.git/objects/{sha1_hash[:2]}'):
        os.mkdir(__pathname + f'/.git/objects/{sha1_hash[:2]}')

    with open(__pathname + f'/.git/objects/{sha1_hash[:2]}/{sha1_hash[2:]}', 'wb+') as f:
        f.write(compressed_content)

    return sha1_hash

def cat_file(flag:str, obj:str):
    try:
        __path = os.getcwd() +  f'/.git/objects/{obj[:2]}/{obj[2:]}'
        with open(__path, 'rb') as f:
            raw_object_content = zlib.decompress(f.read())

        # for blob file, the format of blob is  -> blob size<null>content
        # first we have to extract the header, then the content
        header, content = raw_object_content.split(b'\x00', maxsplit=1)

        object_type, content_size = header.decode().split()

        content = content.decode()

        return content
    except UnicodeDecodeError as ud:
        print("Something went wrong due to: ", ud)
    except Exception as err:
        print(err)
        print("Maybe try the usage as: your_git.sh -p <object>")

def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")