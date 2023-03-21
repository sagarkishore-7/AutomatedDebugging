import ast
import copy
import itertools
from types import CodeType
from typing import Any, Dict, List, Tuple
from project_02.repair.tester import *

class Template:
    """Condition template."""
    def __init__(self, meta_vars: List[Tuple[str, str]], body: ast.expr) -> None:
        self.args: List[str] = [s for s, _ in meta_vars]
        self.types: List[str] = [t for _, t in meta_vars]
        self.body = body

    @classmethod
    def from_lambda(cls, expr: str):
        """Parse a template from a string, basic syntax:
        (<var> : <type>, <var> : <type>, ...) => <condition>
        The lhs parenthesis is optional."""
        lhs, body = expr.split('=>')
        lhs = lhs.strip()
        if lhs.startswith('(') and lhs.endswith(')'):
            lhs = lhs[1:-1]
        lhs = lhs.split(',') if ',' in lhs else [lhs]

        meta_vars = []
        for x in lhs:
            arg, typ = x.split(':')
            meta_vars.append( (arg.strip(), typ.strip()) )
        
        body = ast.parse(body.strip()).body[0].value
        assert isinstance(body, ast.expr)
        return cls(meta_vars, body)

    def instantiate(self, vars: List[str]) -> ast.expr:
        """Instantiate a template with `vars`. Just like applying values to lambda expressions."""
        assert len(vars) == len(self.args)
        return self.NameTransformer(dict(zip(self.args, vars))).visit(copy.deepcopy(self.body))

    class NameTransformer(ast.NodeTransformer):
        def __init__(self, mapping: Dict[str, str]) -> None:
            super().__init__()
            self.mapping = mapping

        def visit_Name(self, node: ast.Name) -> ast.Name:
            if node.id in self.mapping:
                node.id = self.mapping[node.id]
                return node

            return node

class Synthesizer:
    """Condition synthesis."""

    def __init__(self, tree: ast.Module, pos_tests: List[CodeType], neg_tests: List[CodeType],
                 k: int = 10, extra_templates: List[Template] = None, log: bool = False) -> None:
        self.abstract_tree = tree
        self.pos_tests = pos_tests
        self.neg_tests = neg_tests
        self.k = k
        self.extra_templates = extra_templates
        self.log = print if log else no_log

        self.condition: ast.expr            # synthesized condition
        self.concrete_tree: ast.Module      # instantiated tree
    
    def apply(self) -> bool:
        """Entry point."""
        overall_record = Record([], [])

        for test_code in self.neg_tests:
            self.log(f'--> Execute {test_code.co_name}')

            success, record = exec_abstract(self.abstract_tree, test_code, iter([]))
            self.log(f'--(0/{self.k})->', '✓' if success else '✗', record.values)

            i = 1
            while not success and i <= self.k:
                if i == self.k: # the last attempt
                    future_values = all_true()
                else:
                    future_values = iter(self.flip(record.values))

                success, record = exec_abstract(self.abstract_tree, test_code, future_values)
                self.log(f'--({i}/{self.k})->', '✓' if success else '✗', record.values)
                i += 1

            if success:
                overall_record += record
            else:
                return False # synthesis failed

        for test_code in self.pos_tests:
            self.log(f'--> Execute {test_code.co_name} (+)')

            success, record = exec_abstract(self.abstract_tree, test_code, iter([]))
            self.log('   ', '✓' if success else '✗', record.values)
            
            assert success
            overall_record += record
        
        if self.solve(overall_record):
            self.concrete_tree = Instantiate(self.condition).visit(
                copy.deepcopy(self.abstract_tree))
            return True
        else:
            return False

    def flip(self, values: List[bool]) -> List[bool]:
        """Flip the last `False` to `True`, and drop all the `True`s after the last `False`."""
        if not values:
            return []

        for i in range(len(values) - 1, -1, -1):
            if not values[i]:
                return values[:i] + [True]

        return []

    def solve(self, constraints: Record) -> bool:
        """Solve constraints. Returns if a solution is found. Set `self.condition` when found."""
        # Enumerate candidate conditions of form x == v and x != v for all items x: v seen in the environments of constraints.
        candidates = set()
        for env in constraints.envs:
            for var, value in env.items():
                if isinstance(value, str):
                    value = f"'{value}'"
                candidates.add(ast.parse(f"{var} == {value}").body[0].value)
                candidates.add(ast.parse(f"{var} != {value}").body[0].value)

        # Check if each candidate condition is satisfiable.
        for cond in candidates:
            if self.sat(cond, constraints):
                self.condition = cond
                return True

        # candidate enumeration phase 2
        if self.extra_templates is not None:
            env_types = {x: type(v) for env in constraints.envs for x, v in env.items()}
            for tpl in self.extra_templates:
                template_vars = [[x for x, t in env_types.items() if t.__name__ == temp] for temp in tpl.types]
                for t in itertools.product(*template_vars):
                    inst = tpl.instantiate(t)
                    if self.sat(inst, constraints):
                        self.condition = inst
                        return True
        return False

    def sat(self, cond: ast.expr, constraints: Record) -> bool:
        """Check if `cond` satisfies the `constraints`."""
        for env, value in zip(constraints.envs, constraints.values):
            try:
                actual = eval(ast.unparse(cond), {}, env)
            except Exception:
                return False

            if actual != value:
                return False

        return True
    
    def validate(self) -> bool:
        """Check correctness of the repaired program `self.concrete_tree`."""
        return run_tests(self.concrete_tree, self.neg_tests + self.pos_tests)

def no_log(self, *values: object) -> None:
    pass

