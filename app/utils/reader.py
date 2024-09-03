def read_file(filename:str):
    try:
        with open(filename, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError('File not found')
    except Exception as e:
        raise Exception()