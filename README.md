## Purpose
Generates random data from a schema. The data can be returned as `INSERT`-statements.
The library also supports generating `DROP`- and `CREATE TABLE`-statements.
Foreign keys are not supported at the time of writing.
But values can be restricted to certain ranges to enforce correlations.

## Usage
Create your schema directly in source. Eg:

```python
import Relation from pggenerator

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
```

Can result in the following output: 
```sql
DROP TABLE persons;
CREATE TABLE persons(name TEXT, income INTEGER, married BOOLEAN, born DATE, x REAL, mostlyNull TEXT);
INSERT INTO persons (VALUES 
 ('FzA5gmY', 38788, False, '1986-04-12', 0.415140, NULL),
 ('gxlCUI', 13205, False, '1973-12-09', -0.119942, NULL),
 ('emJHwn5', 32377, False, '1987-10-17', -0.018303, 'Oi0vZwyIf6UMZeSRnONee2ktRChnmzJrWvx8JV1GSGizxoxCmLD')
);
```