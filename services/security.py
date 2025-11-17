# services/security.py
import ast
from services.logger import get_logger

logger = get_logger(__name__)

class SecurityViolation(Exception):
    pass

class AstValidator(ast.NodeVisitor):
    """
    Walks the Abstract Syntax Tree of the generated code to ensure it is safe.
    """
    def __init__(self, allowed_names):
        self.allowed_names = set(allowed_names)
        self.allowed_attributes = {
            'filter', 'project', 'join', 'groupby', 'aggregate',
            'get_header', 'columns', 'items',
            'max_by', 'min_by', 'top_k_by'
        }

        self.allowed_functions = {
            'len', 'int', 'float', 'str', 'build_chart_url'
        }

    def visit_Call(self, node):
        """Checks function calls."""
        # Check strict function calls like len(), int()
        if isinstance(node.func, ast.Name):
            if node.func.id not in self.allowed_functions:
                raise SecurityViolation(f"Unauthorized function call: {node.func.id}")

        # Check method calls like .filter(), .join()
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr not in self.allowed_attributes:
                raise SecurityViolation(f"Unauthorized method call: .{node.func.attr}()")

        # Allow lambdas to be called (used inside filter)
        elif isinstance(node.func, ast.Lambda):
            pass

        else:
            raise SecurityViolation("Unauthorized complex call type")

        self.generic_visit(node)

    def visit_Name(self, node):
        """Checks variable access."""
        if isinstance(node.ctx, ast.Load):
            if node.id.startswith("__"):
                raise SecurityViolation(f"Access to private attribute denied: {node.id}")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Checks property access (like .columns or .timestamp)."""
        if node.attr.startswith("__"):
            raise SecurityViolation(f"Access to private attribute denied: {node.attr}")
        self.generic_visit(node)

    def visit_Import(self, node):
        raise SecurityViolation("Imports are strictly forbidden.")

    def visit_ImportFrom(self, node):
        raise SecurityViolation("Imports are strictly forbidden.")


# Toggle to turn security on or off.
# You said you want security disabled, so keep this False in development.
ENABLE_SECURITY = False


def secure_eval(code_string, context):
    """
    Evaluates the generated code string in a restricted environment.

    If ENABLE_SECURITY is True:
        - Parses the AST
        - Runs AstValidator on it
    If ENABLE_SECURITY is False:
        - Skips AST validation and just evals with SAFE_BUILTINS.
    """
    SAFE_BUILTINS = {
        "len": len,
        "int": int,
        "float": float,
        "str": str,
        "max": max,
        "min": min,
        "sum": sum,
        "abs": abs,
    }

    try:
        if ENABLE_SECURITY:
            tree = ast.parse(code_string, mode='eval')
            allowed_names = list(context.keys())
            validator = AstValidator(allowed_names)
            validator.visit(tree)

        logger.info(f"Executing code: {code_string}")
        return eval(code_string, {"__builtins__": SAFE_BUILTINS}, context)

    except SecurityViolation as e:
        logger.error(f"Security blocked: {str(e)}")
        raise e
    except SyntaxError as e:
        logger.error(f"Syntax error: {code_string}")
        raise e
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise e
