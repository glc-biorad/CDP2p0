
import sys 

def update_version_in_file(version, filename):
    with open(filename, 'r') as f:
        filedata = f.read()
 
    import re
    filedata = re.sub(r'(App_Version=)(.*)(\n*)', r'\1'+version+r'\3', filedata)
        
    with open(filename, 'w') as f:
        f.write(filedata)
        
    

        
#accept version and filename from the command line and call update_version_in_file() to update the version in the file.

version = sys.argv[1]
filename = sys.argv[2]
update_version_in_file(version, filename)

