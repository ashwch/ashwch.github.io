Title: Handling missing keys in str.format_map properly
Date: 2010-12-03
Modified: 2010-12-03
Category: Programming
Tags: python, programming
Slug: handling-missing-keys-in-str-format-map
Authors: Ashwini Chaudhary
Summary: SHandling missing keys in `str.format_map` properly


`str.format_map` was introduced in Python 3.2, it allows users to a pass a dictionary instead of individual keyword arguments. This can be very useful in case some of the format arguments are missing from the dictionary, take this example from docs:

```python
class Default(dict):
    def __missing__(self, key):
        return key

print ('{name} was born in {country}'.format_map(Default(name='Guido'))) 
# Guido was born in country
```

But this fails:

```python
>>> print ('{name} was born in {country.state}'.format_map(Default(name='Guido')))
Traceback (most recent call last):
  File "<ipython-input-324-1012aa68ba8d>", line 1, in <module>
    print ('{name} was born in {country.state}'.format_map(Default(name='Guido')))
AttributeError: 'str' object has no attribute 'state'
```

That is obvious because we are returning a string from `__missing__` and that string doesn't have any attribute of the name state.

Note that the above way is also possible in Python 2 and Python 3.0-3.1 using the [`Formatter`](https://docs.python.org/2/library/string.html#string.Formatter) class's `vformat` method.

```python
from string import Formatter
f = Formatter()
print f.vformat('{name} was born in {country}', (), Default(name='Guido'))
# Guido was born in country
```

Dealing with dot notations, conversions(`!s` or `!r`) and format specs(`^`, `>` etc)

The solution is, for missing keys instead of returning simple string, return an instance of a class that can handle these attribute calls along with creating full string back:

```python
class MissingAttrHandler(object):
    def __init__(self, format):
        self.format = format

    def __getattr__(self, attr):
        return type(self)('{}.{}'.format(self.format, attr))

    def __repr__(self):
        return self.format + '}'


class Default(dict):
    def __missing__(self, key):
        return MissingAttrHandler('{{{}'.format(key))
```

Now let's test this:

```python
>>> print('{name} was born in {country.state} and his last '
          'name is {Person.full_name.last_name}'.format_map(Default(name='Guido')))
Guido was born in {country.state} and his last name is {Person.full_name.last_name}
```

Some of you may have already noticed, this solution has one issue though, it will fail if other formatting details like ^, 10d etc are present:

```python
>>> print('{name} was born in {country.state} and his last '
      'name is {Person.full_name.last_name:*^30}'.format_map(Default(name='Guido')))
Traceback (most recent call last):
  File "<ipython-input-94-b375bfa3e06c>", line 2, in <module>
    'name is {Person.full_name.last_name:*^30}'.format_map(Default(name='Guido')))
TypeError: non-empty format string passed to object.__format__
```

This is because MissingAttrHandler has no `__format__`` method of its own, hence the `__format__` lookup goes to its base class object(`object.__format__`)

```python
>>> MissingAttrHandler.__format__ is object.__format__
True
>>> object.__format__(MissingAttrHandler(''), '^*30s')
Traceback (most recent call last):
  File "<ipython-input-129-c4e00a46bd28>", line 1, in <module>
    object.__format__(MissingAttrHandler(''), '^*30s')
TypeError: non-empty format string passed to object.__format__
```

So, let's define a `__format__`` method in our class that takes care of this:

```python
def __format__(self, format):
        return '{}:{}}}'.format(self.format, format)
```

Let's test it:

```python
>>> print('{name} was born in {country.state} and dict has '
      '{dict.get:*^30} method.'.format_map(Default(name='Guido')))
Guido was born in {country.state:} and dict has {dict.get:*^30} method.
>>> print('{name} was born in {country.state} and dict has '
      '{dict.get:>30d} method.'.format_map(Default(name='Guido')))
Guido was born in {country.state:} and dict has {dict.get:>30d} method.
```

Seems to be working fine, let's try one more thing:

```python
>>> print('{name} was born in {country.state} and dict has '
...       '{dict.get!s:*^30} method.'.format_map(Default(name='Guido')))
Guido was born in {country.state:} and dict has **********{dict.get}********** method.
```

Well this was quite unexpected, what exactly happened there?

Well due to the `!s` present in the format string after getting the value of these fields using either `str()` or `repr()`(which is a string object), Python will now call `__format__` on it with `*^30` as an argument. But as we returned a string object and not a `MissingAttrHandler` object the format call goes to that str.

```python
>>> '{dict.get}'.__format__('*^30')
'**********{dict.get}**********'
```

We can try to return an instance of MissingAttrHandler rather than a string from its `__repr__` method. But to return `MissingAttrHandle` instance from `__str__` or `__repr__` we will have to inherit from str as well because Python expects us to return an instance of type str. Now `__repr__` will look like:


```python
def __repr__(self):
        return MissingAttrHandler(self.format + '!r}')
```

Note that now we need to define `__str__` as well because our class does not inherit from str which provides a `__str__` method, hence calling `__str__` on it won't fallback to `__repr__` anymore.

And one cool thing about `__format__` is that once defined, it is the function that is by default called during string formatting unless we provide `!r` or !s explicitly. If `!r` or `!s` are present on the format string then `__repr__` and `__str__` are called respectively and then `__format__` is called on the resulting object.

Ah! ha that's exactly what we needed right? Using this we can also add !r or !s in our format strings and later complete it with the `__format__` method.

So, in the end our class will look like:

```python
class MissingAttrHandler(str):
    def __init__(self, format):
        self.format = format

    def __getattr__(self, attr):
        return type(self)('{}.{}'.format(self.format, attr))

    def __repr__(self):
        return MissingAttrHandler(self.format + '!r}')

    def __str__(self):
        return MissingAttrHandler(self.format + '!s}')

    def __format__(self, format):
        if self.format.endswith('}'):
            self.format = self.format[:-1]
        return '{}:{}}}'.format(self.format, format)


class Default(dict):
    def __missing__(self, key):
        return MissingAttrHandler('{{{}'.format(key))
```

Let's try it:

```python
>>> print('{name} was born in {country.state} and dict has '
      '{dict.get!r:*^30} method.'.format_map(Default(name='Guido', dct=dict)))
Guido was born in {country.state:} and dict has {dict.get!r:*^30} method.
>>> print('{name} was born in {country.state!r:=20s} and dict has '
      '{dict.get!s:*^30} method.'.format_map(Default(name='Guido', dct=dict)))
Guido was born in {country.state!r:=20s} and dict has {dict.get!s:*^30} method.
```

Works! ;-)

I hope you must have learned something about string formatting in Python with the aforementioned method.

But is there any other way to do this?

### Yes!

## Second way:

We can achieve the same thing as above using [`Formatter`](https://docs.python.org/2/library/string.html#string.Formatter) class from string module, the [`parse()`](https://docs.python.org/2/library/string.html#string.Formatter.parse) method of this class can be used to parse the format string. It returns an iterable that yields a tuple containing (literal_text, field_name, format_spec, conversion). We can use these fields to re-create our string.

```python
from functools import reduce
from operator import attrgetter
from string import Formatter


def get_field_value(field_name, mapping):
    try:
        if '.' not in field_name:
            return mapping[field_name], True
        else:
            obj, attrs = field_name.split('.', 1)
            return attrgetter(attrs)(mapping[obj]), True
    except Exception as e:
        return field_name, False



def str_format_map(format_string, mapping):
    f = Formatter()
    parsed = f.parse(format_string)
    output = []
    for literal_text, field_name, format_spec, conversion in parsed:
        conversion = '!' + conversion if conversion is not None else ''
        format_spec = ':' + format_spec if format_spec else ''
        if field_name is not None:
            field_value, found = get_field_value(field_name, mapping)
            if not found:
                text = '{{{}{}{}}}'.format(field_value,
                                           conversion,
                                           format_spec)
            else:
                format_string = '{{{}{}}}'.format(conversion, format_spec)
                text = format_string.format(field_value)
        output.append(literal_text + text)
        text = ''
    return ''.join(output)
```

Demo:

```python
>>> s = '{name} was born in {country.state} and dict has {dict.get!r:*^30} method.'
>>> print(str_format_map(s, dict(dict=dict, name="guido")))
guido was born in {country.state} and dict has <method 'get' of 'dict' objects> method.
>>> s = '{name} was born in {country.state!r:=20s} and dict has {dict.get!s:*^30} method.'
>>> print(str_format_map(s, dict(dct=dict, name="guido")))
guido was born in {country.state!r:=20s} and dict has {dict.get!s:*^30} method.
```
