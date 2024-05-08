# Content from: ./.merged_py_file.py


# Content from: ./Docify-Combiner.py
import os
FINAL = "."
def copy_py_files(directory, output_file):
    with open(output_file, 'w') as output:
        for root, _, files in os.walk(directory):
            for filename in sorted(files):
                if filename.endswith(".py") and filename != "Dockify-Combiner.py":
                    file_path = os.path.join(root, filename)
                    print(file_path)
                    with open(file_path, 'r') as file:
                        output.write("# Content from: {}\n".format(file_path))
                        output.write(file.read())
                        output.write("\n\n")
                        

                        
def list_folders_and_files():
    """
    Lists all folders and files in the current directory.
    """
    items = os.listdir()
    folders = [item for item in items if os.path.isdir(item)]
    files = [item for item in items if os.path.isfile(item)]
    return folders, files

def navigate():
    """
    Allows the user to navigate through folders and files.
    """
    global FINAL
    while True:
        print("\nCurrent Directory Contents:")
        folders, files = list_folders_and_files()
        print("Folders:")
        for folder in folders:
            print(folder + "/")
        print("\nFiles:")
        for file in files:
            print(file)
        
        choice = input("\nEnter folder or file name to navigate (or press Enter to exit): ")
        if choice == "":
            # return os.path.abspath(choice)
            break
        elif os.path.isdir(choice):
            os.chdir(choice)
        elif os.path.isfile(choice):
            return os.path.abspath(choice)
        else:
            print("Invalid choice. Please enter a valid folder or file name.")


def main():
    # source_directory = input("Enter directory name (. for current directory): \n") 
    output_file = ".merged_py_file.py"
    # source_directory = navigate()
    source_directory = "."

    copy_py_files(source_directory, output_file)
    print("All .py files copied to {}".format(output_file))

if __name__ == "__main__":
    main()


# Content from: ./app/cat.py
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
    except Exception as err:
        print(err)
        print("Maybe try the usage as: your_git.sh -p <object>")

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



# Content from: ./app/hash.py
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

    # hashing to get 40 character sha1 checksum hash
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

# Content from: ./app/init.py
import os

def init():
    if os.path.exists(".git"):
        raise FileExistsError("Already a git repository")
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/objects/info")
    os.mkdir(".git/objects/pack")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")

# Content from: ./app/main.py
import sys
from init import init
from hash import hash_object
from cat import cat_file
from tree import ls_tree

def main():

    command = sys.argv[1]
    # my_git init
    if command == "init":
        init()
    # my_git cat-file -p <object>
    elif command == "cat-file":
        flag = sys.argv[2]
        obj = str(sys.argv[3])
        cat_content = cat_file(flag, obj)
        print(cat_content, end="")
    # my_git hash-object -w filename
    elif command == "hash-object":
        flag = sys.argv[2]
        filename = sys.argv[3]
        sha1_hash = hash_object(flag, filename)
        print(sha1_hash)
    elif command == "ls-tree":
        obj = sys.argv[2]
        print(ls_tree(obj))
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()


# Content from: ./app/tree.py
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

