import os
from time import sleep



document = os.path.join(os.path.join(
    os.environ['USERPROFILE']), 'Documents') + '\\' + 'test.test'

desktop = os.path.join(os.path.join(
    os.environ['USERPROFILE']), 'Desktop') + '\\' + 'test.test'


f = open(desktop, "w")
d = open(document, 'w')
while True:
    d.write('sdd')
    f.write('ss')
    sleep(1)
    print(f)
