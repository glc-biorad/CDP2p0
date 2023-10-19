
import sys

def add_or_update_version_in_file(version, filename):
    with open(filename, 'r') as f:
        filedata = f.read()
 
    import re
    if filedata.find('\n# Version: ')  >= 0:
        filedata = re.sub(r'(\n# Version: )(.*)(\n*)', r'\1'+version+r'\3', filedata)
    else:
        filedata = '\n# Version: ' + version + '\n' + filedata  
        
    with open(filename, 'w') as f:
        f.write(filedata)
        
def update_version_in_py_files(version, path):
    # Get all the .py files in the path, loop through them
    # and update the version in each file.
    import os
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                filename = os.path.join(root, file)
                print(filename + '\n' )
                add_or_update_version_in_file(version, filename)
                   


version = sys.argv[1]
path = sys.argv[2]
update_version_in_py_files(version, path)

