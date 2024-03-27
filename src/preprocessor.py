lines = None
with open('input','r') as f:
    lines = f.readlines()
    f.close()
if lines==None:
    raise Exception("Couldn't read")

with open('preprocess-out','w') as f:
    for line in lines:
        if "//" in line:
            line = line.split('//')[0]
            line = line + '\n'
        f.write(line)
    f.close()
