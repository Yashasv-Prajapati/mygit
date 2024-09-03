'''
Main Entry Point For the Project
'''
import sys
from init import init
from hash import hash_object
from cat import cat_file
from tree import ls_tree
from index import update_index

def main():

    command = sys.argv[1]
    # my_git init
    if command == "init":
        init()

    # my_git cat-file -p <object>(SHA1)
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
        obj_hash = sys.argv[2]
        print(ls_tree(obj_hash))

    elif command == "update-index":
        flag = sys.argv[2]
        filenames = sys.argv[3:]
        if flag not in ['--add', '--remove']:
            raise ValueError('Flag corresponding to this command is not recognized.\nUsage: mygit update-index --add or mygit update-index --remove')
        update_index(flag, filenames)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
