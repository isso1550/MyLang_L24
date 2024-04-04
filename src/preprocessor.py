import sys

input_file = "input"
if (len(sys.argv)>1):
    input_file = sys.argv[1]


lines = None
with open(input_file,'r') as f:
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
