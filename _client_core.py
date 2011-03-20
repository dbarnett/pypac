from xmlrpclib import ServerProxy

s = ServerProxy('http://localhost:8888')

def up():
    return s.move('u')

def down():
    return s.move('d')

def left():
    return s.move('l')

def right():
    return s.move('r')

def wait():
    return s.move('.')

def whereAmI():
    return s.get_pos()

def checkMap():
    return s.get_map()
