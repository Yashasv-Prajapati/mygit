import os
import zlib

# main function to cat the file
def cat_file(flag:str, obj:str):
    try:
        if flag == '-p': # return the content based on the object type automatically
            return cat_blob(obj)
        elif flag == '-t': # returns the type of object
            return cat_object_type(obj)
        else:
            raise ValueError("Unknown flag")

    except UnicodeDecodeError as ud:
        print("Something went wrong due to: ", ud)
    except FileNotFoundError as fnf:
        print("Could find the file corresponding to this hash, make sure you're in the correct directory")
    except Exception as err:
        print(err)
        print("Maybe try the usage as: your_git.sh -p <object>")

    exit(0)

# Figure out the type of object and return the content appropriately
def cat_blob(obj_hash:str):

    __path = os.getcwd() + f'/.git/objects/{obj_hash[:2]}/{obj_hash[2:]}'
    with open(__path, 'rb') as f:
        raw_object_content = zlib.decompress(f.read())

    # for blob file, the format of blob is  -> blob size<null>content
    # first we have to extract the header, then the content
    header, content = raw_object_content.split(b'\x00', maxsplit=1)

    object_type, content_size = header.decode().split()

    if object_type != 'blob':
        return "Not a blob object, current implementation only supports blob objects."

    content = content.decode('utf-8')

    return content

# Figure out the type of object and return the type
def cat_object_type(obj_hash:str):

    __path = os.getcwd() + f'/.git/objects/{obj_hash[:2]}/{obj_hash[2:]}'
    with open(__path, 'rb') as f:
        raw_object_content = zlib.decompress(f.read())

    # for blob file, the format of blob is  -> blob size<null>content
    # first we have to extract the header, then the content
    header, _ = raw_object_content.split(b'\x00', maxsplit=1)

    object_type, _ = header.decode().split()

    return object_type

