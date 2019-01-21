import random as rand
import time
import datetime as dt

class Field(object):
    def __init__(self, name, nullChance = 0, unique = False):
        self.name = name
        self.generated = []
        self.nullChance = nullChance
        self.relation = None
        self.unique = unique

    def fieldType(self):
        raise "Not implemented"

    def schema(self):
        return "%s%s" % (self.fieldType(), (" UNIQUE" if self.unique else ""))

    def generateNonNull(self):
        raise "Not implemented"

    def generate(self):
        val = "NULL" if rand.random() < self.nullChance else self.generateNonNull()
        self.generated.append(val)
        return val

class IntField(Field):
    def __init__(self, name, minVal = -2147483648, maxVal = 2147483647, nullChance = 0, unique = False):
        super(IntField, self).__init__(name, nullChance, unique)
        self.min = minVal
        self.max = maxVal

    def fieldType(self):
        return "INTEGER"

    def generateNonNull(self):
        return rand.randint(self.min, self.max)

class RealField(Field):
    def __init__(self, name, precision = 6, minVal = -2147483648.0, maxVal = 2147483647.0, nullChance = 0, unique = False):
        super(RealField, self).__init__(name, nullChance, unique)
        self.format = "{:.%sf}" % (precision,)
        self.min = minVal
        self.max = maxVal

    def fieldType(self):
        return "REAL"

    def generateNonNull(self):
        return self.format.format(rand.uniform(self.min, self.max))

class BooleanField(Field):
    def __init__(self, name, chanceForTrue = 0.5, nullChance = 0, unique = False):
        super(BooleanField, self).__init__(name, nullChance, unique)        
        self.chanceForTrue = chanceForTrue

    def fieldType(self):
        return "BOOLEAN"

    def generateNonNull(self):
        return rand.random() <= self.chanceForTrue

class TextField(Field):
    def __init__(self, name, minLength = 0, maxLength = 255, letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", nullChance = 0, unique = False):
        super(TextField, self).__init__(name, nullChance, unique)
        self.minLength = minLength
        self.maxLength = maxLength
        self.letters = letters

    def fieldType(self):
        return "TEXT"

    def generateNonNull(self):
        return "'%s'" % (''.join([rand.choice(self.letters) for _ in range(rand.randint(self.minLength, self.maxLength))]),)

class DateField(Field):
    def __init__(self, name, earliest, latest, nullChance = 0, unique = False):
        '''
        Both dates are expected to be a triple (year, month, day)
        '''
        super(DateField, self).__init__(name, nullChance, unique)
        self.earliest = time.mktime(earliest + (0,0,0,0,0,0)) # append hour, minute, second, ...
        self.latest = time.mktime(latest + (0,0,0,0,0,0))

    def fieldType(self):
        return "DATE"

    def generateNonNull(self):
        return "'%s'" % (dt.datetime.fromtimestamp(rand.randint(self.earliest, self.latest)).strftime('%Y-%m-%d'),)

class SerialField(Field):
    def __init__(self, name, startValue = 1, nullChance = 0):
        super(SerialField, self).__init__(name, nullChance, True)
        self.current = startValue

    def fieldType(self):
        return "SERIAL"

    def generateNonNull(self):
        val = self.current
        self.current += 1
        return val

class ForeignKeyField(Field):
    '''
    keep in mind, when generating tuples for a relation with a ForeignKeyField,
    at least some tuples for the referenced Field must be created already.
    Naturally, the values for the ForeignKeyField will only be whatever has been
    created up to that point in the referenced Field.
    The type of the field will obviously be the same as the referenced field.
    '''
    def __init__(self, name, reference, nullChance = 0, unique = False):
        super(ForeignKeyField, self).__init__(name, nullChance, unique)
        if not reference.unique:
            raise Exception("Can not reference non-UNIQUE field '%s'" % (str(reference.name,)))
        self.reference = reference

    def schema(self):
        return "%s REFERENCES %s(%s)" % (self.reference.fieldType(), self.reference.relation.name, self.reference.name)

    def generateNonNull(self):
        assert len(self.reference.generated) > 0
        return rand.choice(self.reference.generated)

class Relation(object):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
        for f in fields:
            f.relation = self

    def field(self, fname):
        for f in self.fields:
            if f.name == fname:
                return f
        return None

    def create(self):
        return "CREATE TABLE %s(%s);" % (self.name, ', '.join(["%s %s" % (f.name,f.schema()) for f in self.fields]))

    def drop(self, cascade = False):
        return "DROP TABLE %s %s;" % (self.name, ("CASCADE" if cascade else ""))

    def insert(self, n):
        tuples = []
        for i in range(n):
            tuples.append(', '.join([str(v.generate()) for v in self.fields]))
        return "INSERT INTO %s (VALUES \n %s\n);" % (self.name, ',\n '.join("(%s)" % (t,) for t in tuples))

def main():
    # print(DateField("some_data", (1990,12,1), (2007,1,1)).generate())
    # print(TextField("some_text", 20).generate())
    # print(BooleanField("some_bool", 0.5).generate())
    # print(IntField("some_int", 10,100).generate())
    # print(RealField("some_real", 6,-10,10).generate())

    r1 = Relation("persons", [
            TextField("name", minLength = 5, maxLength = 10, unique = True),
            IntField("income", 10000, 40000),
            BooleanField("married", 0.3),
            DateField("born", (1970,1,1),(2010,4,10)),
            RealField("x", 6,-1,1),
            TextField("mostlyNull", nullChance = 0.95),
            SerialField("id")
        ])

    r2 = Relation("orders", [
            ForeignKeyField("pid", r1.field("id")),
            IntField("quantity", 1,10),
            TextField("article", maxLength = 20)
        ])

    r3 = Relation("workers", [
            ForeignKeyField("worker", r1.field("name")),
            ForeignKeyField("boss", r1.field("name"))
        ])

    print(r1.drop(True))
    print(r1.create())
    print(r1.insert(20))

    print(r2.drop(True))
    print(r2.create())
    print(r2.insert(1000))

    print(r3.drop(True))
    print(r3.create())
    print(r3.insert(50))

if __name__ == '__main__':
    main()