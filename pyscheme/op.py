from functools import reduce
from typing import Callable

"""
We need to distinguish between
1. primitives that have their arguments evaluated for them
   do not take a continuation
2. primitives that are lazy (special forms)
   take a continuation
3. closures that have their arguments evaluated for them
   still need a continuation to evaluate the body
4. macros
   evaluate body with unevaluated args, then re-evaluate result
"""

class Op:
    def apply(self, args, env, ret: Callable, amb: Callable):
        pass


class Primitive(Op):
    def apply(self, args, env, ret: Callable, amb: Callable):
        def deferred_apply(evaluated_args, amb: Callable):
            return lambda: self.apply_evaluated(evaluated_args, ret, amb)
        return args.eval(env, deferred_apply, amb)

    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        pass


class SpecialForm(Op):
    pass


class Closure(Primitive):
    def __init__(self, args, body, env):
        self._args = args
        self._body = body
        self._env = env

    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: self._body.eval(self._env.extend(dict(zip(self._args, args))), ret, amb)

    def __str__(self):
        return "Closure(" + str(self._args) + ": " + str(self._body) + ")"


class Addition(Primitive):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        import pyscheme.expr as expr
        return lambda: ret(expr.Constant(reduce(lambda x, y: x.value() + y.value(), args)), amb)


class Equality(Primitive):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args.car().eq(args.cdr().car()), amb)


class And(SpecialForm):
    def apply(self, args, env, ret: Callable, amb: Callable):
        def cont(lhs, amb: Callable):
            if lhs.is_true():
                return lambda: args.cdr().car().eval(env, ret, amb)
            elif lhs.is_false():
                return lambda: ret(lhs, amb)
            else:
                def cont2(rhs, amb: Callable):
                    if rhs.is_false():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)
                return lambda: args.cdr().car().eval(env, cont2, amb)

        return lambda: args.car().eval(env, cont, amb)


class Or(SpecialForm):
    def apply(self, args, env, ret: Callable, amb: Callable):
        def cont(lhs, amb: Callable):
            if lhs.is_true():
                return lambda: ret(lhs, amb)
            elif lhs.is_false():
                return lambda: args.cdr().car().eval(env, ret, amb)
            else:
                def cont2(rhs, amb: Callable):
                    if rhs.is_true():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)
                return lambda: args.cdr().car().eval(env, cont2, amb)

        return lambda: args.car().eval(env, cont, amb)


class Then(SpecialForm):
    def apply(self, args, env, ret: Callable, amb: Callable):
        def amb2():
            return lambda: args.cdr().car().eval(env, ret, amb)
        return lambda: args.car().eval(env, ret, amb2)


class Fail(SpecialForm):
    def apply(self, args, env, ret: Callable, amb: Callable):
        return lambda: amb()


class Not(Primitive):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(~(args.car()), amb)


class Xor(Primitive):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args.car() ^ args.cdr().car(), amb)


class Cons(Primitive):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        from pyscheme.expr import Pair
        return lambda: ret(Pair(args.car(), args.cdr().car()), amb)


class Append(Primitive):
    def apply_evaluated(self, args, ret:Callable, amb: Callable):
        return lambda: ret(args.car().append(args.cdr().car()), amb)
