import sys
from git_internals import init, cat_file, hash_object

def main():

    command = sys.argv[1]

    if command == "init": # my_git init
        init()

    elif command == "cat-file": # my_git cat-file -p <object>
        flag = sys.argv[2]
        obj = str(sys.argv[3])
        cat_content = cat_file(flag, obj)
        print(cat_content, end="")

    elif command == "hash-object": # my_git hash-object -w filename
        flag = sys.argv[2]
        filename = sys.argv[3]
        sha1_hash = hash_object(flag, filename)
        print(sha1_hash)

    else:
        raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
