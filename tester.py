from time import sleep


f = open("./test.test", "w")
while True:
    f.write('ss')
    sleep(1)
    print(f)