"""
source_preprocessor.py

Purpose:
    Preprocesses source code before it is submitted to an AI model.

Responsibilities:
    - Remove module, class, and function docstrings.
    - Remove comment lines.
    - Preserve executable source code.
    - Reduce prompt size and improve AI review quality.

Author:
    Ron Gonzalez

Created:
    June 2026
"""

import ast
import io
import logging
import tokenize

logger = logging.getLogger(__name__)


class SourceCodePreprocessingService:
    """
    Utility class for preparing source code for AI analysis.
    """

    @staticmethod
    def remove_comments(source_code: str) -> str:
        """
        Remove Python comments while preserving executable code.
        """
        logger.debug("Starting comment removal.")

        try:
            output = []

            tokens = tokenize.generate_tokens(io.StringIO(source_code).readline)

            for token in tokens:
                if token.type != tokenize.COMMENT:
                    output.append(token)

            cleaned = tokenize.untokenize(output)

            logger.debug("Comment removal completed successfully.")

            return cleaned

        except Exception:
            logger.exception("Comment removal failed.")
            raise

    @staticmethod
    def remove_docstrings(source_code: str) -> str:
        """
        Remove module, class, and function docstrings.
        """
        logger.debug("Starting docstring removal.")

        class DocstringRemover(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                self.generic_visit(node)

                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    node.body.pop(0)

                return node

            def visit_AsyncFunctionDef(self, node):
                self.generic_visit(node)

                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    node.body.pop(0)

                return node

            def visit_ClassDef(self, node):
                self.generic_visit(node)

                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    node.body.pop(0)

                return node

            def visit_Module(self, node):
                self.generic_visit(node)

                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    node.body.pop(0)

                return node

        try:
            tree = ast.parse(source_code)
            tree = DocstringRemover().visit(tree)
            ast.fix_missing_locations(tree)

            cleaned = ast.unparse(tree)

            logger.debug("Docstring removal completed successfully.")

            return cleaned

        except Exception:
            logger.exception("Docstring removal failed.")
            raise

    @classmethod
    def preprocess(
        cls,
        source_code: str,
        *,
        remove_comments: bool = True,
        remove_docstrings: bool = True,
    ) -> str:
        """
        Preprocess source code prior to AI analysis.

        Args:
            source_code:
                Python source code to preprocess.

            remove_comments:
                Remove Python comments.

            remove_docstrings:
                Remove module, class, and function docstrings.

        Returns:
            Preprocessed source code.
        """
        logger.info("Starting source preprocessing.")

        try:
            if remove_comments:
                source_code = cls.remove_comments(source_code)

            if remove_docstrings:
                source_code = cls.remove_docstrings(source_code)

            logger.info("Source preprocessing completed successfully.")

            return source_code

        except Exception:
            logger.exception("Source preprocessing failed.")
            raise
