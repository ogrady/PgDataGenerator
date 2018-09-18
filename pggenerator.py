import random as rand
import time
import datetime as dt

class Field(object):
    def __init__(self, nullChance = 0):
        self.nullChance = nullChance

    def schema(self):
        raise "Not implemented"

    def generateNonNull(self):
        raise "Not implemented"

    def generate(self):
        return "NULL" if rand.random() < self.nullChance else self.generateNonNull()  

class IntField(Field):
    def __init__(self, minVal = -2147483648, maxVal = 2147483647, nullChance = 0):
        super(IntField, self).__init__(nullChance)
        self.min = minVal
        self.max = maxVal

    def schema(self):
        return "INTEGER"

    def generateNonNull(self):
        return rand.randint(self.min, self.max)

class RealField(Field):
    def __init__(self, precision = 6, minVal = -2147483648.0, maxVal = 2147483647.0, nullChance = 0):
        super(RealField, self).__init__(nullChance)
        self.format = "{:.%sf}" % (precision,)
        self.min = minVal
        self.max = maxVal

    def schema(self):
        return "REAL"

    def generateNonNull(self):
        return self.format.format(rand.uniform(self.min, self.max))

class BooleanField(Field):
    def __init__(self, chanceForTrue = 0.5, nullChance = 0):
        super(BooleanField, self).__init__(nullChance)        
        self.chanceForTrue = chanceForTrue

    def schema(self):
        return "BOOLEAN"

    def generateNonNull(self):
        return rand.random() <= self.chanceForTrue

class TextField(Field):
    def __init__(self, minLength = 0, maxLength = 255, letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", nullChance = 0):
        super(TextField, self).__init__(nullChance)
        self.minLength = minLength
        self.maxLength = maxLength
        self.letters = letters

    def schema(self):
        return "TEXT"

    def generateNonNull(self):
        return "'" + ''.join([rand.choice(self.letters) for _ in range(rand.randint(self.minLength, self.maxLength))]) + "'"

class DateField(Field):
    def __init__(self, earliest, latest, nullChance = 0):
        '''
        Both dates are expected to be a triple (year, month, day)
        '''
        super(DateField, self).__init__(nullChance)
        self.earliest = time.mktime(earliest + (0,0,0,0,0,0)) # append hour, minute, second, ...
        self.latest = time.mktime(latest + (0,0,0,0,0,0))

    def schema(self):
        return "DATE"

    def generateNonNull(self):
        return "'" + dt.datetime.fromtimestamp(rand.randint(self.earliest, self.latest)).strftime('%Y-%m-%d') + "'"

class SerialField(Field):
    def __init__(self, startValue = 1, nullChance = 0):
        super(SerialField, self).__init__(nullChance)
        self.current = startValue

    def schema(self):
        return "INTEGER"

    def generateNonNull(self):
        val = self.current
        self.current += 1
        return val

class Relation(object):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def create(self):
        return "CREATE TABLE %s(%s);" % (self.name, ', '.join(["%s %s" % (k,v.schema()) for k,v in self.fields.items()]))

    def drop(self):
        return "DROP TABLE %s;" % (self.name)

    def insert(self, n):
        tuples = []
        for i in range(n):
            tuples.append(', '.join([str(v.generate()) for v in self.fields.values()]))
        return "INSERT INTO %s (VALUES \n %s\n);" % (self.name, ',\n '.join("(%s)" % (t,) for t in tuples))

# print(DateField((1990,12,1), (2007,1,1)).generate())
# print(TextField(20).generate())
# print(BooleanField(0.5).generate())
# print(IntField(10,100).generate())
# print(RealField(6,-10,10).generate())

"""
# usage example:
r = Relation("persons", {
        "name": TextField(minLength = 5, maxLength = 10),
        "income": IntField(10000, 40000),
        "married": BooleanField(0.3),
        "born": DateField((1970,1,1),(2010,4,10)),
        "x": RealField(6,-1,1),
        "mostlyNull": TextField(nullChance = 0.95)
    })

print(r.drop())
print(r.create())
print(r.insert(3))
"""