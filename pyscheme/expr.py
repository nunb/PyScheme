# PyScheme lambda language written in Python
#
# Expressions (created by the parser) for evaluation
#
# Copyright (C) 2018  Bill Hails
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pyscheme.op as op
from pyscheme import environment
from typing import Callable
from pyscheme.exceptions import NonBooleanExpressionError
from pyscheme.singleton import Singleton, FlyWeight
from pyscheme.types import Promise, Continuation, Amb


class Expr:
    def eval(self, env: 'environment.Environment', ret: Continuation, amb: Amb) -> Promise:
        pass

    def is_true(self) -> bool:
        raise NonBooleanExpressionError()

    def is_false(self) -> bool:
        raise NonBooleanExpressionError()

    def is_unknown(self) -> bool:
        raise NonBooleanExpressionError()

    def __eq__(self, other: 'Expr') -> bool:
        return id(self) == id(other)

    def eq(self, other: 'Expr') -> 'Bool':
        if self == other:
            return T()
        else:
            return F()

    def gt(self, other: 'Expr') -> 'Bool':
        if self > other:
            return T()
        else:
            return F()

    def lt(self, other: 'Expr') -> 'Bool':
        if self < other:
            return T()
        else:
            return F()

    def ge(self, other: 'Expr') -> 'Bool':
        if self >= other:
            return T()
        else:
            return F()

    def le(self, other: 'Expr') -> 'Bool':
        if self <= other:
            return T()
        else:
            return F()

    def ne(self, other: 'Expr') -> 'Bool':
        if self != other:
            return T()
        else:
            return F()

    def is_null(self) -> bool:
        return False


class List(Expr):
    pass


class Constant(Expr):
    def __init__(self, value):
        self._value = value

    def eval(self, env: 'environment.Environment', ret: Continuation, amb: Amb) -> Promise:
        return lambda: ret(self, amb)

    def value(self):
        return self._value

    def __eq__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value == other.value()
        else:
            return False

    def __gt__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value > other.value()
        else:
            return False

    def __lt__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value < other.value()
        else:
            return False

    def __ge__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value >= other.value()
        else:
            return False

    def __le__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value <= other.value()
        else:
            return False

    def __ne__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value != other.value()
        else:
            return False

    def __add__(self, other: Expr):
        return Constant(self._value + other._value)

    def __sub__(self, other: Expr):
        return Constant(self._value - other._value)

    def __mul__(self, other: Expr):
        return Constant(self._value * other._value)

    def __floordiv__(self, other: Expr):
        return Constant(self._value // other._value)

    def __mod__(self, other: Expr):
        return Constant(self._value % other._value)

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


class Boolean(Constant):
    def __init__(self):
        pass

    def __and__(self, other: 'Boolean') -> 'Boolean':
        pass

    def __or__(self, other: 'Boolean') -> 'Boolean':
        pass

    def __invert__(self) -> 'Boolean':
        pass

    def __xor__(self, other: 'Boolean') -> 'Boolean':
        return (self & ~other) | (other & ~self)

    def __eq__(self, other: 'Boolean') -> 'Boolean':
        return id(self) == id(other)

    def is_true(self) -> bool:
        return False

    def is_false(self) -> bool:
        return False

    def is_unknown(self) -> bool:
        return False


class T(Boolean, metaclass=Singleton):
    def __and__(self, other: Boolean) -> Boolean:
        return other

    def __or__(self, other: Boolean) -> Boolean:
        return self

    def __invert__(self) -> Boolean:
        return F()

    def __str__(self) -> str:
        return "true"

    def eq(self, other: Boolean) -> Boolean:
        if self == other:
            return self
        else:
            return other

    def is_true(self) -> bool:
        return True

    __repr__ = __str__


class F(Boolean, metaclass=Singleton):
    def __and__(self, other: Boolean) -> Boolean:
        return self

    def __or__(self, other: Boolean) -> Boolean:
        return other

    def __invert__(self) -> Boolean:
        return T()

    def __str__(self) -> str:
        return "false"

    def eq(self, other) -> Boolean:
        if self == other:
            return T()
        elif other == U():
            return other
        else:
            return self

    def is_false(self) -> bool:
        return True

    __repr__ = __str__


class U(Boolean, metaclass=Singleton):
    def __and__(self, other: Boolean) -> Boolean:
        if other == F():
            return other
        else:
            return self

    def __or__(self, other: Boolean) -> Boolean:
        if other == T():
            return other
        else:
            return self

    def __invert__(self) -> Boolean:
        return self

    def eq(self, other: Boolean) -> Boolean:
        return self

    def __str__(self) -> str:
        return "unknown"

    def is_unknown(self) -> bool:
        return True

    __repr__ = __str__


class Symbol(Expr, metaclass=FlyWeight):
    def __init__(self, name):
        self._name = name

    def eval(self, env: 'environment.Environment', ret: Continuation, amb: Amb) -> Promise:
        return lambda: env.lookup(self, ret, amb)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def __str__(self):
        return str(self._name)

    __repr__ = __str__


class List(Expr):
    @classmethod
    def list(cls, args, index=0):
        if index == len(args):
            return Null()
        else:
            return Pair(args[index], cls.list(args, index=index + 1))

    def is_null(self):
        return False

    def car(self):
        pass

    def cdr(self):
        pass

    def __len__(self):
        pass

    def __str__(self):
        return self.qualified_str('[', ', ', ']')

    __repr__ = __str__

    def __getitem__(self, item):
        pass

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        pass

    def trailing_str(self, sep: str, end: str) -> str:
        pass

    def append(self, other) -> List:
        pass

    def last(self):
        pass

    def __iter__(self):
        return ListIterator(self)


class Pair(List):
    def __init__(self, car, cdr: List):
        self._car = car
        self._cdr = cdr
        self._len = 1 + len(cdr)

    def car(self):
        return self._car

    def cdr(self):
        return self._cdr

    def eval(self, env: 'environment.Environment', ret: Callable, amb: Callable):
        def car_continuation(evaluated_car, amb: Callable):
            def cdr_continuation(evaluated_cdr, amb: Callable):
                return lambda: ret(Pair(evaluated_car, evaluated_cdr), amb)
            return lambda: self._cdr.eval(env, cdr_continuation, amb)
        return self._car.eval(env, car_continuation, amb)

    def last(self):
        if self._len == 1:
            return self._car
        else:
            return self._cdr.last()

    def __len__(self):
        return self._len

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        return start + str(self._car) + self._cdr.trailing_str(sep, end)

    def trailing_str(self, sep: str, end: str) -> str:
        return sep + str(self._car) + self._cdr.trailing_str(sep, end)

    def append(self, other: List):
        return Pair(self._car, self._cdr.append(other))

    def __eq__(self, other: List):
        if other.__class__ == Pair:
            return self._car == other.car() and self._cdr == other.cdr()
        else:
            return False

    def __getitem__(self, item):
        if type(item) is not int:
            raise TypeError
        if item < 0:
            raise KeyError
        val = self
        while item > 0:
            val = val.cdr()
            item -= 1
        if val.is_null():
            raise KeyError
        return val.car()


class Null(List, metaclass=Singleton):
    def is_null(self):
        return True

    def car(self):
        return self

    def cdr(self):
        return self

    def eval(self, env: 'environment.Environment', ret: Callable, amb: Callable):
        return ret(self, amb)

    def last(self):
        return self

    def __len__(self):
        return 0

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        return start + end

    def trailing_str(self, sep: str, end: str) -> str:
        return end

    def append(self, other):
        return other

    def __eq__(self, other: Expr):
        return other.is_null()

    def __getitem__(self, item):
        if type(item) is not int:
            raise TypeError
        raise KeyError


class ListIterator:
    def __init__(self, lst: List):
        self._lst = lst

    def __next__(self):
        if self._lst.is_null():
            raise StopIteration
        else:
            val = self._lst.car()
            self._lst = self._lst.cdr()
            return val


class Char(Expr, metaclass=FlyWeight):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "'" + str(self._value) + "'"


class Conditional(Expr):
    def __init__(self, test: Expr, consequent: Expr, alternative: Expr):
        self._test = test
        self._consequent = consequent
        self._alternative = alternative

    def eval(self, env: 'environment.Environment', ret: Callable, amb: Callable):
        def deferred(result: Expr, amb: Callable):
            if result.is_true():
                return lambda: self._consequent.eval(env, ret, amb)
            else:
                return lambda: self._alternative.eval(env, ret, amb)
        return lambda: self._test.eval(env, deferred, amb)

    def __str__(self):
        return "if (" + str(self._test) + \
               ") {" + str(self._consequent) + \
               "} else {" + str(self._alternative) + "}"

    __repr__ = __str__


class Lambda(Expr):
    def __init__(self, args: List, body: Expr):
        self._args = args
        self._body = body

    def eval(self, env: 'environment.Environment', ret: Callable, amb: Callable):
        return lambda: ret(op.Closure(self._args, self._body, env), amb)

    def __str__(self):
        return "Lambda " + str(self._args) + ": { " + str(self._body) + " }"

    __repr__ = __str__


class Application(Expr):
    def __init__(self, operation: Expr, operands: List):
        self._operation = operation
        self._operands = operands

    def eval(self, env: 'environment.Environment', ret: Callable, amb: Callable):
        def deferred_op(evaluated_op, amb: Callable):
            return lambda: evaluated_op.apply(self._operands, env, ret, amb)
        return self._operation.eval(env, deferred_op, amb)

    def __str__(self):
        return str(self._operation) + str(self._operands)


class Sequence(Expr):
    def __init__(self, exprs: List):
        self._exprs = exprs

    def eval(self, env: 'environment.Environment', ret: Callable, amb: Callable):
        def take_last(expr: List, amb: Callable):
            return lambda: ret(expr.last(), amb)
        return lambda: self._exprs.eval(env, take_last, amb)

    def __str__(self):
        return self._exprs.qualified_str('', ' ; ', '')


