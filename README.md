## Purpose
Generates random data from a schema. The data can be returned as `INSERT`-statements.
The library also supports generating `DROP`- and `CREATE TABLE`-statements.
Names are not put between backticks, so you can deliberately break this tool by using reserved words as names for relations or fields.

## Usage
Create your schema directly in source. Each relation accepts a name and a list of fields, whereas each field accepts several type-specific parameters. Eg:

```python
from pggenerator import *

    r1 = Relation("persons", [
            TextField("name", minLength = 5, maxLength = 10),
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

    print(r1.drop())
    print(r1.create())
    print(r1.insert(3))

    print(r2.drop())
    print(r2.create())
    print(r2.insert(1))

    print(r3.drop())
    print(r3.create())
    print(r3.insert(1))
```

Can result in the following output: 
```sql
DROP TABLE persons;
CREATE TABLE persons(name TEXT, income INTEGER, married BOOLEAN, born DATE, x REAL, mostlyNull TEXT, id INTEGER);
INSERT INTO persons (VALUES 
 ('NJnHH6', 15672, True, '2008-04-14', 0.733117, NULL, 1),
 ('NOxNW', 17654, False, '1996-05-02', 0.215981, NULL, 2),
 ('qbDG8B5hWq', 11499, False, '1998-10-17', 0.697616, NULL, 3)
);
DROP TABLE orders;
CREATE TABLE orders(pid INTEGER REFERENCES persons(id), quantity INTEGER, article TEXT);
INSERT INTO orders (VALUES 
 (2, 5, 'tv4OEUw')
);
DROP TABLE workers;
CREATE TABLE workers(worker TEXT REFERENCES persons(name), boss TEXT REFERENCES persons(name));
INSERT INTO workers (VALUES 
 ('qbDG8B5hWq', 'qbDG8B5hWq')
);
```

## Supported Types
This data generator only supports a limited number of built-in types.

- Integer
- Real
- Boolean
- Date
- Text
- Serial
- Foreignkey

Most of these do the obvious. Parameters are explained in the following section.
Each field takes a name as first parameter and an optional names parameter `nullChance` (which is 0 per default) which
expects a number between 0 and 1 to determine whether a value in this field is `NULL`.
All data types also take a parameter `unique`, which is **just a flag** that will append the string `UNIQUE` to the field.
It is required to make a field that is target of a `ForeignKey` unique to comply with Postgres.
**This does not guarantee actual uniqueness within the data!** If you use this flag, manual post processing may be required.
`Serial` is the only data type that (coincidentally) provides real uniqueness.
Most parameters in the following sections have appropriate default values to reflect behaviour as could be expected in PostgreSQL
(eg integers ranging from -2147483648 to 2147483647) as mentioned in [the docs](https://www.postgresql.org/docs/10/static/datatype-numeric.html)).

### IntField
- `minVal`: minimum value this field produces (default: -2147483647)
- `maxVal`: maximum value this field produces (default: 2147483648)

### RealField
- `precision`: decimals
- `minVal`: minimum value this field produces (default: -2147483647.0)
- `maxVal`: maximum value this field produces (default: 2147483648.0)

### BoolField
- `chanceForTrue`: number between 0 and 1 that reflects the chance that this field produces true (default: 0.5)

### TextField
- `minLength`: minimal length text in this field has (default: 0)
- `maxLength`: maximal length text in this field has (default: 255),
- `letters`: alphabet to draw letters from (default: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")

### DateField
- `earliest`: earliest date this field produces, in the form of a tuple `(y,m,d)`
- `latest`: latest date this field produces, in the form of a tuple `(y,m,d)`

### SerialField
- `startValue`: the first value this field produces (default: 1)

Serials go up in increments of 1.

### ForeignKey
- `references`: a field-object this field draws its values from

ForeignKey is a bit special in that it assumes the type of whatever field it references.
It will check for referential integrity and as such will only select values from the referenced field from whatever has been created up until there.
For example:

```python
r1 = Relation(IntField("x"))
r2 = Relation(ForeignKey("ref", r1.field("x")))

r1.insert(1)
r2.insert(100)
r1.insert(100)
```

`r2(ref)` will only contain references to the first value created in `r1`, as the other 100 were not known at the time the tuples in `r2` were created.
