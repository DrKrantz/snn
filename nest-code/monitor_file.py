file = 'brunel-py-ex-12502-0.gdf'

while True:
    try:
        f = open(file, 'r+')

        lines = f.readlines()
        if lines:
            print(lines)
            lines = ''
            f.write(lines)
        f.close()
    except IOError:
        pass
