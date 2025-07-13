Title: Become a pdb power-user
Date: 2016-11-08
Modified: 2023-11-26
Category: Programming
Tags: python, programming, debugging, pdb, ipdb
Slug: become-a-pdb-power-user
Authors: Ashwini Chaudhary
Summary: Become a pdb power-user

This is an explanatory article related to my talk at [MUPy](https://www.pypals.org/mupy)  -- [ Become a pdb power-user](http://slides.com/ashwch/pdb-mupy#/).

This article was originally published on [Medium](https://medium.com/instamojo-matters/become-a-pdb-power-user-e3fc4e2774b2)

## Table of Contents

1. [What's pdb?](#whats-pdb)
2. [Why pdb?](#why-pdb)
3. [How to start pdb?](#how-to-start-pdb)
   - [Starting program under debugger control](#starting-program-under-debugger-control)
   - [Running code under debugger control](#running-code-under-debugger-control)
   - [Set a hardcoded breakpoint](#set-a-hardcoded-breakpoint)
   - [Post-mortem debugging](#post-mortem-debugging)
4. [Basic pdb commands](#basic-pdb-commands)
   - [Stepping through code](#stepping-through-code)
   - [Jumping between stacks](#jumping-between-stacks)
   - [Breakpoints](#breakpoints)
   - [Tips and tricks](#tips-and-tricks)
   - [What's new in Python 3](#whats-new-in-python-3)

---

## What's pdb?

`pdb` is a module from Python's standard library that allows us to do things like:

- Stepping through source code
- Setting conditional breakpoints
- Inspecting stack trace
- Viewing source code
- Running Python code in a context
- Post-mortem debugging

## Why pdb?
It is not necessary to use `pdb` all the time, sometimes we can get away with simple `print` statements or logging.

But these other approaches are most of the time not good enough and don't give us enough control while debugging. Plus after debugging we also have to take care of removing the `print`` statements that we had added to our program just for debugging purpose, this isn't true for logging though as we can filter out logs easily. But at the end both of these approaches clutter our code and don't give us enough debugging power either.


## How to start pdb?

There are multiple ways to start pdb depending on your use case.

### 1. Starting program under debugger control
We can start a script itself under debugger's control by executing the script using `-m pdb` argument. Let's run script.py:

```bash
$ python -m pdb script.py
 > /pdb-mupy/script.py(1)<module>()
 -> """I am the first script in this demo"""
 (Pdb)
```

In this mode Python will stop the program on first line and you are going to be inside debugger(`(Pdb)` is pdb's prompt). At this point you can either set breakpoints or continue executing your program.

Another special thing about it is that after the program completion if no exception occurred then your program will restart in same mode otherwise it will start in post-mortem mode. After post-mortem mode you can restart the program again.

### 2. Running code under debugger control
Instead of running the whole code under debugger control we can run particular code under using `pdb.run`, `pdb.runeval` and `pdb.runcall`.

```python
>>> import pdb
>>> import script
>>> pdb.run('script.divide(10, 5)')
> <string>(1)<module>()->None
(Pdb) s   # we can run any pdb command here
--Call--
> /pdb-mupy/script.py(6)divide()
-> def divide(numerator, denominator):
(Pdb) n
> /pdb-mupy/script.py(7)divide()
-> return numerator / denominator
(Pdb) p numerator, denominator
(10, 5)
(Pdb) c
>>>
```

Here `<string>(1)<module>()` means that we are at the start of string passed to `run()` and no code has executed yet. In the above example we stepped into the divide function using `s`(don't worry about `s`, `n`, `c` etc, we will be covering them in detail).

`runeval()` does the same thing as `run()` except that it also returns the value of executed code.

`runcall()` allows us to pass a Python callable itself instead of a string.

```python
>>> pdb.runcall(script.divide, 10, 5)
> /pdb-mupy/script.py(7)divide()
-> return numerator / denominator
(Pdb)
```

### 3. Set a hardcoded breakpoint
This is the most common way to debug programs, it basically involves adding the line pdb.set_trace() in the source code wherever we want our program to stop.


### 4. Post-mortem debugging
Post-mortem debugging allows us to debug a dead program using its `traceback` object. In post-mortem debugging we can inspect the state of the program at the time it died. But apart from inspecting the state we can't do much here(like stepping through the code) because like the name suggests we are performing post-mortem of a dead program.

By default the `-m pdb` we had discussed earlier puts us in post-mortem mode if an exception occurs. Other ways are using: `pdb.pm()` and `pdm.post_mortem()`.

`pdb.pm()` will take us to the post-mortem mode for the exception found in `sys.last_traceback`.

On the other hand `pdb.post_mortem()` excepts an optional `traceback` object otherwise will try to handle the exception currently being handled.

```python
>>> import pdb
>>> import script
>>> script.divide(10, 0)
Traceback (most recent call last):
  File "<ipython-input-8-fe270324adad>", line 1, in <module>
    script.divide(10, 0)
  File "script.py", line 7, in divide
    return numerator / denominator
ZeroDivisionError: integer division or modulo by zero
```

Now to inspect the state at the time this above exception occurred using `pdb.pm()`.

```python
>>> pdb.pm()
> /Users/ashwini/work/instamojo/pdb-mupy/script.py(7)divide()
-> return numerator / denominator
(Pdb) args  # Arguments passed to the function at that time
numerator = 10
denominator = 0
```

We could have done something similar using `pdb.post_mortem()` with the `traceback` object:

```python
>>> import sys
>>> pdb.post_mortem(sys.last_traceback)
> /Users/ashwini/work/instamojo/pdb-mupy/script.py(7)divide()
-> return numerator / denominator
(Pdb)
```

Similarly we can handle the current exception being handled using `pdb.post_mortem()` without any argument:

```python
>>> try:
...     script.divide(10, 0)
... except Exception:
...     pdb.post_mortem()
...
> /Users/ashwini/work/instamojo/pdb-mupy/script.py(7)divide()
-> return numerator / denominator
(Pdb)
```


## Basic pdb commands
`(Pdb)` prompt we have seen so far is pdb's own shell and it has its own set of commands that makes debugging even easier. In this section we will go through some of the basic commands.

Before starting with the commands it is important to understand the notation we use for commands, for example a command like `c`(`ont`(`inue`)) means we can either use `c`, `cont` or `continue` for this command. The square brackets(`[]`) followed by a command are its optional arguments, without square brackets it is a compulsory argument.

- `h(elp) [command]`

- `help` or simply `h` provides help related to a `pdb` command. Without arguments it lists all of the pdb commands available.

- (Pdb) help

```
Documented commands (type help <topic>):
========================================
EOF    c          d        h         list      q        rv       undisplay
a      cl         debug    help      ll        quit     s        unt
alias  clear      disable  ignore    longlist  r        source   until
args   commands   display  interact  n         restart  step     up
b      condition  down     j         next      return   tbreak   w
break  cont       enable   jump      p         retval   u        whatis
bt     continue   exit     l         pp        run      unalias  where
```

Get help related to args command:
- `(Pdb) help args`

```
(Pdb) help args
a(rgs)
        Print the argument list of the current function.
```

This command can save your time related to visiting Python documentation in case you forgot about a command.

Note: `!` command is the only exception here as help only works with valid Python identifiers. Alternative is to use `help exec`.


- `p` or `pp`

To print variable inside debugger we can use `p` for normal printing and pp for pretty-printing. We can use simple Python print as well but it is not a pdb command.

- `a(rgs)`

`args` prints the arguments with their values of the current function.

```python
>>> pdb.runcall(script.divide, 10 , 15)
> /pdb-mupy/script.py(7)divide()
-> return numerator / denominator
(Pdb) args
numerator = 10
denominator = 15
q(uit)
```

To exit the debugger we can use `q` or `quit`.

- `! statement`

To run Python code in debugger we can use `!` followed by the code we want to run. Without `!` the code can fail if it collides with any `pdb` command, hence it is recommended to always use `!` to run Python code.

```bash
$ python -m pdb script.py
> /pdb-mupy/script.py(1)<module>()
-> """I am the first script in this demo"""
(Pdb) !c = 2  # Define a variable named c
(Pdb) p c
2
```

Without `!` it fails because pdb thinks we are trying to run pdb's `c` command.
```python
(Pdb) c = 2
2
The program finished and will be restarted:
> /pdb-mupy/script.py(1)<module>()
-> """I am the first script in this demo"""
(Pdb)
```

- `run [args ...]`

`run` allows us to restart a program. This is helpful if we want to restart the programs with different argument without exiting the debugger.

```bash
$ python -m pdb script.py 10 5
> /pdb-mupy/script.py(1)<module>()
-> """I am the first script in this demo"""
(Pdb) !import sys
(Pdb) p sys.argv
['script.py', '10', '5']
Let's restart this program with different arguments:
(Pdb) run 30 40
Restarting script.py with arguments:
    30 40
> /pdb-mupy/script.py(1)<module>()
-> """I am the first script in this demo"""
(Pdb) !import sys
(Pdb) p sys.argv
['script.py', '30', '40']
```

- `l(ist) [first[, last]]`

`l` or `list` command can be used to list the source code.

Without any argument it lists the *11* lines around the current line. With one argument 11 lines around the specified line number. With two argument it lists the lines in that range, if second argument is less that first then it is taken as count.

```bash
$ python -m pdb script.py
> /pdb-mupy/script.py(1)<module>()
-> """I am the first script in this demo"""
List 11 lines around the current line:
(Pdb) list
  1  -> """I am the first script in this demo"""
  2
  3     import sys
  4
  5
  6     def divide(numerator, denominator):
  7         return numerator / denominator
  8
  9
 10     if __name__ == '__main__':
 11         numerator = int(sys.argv[1])
List lines 5 to 8:
(Pdb) list 5, 8
  5
  6     def divide(numerator, denominator):
  7         return numerator / denominator
  8
```

- `alias [name [command]]` or `unalias`

`alias` command can be used to set aliases for commands in debugger, similarly `unalias` can be used to unset an already existing alias.

Let's say we want to create an alias that returns a list of squares.

```python
(Pdb) alias squares [i**2 for i in xrange(%1)]
(Pdb) squares 5
[0, 1, 4, 9, 16]
```

Here `%1` is the argument that our alias expects(5 in the above example), if it expects more then we can use `%2`, `%3` etc

We can also create aliases using existing aliases:

```python
(Pdb) alias squares_7 squares 7
```

Now `squares_7` is equivalent to running `squares 7`

```python
(Pdb) squares_7
[0, 1, 4, 9, 16, 25, 36]
```

To remove an alias use `unalias` command followed by the command name.


### Stepping through code

One of the strongest feature of pdb is that we can move through our code in various ways: 
- Line by line 
- Jumping inside a function 
- Skip a loop 
- Skip function

In this section we will learn about the commands that allow us to step through the code. The code that we will be use in this section is [`next_and_step_until.py`](https://github.com/ashwch/pdb-mupy/blob/master/next_and_step_until.py.). These are the commands that you will be using the most, hence it is important to have a clear understanding here.

- `n(ext)`

`n` or simply `next` command runs the code on current line at full-speed and takes us to the next line in the current function.

- `s(tep)`

`s` or `step` is similar to next but they vary when a callable(function etc) is involved. If a callable is there then it will step us inside that callable instead of taking us to next line in the current function. If no callable is involved then it is same as next.

- `unt(il)`

`until` command tells the debugger to continue executing until we have reached a line number greater than the current line number. This command is helpful in exiting a loop.

- `r(eturn)`

`r` or `return` takes us to the end of the current function. At global level it takes us to the last line in the module. This command is helpful you want to step through the whole function body at once.

- `c(ont(inue))`

`c` or `cont` or `continue` command lets us run the whole code at full-speed when we are done with our debugging. If there's another breakpoint in your program then it will stop at that next breakpoint.

Let's debug through our script [`next_and_step_until.py`](https://github.com/ashwch/pdb-mupy/blob/master/next_and_step_until.py) while making use of the above commands. We have set a breakpoint on line #19 in that script and debugger will stop on next valid line: #21.

```bash
$ python next_and_step_until.py
> /Users/ashwini/work/instamojo/pdb-mupy/next_and_step_until.py(21)<module>()
-> knights()  # Just want to run this function and move on to next line? Use n(ext).
(Pdb)
```

Now to run the `knights()` function at full-speed use `n(ext)`. As you can see it printed the statements we have inside the `knights()` function and stopped on the next line in the current function.

```python
(Pdb) n
We are the Knights who say ni!
Get us a shrubbery.
> /Users/ashwini/work/instamojo/pdb-mupy/next_and_step_until.py(22)<module>()
-> credits()  # Want to step inside this function? Use s(tep).
(Pdb)
```

Now let's say we want to debug something inside `credits()` call, for that we can use `s(tep)`.

```python
(Pdb) s
--Call--
> /pdb-mupy/next_and_step_until.py(11)credits()
-> def credits():
(Pdb) n
> /pdb-mupy/next_and_step_until.py(12)credits()
-> print "A Møøse once bit my sister... No realli!"
(Pdb) n
A Møøse once bit my sister... No realli!
> /pdb-mupy/next_and_step_until.py(13)credits()
-> print "We apologise for the fault in the print statements."
(Pdb)
```

Now that we are done with this function we can use `r(eturn)` to go to its end and then use `n` to exit:

```python
(Pdb) r
We apologise for the fault in the print statements.
Those responsible have been sacked.
--Return--
> /Users/ashwini/work/instamojo/pdb-mupy/next_and_step_until.py(15)credits()->'M\xc3\xb8\xc...pretti nasti.'
-> return "Møøse bites Kan be pretti nasti."
(Pdb) n
> /Users/ashwini/work/instamojo/pdb-mupy/next_and_step_until.py(24)<module>()
-> for i in range(1, 5):
```

Now we are in a loop and both `n(ext)` and `s(tep)` can't be used to complete it in a single step. To skip the loop we can go its last line and use `unt(il)`.

```python
-> for i in range(1, 5):
(Pdb) n
> /pdb-mupy/next_and_step_until.py(26)<module>()
-> print "Shrubbery #{}".format(i)
(Pdb) until
Shrubbery #1
Shrubbery #2
Shrubbery #3
Shrubbery #4
> /pdb-mupy/next_and_step_until.py(28)<module>()
-> print "We have found the Holy Grail."
(Pdb)
```

Now we can continue executing the program using `c(ont(inue))`.

```python
(Pdb) cont
We have found the Holy Grail.
```

### Jumping between stacks

So far we have only seen how to move forward in code by moving line by line and jumping inside a function call. But `pdb` also provides us functionality to jump up and down in the current stack.

Best way to demonstrate this is to use a recursive function as an example, its code can be found at [`recursive.py`](https://github.com/ashwch/pdb-mupy/blob/master/recursive.py).

The three commands we will be going through in this section are `u(p)`, `d(own)` and `w(here)`.

- `w(here)`

`w` or `where` prints the whole trace till the most recent frame and current frame is represented using an arrow.

Let's run our program and when it stops at the breakpoint we will use `w(here)` to view the whole stack trace

```bash
$ python recursive.py
> /pdb-mupy/recursive.py(10)func()
-> return 0
(Pdb) where
  /pdb-mupy/recursive.py(14)<module>()
-> print (func(4))
  /pdb-mupy/recursive.py(7)func()
-> return func(n - 1)
  /pdb-mupy/recursive.py(7)func()
-> return func(n - 1)
  /pdb-mupy/recursive.py(7)func()
-> return func(n - 1)
  /pdb-mupy/recursive.py(7)func()
-> return func(n - 1)
> /pdb-mupy/recursive.py(10)func()  # Current frame
-> return 0
(Pdb)
```

Here `>` represents the current frame.

Now we can go up and down in the stack using `u(p)` and `d(own)`. Let's move up twice and then check the argument value using `a(rgs)`. The breakpoint was set at `n = 0`, now when we moved up twice we have `n = 2`.

```python
(Pdb) u
> /pdb-mupy/recursive.py(7)func()
-> return func(n - 1)
(Pdb) u
> /pdb-mupy/recursive.py(7)func()
-> return func(n - 1)
(Pdb) args
n = 2
(Pdb)
```

Similarly we can go back down using `d(own)`:

```python
(Pdb) d
> /pdb-mupy/recursive.py(7)func()
-> return func(n - 1)
(Pdb) args
n = 1
```

`u(p)` is also useful when you stepped(`s(tep)`)inside a function accidentally and want to go back.

### Breakpoints

So far we have only seen how to set a break-point by updating the code and adding `pdb.set_trace()` wherever we want to stop our program. But, `pdb` also provides us a way to set dynamic conditional breakpoints without updating the source code. In this section we will be using code from [`breakpoints.py`](https://github.com/ashwch/pdb-mupy/blob/master/breakpoints.py) file.

- `b(reak) [[filename:]lineno | function[, condition]]`:

We can set a breakpoint in the current file by specifying the line number or function name in the current file. Or we can also set breakpoint in some other file(this file should be present in module search path) by specifying the file name followed by a line number.
Each number is assigned a number and this number can be used later with other commands to access the breakpoint.

`condition` is a Python statement that should be True to stop at the breakpoint. This condition is executed in the scope at which we have set the breakpoint.

Few examples of setting breakpoints.

- `break 13` # Set breakpoint on line number 13
- `break divide` # Set breakpoint on `divide` function
- `break divide, denominator == 0` # Set breakpoint in divide function only if `denominator` is 0

```bash
$ python -m pdb breakpoints.py 10 0
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
(Pdb) break divide, denominator == 0
Breakpoint 1 at /pdb-mupy/breakpoints.py:5
```

Get list of breakpoints using `b(break)`. Here `Num = 1` is the number assigned to the breakpoint. `Disp == keep` means it is a permanent breakpoint and `End = yes` means this breakpoint is right now enabled.

```python
(Pdb) break
    Num Type         Disp Enb   Where
    1   breakpoint   keep yes   at /pdb-mupy/breakpoints.py:5
        stop only if denominator == 0
    (Pdb) c
```

As denominator is program our program stopped under debugger control:

```python
> /pdb-mupy/breakpoints.py(8)divide()
    -> print "Calculating {}/{}".format(numerator, denominator)
    (Pdb) args
    numerator = 10.0
    denominator = 0.0
```

Let's restart the program using different arguments:

```python
(Pdb) run 10 5
Restarting breakpoints.py with arguments:
    10 5
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
(Pdb) c
Calculating 10.0/5.0
2.0
The program finished and will be restarted
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
```

As the denominator wasn't zero this time the program didn't stop at the breakpoint.

```python
(Pdb) break
Num Type         Disp Enb   Where
1   breakpoint   keep yes   at /pdb-mupy/breakpoints.py:5
    stop only if denominator == 0
    breakpoint already hit 2 times
```

**Note**: Breakpoints persist even after the auto restart or forced restart(using `run`) in `-m pdb` mode.


- `tbreak [[filename:]lineno | function[, condition]]`:

`tbreak` allows us to set a temporary breakpoint. This breakpoint goes away as soon as it is hit once. Can be pretty useful if you want to set a breakpoint only once, say inside a loop or for the first time a function is invoked.

```bash
$ python -m pdb breakpoints.py 10 5
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
(Pdb) tbreak divide, denominator == 0
Breakpoint 1 at/pdb-mupy/breakpoints.py:5
(Pdb) break
Num Type         Disp Enb   Where
1   breakpoint   del  yes   at /pdb-mupy/breakpoints.py:5
    stop only if denominator == 0
```

Notice the value of `Disp` this time. It is `del` instead of `keep`, means it is a temporary breakpoint.

```python
(Pdb) c
Calculating 10.0/5.0
2.0
The program finished and will be restarted
> /Users/ashwini/work/instamojo/pdb-mupy/breakpoints.py(2)<module>()
-> import sys
```

Programs simply restarted because the breakpoint condition wasn't true, now let's make it true by restarting it with different arguments.

```python
(Pdb) run 10 0
Restarting breakpoints.py with arguments:
    10 0
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
(Pdb) c
Deleted breakpoint 1
> /Users/ashwini/work/instamojo/pdb-mupy/breakpoints.py(8)divide()
-> print "Calculating {}/{}".format(numerator, denominator)
(Pdb) break
(Pdb)
```

This time it did hit the breakpoint and was deleted as well.

- `cl(ear) [filename:lineno | bpnumber [bpnumber ...]]`:

We can permanently remove breakpoints using `cl(ear)` command.


- `disable [bpnumber [bpnumber ...]]` or `enable [bpnumber [bpnumber ...]]`:

To temporary disable a breakpoint use `disable` and to re-enable a breakpoint use `enable`. Unlike `clear` breakpoints are not removed permanently in this case.

- `ignore bpnumber [count]`:

We can also ignore a breakpoint count number of times using `ignore` command. Breakpoint is re-activated when the count becomes 0.


- `condition bpnumber [condition]`:

To update or add condition to a breakpoint we can use the condition command.

**Note**: If the condition is an invalid Python code then it will be evaluated as True but in case the breakpoint was a temporary one then it won't be deleted and if the breakpoint had an ignore count then it won't be decremented. This is done to notify the user that something's wrong.

- `commands [bpnumber]`:

`commands` is a pretty useful command related to breakpoints. If used in a certain way then it can be equivalent to adding print statements in our code.

This command allows us to run multiple commands when a breakpoint is hit.

Let's add a breakpoint on `divide` function and now we will print some stuff as well using `commands`.

```bash
$ python -m pdb breakpoints.py 10 5
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
(Pdb) break divide
Breakpoint 1 at /Users/ashwini/work/instamojo/pdb-mupy/breakpoints.py:5
```

In commands mode the prompt is (com). To end the commands use end.

```python
(Pdb) commands 1
(com) args
(com) p "Inside divide()"
(com) end
(Pdb) c
numerator = 10.0
denominator = 5.0
'Inside divide()'
> /pdb-mupy/breakpoints.py(8)divide()
-> print "Calculating {}/{}".format(numerator, denominator)
```

Now as you can see our program printed few things on hitting the breakpoint.

We can also use commands like `cont`, `next` etc. But these commands will also act as `end` because these commands can lead us to next breakpoint which may have its own set of commands and then debugger will be confused about whose commands to run next.

Another commands is silent, when this command is part of commands list then you won't see the message we get at a breakpoint.

```bash
$ python -m pdb breakpoints.py 10 5
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
(Pdb) break divide
Breakpoint 1 at /pdb-mupy/breakpoints.py:5
(Pdb) commands 1
(com) args
(com) p "Inside divide()"
(com) silent
(com) cont
(Pdb) c
numerator = 10.0
denominator = 5.0
'Inside divide()'
Calculating 10.0/5.0
2.0
The program finished and will be restarted
> /pdb-mupy/breakpoints.py(2)<module>()
-> import sys
(Pdb)
```

As you can see above the program didn't stop at the breakpoint this time due to `cont` command and we didn't see the lines(shown below) related to breakpoint either due to `silent` command:

```python
> /pdb-mupy/breakpoints.py(8)divide()
-> print "Calculating {}/{}".format(numerator, denominator)
```

### Tips and tricks
- `.pdbrc` file: If present the commands present in this file are ran at the start of debugger session. This file can be added to your home directory and/or current directory.

- Plain enter repeats the last command(list command is an exception).

- To enter multiple commands on a single line use `;;` as separator.

### What's new in Python 3

#### Python 3.3+

- Tab-completion via the `readline` module is available for commands and command arguments.

#### Python 3.2+

- `pdb.py` now accepts a `-c` option that executes commands as if given in a ``.pdbrc file`

- A new command `ll` can be used to see the source related to the current function or frame.

- A new command `source` can be used to see the source code of an expression: `source expression`.

- A new command `interact` can be used to start interactive shell in debugger using the `globals()` and `locals()` in the current frame. This can be done in Python 2 using `!import code; code.interact(local=vars())`.
