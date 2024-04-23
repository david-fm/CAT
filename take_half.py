import os

if __name__ == '__main__':
    
    fh = open('/Users/davidflorezmazuera/Downloads/spanish-corpora/raw/all_wikis.txt', 'rt')
    line = fh.readline()

    with open('output.txt', 'w') as f:
        # write till output.txt is 100MB
        while os.path.getsize('output.txt') < 1024*1024*100:
            f.write(line)
            line = fh.readline()
        