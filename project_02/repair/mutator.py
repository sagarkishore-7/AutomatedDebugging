import ast
import copy
from typing import Iterable, List


class Marker(ast.NodeTransformer):
    """Mark the target statement."""

    def __init__(self, line_no: int) -> None:
        super().__init__()
        self.line_no = line_no
        self.found = False  # target found?
        self.loop_level = 0  # depth of loop (0 indicates outside loop body)
        self.is_first_stmt = False  # is the first stmt in block?

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(node, ast.stmt) and node.lineno == self.line_no:
            node.__target__ = (self.loop_level > 0, self.is_first_stmt)
            self.found = True
            return node

        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        self.loop_level += self._check_loop_enter(value)
                        self.is_first_stmt = self._check_first_stmt(value, old_value)
                        value = self.visit(value)
                        self.loop_level -= self._check_loop_exit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                self.loop_level += self._check_loop_enter(old_value)
                new_node = self.visit(old_value)
                self.loop_level -= self._check_loop_exit(new_node)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)

        return node

    def _check_loop_enter(self, node: ast.AST) -> int:
        """Checks if the given node is a loop node and returns 1 if it is, 0 otherwise."""
        if isinstance(node, (ast.While, ast.For)):
            return 1
        return 0

    def _check_loop_exit(self, node: ast.AST) -> int:
        """Checks if the given node is a loop node and returns 1 if it is, 0 otherwise."""
        if isinstance(node, (ast.While, ast.For)):
            return 1
        return 0

    def _check_first_stmt(self, value, old_values: list) -> bool:
        """Checks if the given value is the first statement in the given list."""
        return value == old_values[0]


def mk_abstract() -> ast.expr:
    """Create an AST for the abstract condition."""
    return ast.Name('__abstract__')


class MutationOperator(ast.NodeTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.mutated = False

class Tighten(MutationOperator):
    """If the target statement is an if-statement, transform its condition by
    conjoining an abstract condition: if c => if c and not __abstract__."""

    def __init__(self) -> None:
        super().__init__()

    def visit_If(self, node):
        if hasattr(node, '__target__'):
            new_condition = ast.BoolOp(
                op=ast.And(),
                values=[node.test,
                        ast.UnaryOp(
                            op=ast.Not(),
                            operand=ast.Name(id='__abstract__', ctx=ast.Load())
                        )]
            )
            node.test = new_condition
            self.mutated = True
        self.generic_visit(node)
        return node



class Loosen(MutationOperator):
    """If the target statement is an if-statement, transform its condition by
    disjoining an abstract condition: if c => if c or __abstract__."""

    def __init__(self) -> None:
        super().__init__()

    def visit_If(self, node):
        if hasattr(node, '__target__'):
            new_condition = ast.BoolOp(
                op=ast.Or(),
                values=[node.test,
                        ast.Name(id='__abstract__', ctx=ast.Load())
                        ]
            )
            node.test = new_condition
            self.mutated = True
        self.generic_visit(node)
        return node


class Guard(MutationOperator):
    """Transform the target statement so that it executes only if an abstract condition is false:
    s => if not __abstract__: s."""

    def __init__(self):
        super().__init__()
        self.abstract_condition = '__abstract__'

    def visit(self, node):
        if hasattr(node, '__target__'):
            new_node = ast.If(
                test=ast.UnaryOp(
                    op=ast.Not(),
                    operand=ast.Name(
                        id=self.abstract_condition,
                        ctx=ast.Load()
                    )
                ),
                body=[node],
                orelse=[]
            )
            self.mutated = True
            node = new_node
        else:
            self.generic_visit(node)
        return node


class Break(MutationOperator):
    """If the target statement is in loop body, right before it insert a `break` statement that
    executes only if an abstract condition is true, i.e., if __abstract__: break."""
    def __init__(self, required_position: bool) -> None:
        """If `required_position` is `True`, this operation is performed only when the
        target is the first statement.
        If `required_position` is `False`, this operation is performed only when the
        target is not the first statement.
        """
        super().__init__()
        self.required_position = required_position
        self.abstract_condition = '__abstract__'

    def visit_loop(self, node):
        index = self.get_target_index(node)
        if node is not None and index is not None and hasattr(node.body[index], '__target__'):
            target = node.body[index].__target__
            if isinstance(target, tuple) and len(target) == 2 and target[0] and (
                    (self.required_position and target[1]) or (not self.required_position and not target[1])):
                new_node = ast.copy_location(node, node)
                new_node.body.insert(index, ast.If(
                    test=ast.Name(self.abstract_condition, ast.Load()),
                    body=[ast.Break()], orelse=[]))
                self.mutated = True
                return new_node
        self.generic_visit(node)
        return node

    def visit_While(self, node):
        return self.visit_loop(node)

    def visit_For(self, node):
        return self.visit_loop(node)

    def get_target_index(self, node) -> int | None:
        for index, stmt in enumerate(node.body):
            if hasattr(stmt, '__target__'):
                return index
        return None


class Mutator:
    """Perform program mutation."""
    def __init__(self, tree: ast.Module, line_no: int, log: bool = False) -> None:
        assert isinstance(tree, ast.Module)
        self.old_tree = tree
        self.log = log
        
        marker = Marker(line_no)
        self.marked_tree = marker.visit(copy.deepcopy(tree))
        assert marker.found

    def apply(self, ops: List[MutationOperator] = None) -> Iterable[ast.Module]:
        if ops is None:
            # in default priority order
            ops = [Tighten(), Loosen(), Break(True), Guard(), Break(False)] 

        for visitor in ops:
            new_tree = visitor.visit(copy.deepcopy(self.marked_tree))
            if self.log:
                print(f'-> {visitor.__class__.__name__}', '✓' if visitor.mutated else '✗')

            if visitor.mutated:
                if self.log:
                    print(ast.unparse(new_tree))

                yield new_tree
