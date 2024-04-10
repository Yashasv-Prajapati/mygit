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