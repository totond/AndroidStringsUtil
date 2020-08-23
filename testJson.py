import json

from json import JSONEncoder
class MyEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

class Person(object):
    def __init__(self):
        self.name = 'John'
        self.age = 25
        self.id = 1


person = Person()

s = json.dumps(person, cls=MyEncoder)
print(s)

# 输出结果
