
# My Git

For learning how git works internally and to implement the basic git commands.

The entry point for the Git implementation is in `app/main.py`

# Running locally

To initialize a git repository
``` 
python3 app/main.py init
```

To hash_object
```
python3 app/main.py hash_object -w <file_path>
```

To cat_file
```
python3 app/main.py cat_file -p <hash>
```

To print tree
```
python3 app/main.py ls-tree <hash-of-tree>
```


# Using the provided script [breaking currently]
I suggest executing `mygit.sh` in a different folder when testing locally.
For example:

```sh
mkdir -p /tmp/testing && cd /tmp/testing
/path/to/your/repo/mygit.sh init
```

To make this easier to type out, you could add a
[shell alias](https://shapeshed.com/unix-alias/):

```sh
alias mygit=/path/to/your/repo/mygit.sh

mkdir -p /tmp/testing && cd /tmp/testing
mygit init
```
