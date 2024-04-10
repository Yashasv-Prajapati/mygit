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
