"""
Visitor para traducir SQL a Cypher.

Recorre el AST generado por ANTLR4 y construye la consulta Cypher equivalente.

Mapeo básico según CORE-03:
- SELECT col FROM table -> MATCH (n:Table) RETURN n.col
- WHERE con operadores =, >, <, <=, >=, !=
- Soporte para AND, OR
"""

from app.core.parser.generated.SQLSimpleVisitor import SQLSimpleVisitor


class SQLToCypherVisitor(SQLSimpleVisitor):
    """
    Visitor que traduce SQL a Cypher Neo4j.

    Implementa el mapeo definido en el documento CORE-03 del proyecto.
    """

    def __init__(self):
        """Inicializa el visitor con estado limpio."""
        self.table_name = None
        self.columns = []
        self.conditions = []
        self.errors = []

    def visitQuery(self, ctx):
        """
        Procesa la regla principal query.

        Args:
            ctx: Contexto del query del parser

        Returns:
            str: Resultado del selectStatement
        """
        return self.visit(ctx.selectStatement())

    def visitSelectStatement(self, ctx):
        """
        Procesa un SELECT statement completo.

        Args:
            ctx: Contexto del SELECT statement del parser

        Returns:
            str: Consulta Cypher completa
        """
        # Obtener nombre de tabla
        self.table_name = ctx.tableName().getText()

        # Visitar la lista de columnas
        self.visit(ctx.selectList())

        # Visitar WHERE clause si existe
        if ctx.whereClause():
            self.visit(ctx.whereClause())

        # Construir consulta Cypher
        return self._build_cypher_query()

    def visitSelectAll(self, ctx):
        """Procesa SELECT * - retorna todas las propiedades del nodo."""
        self.columns = ["*"]

    def visitSelectColumns(self, ctx):
        """Procesa SELECT con columnas específicas."""
        self.columns = [col.getText() for col in ctx.columnName()]

    def visitWhereClause(self, ctx):
        """Procesa la cláusula WHERE."""
        condition_result = self.visit(ctx.condition())
        if condition_result:
            self.conditions.append(condition_result)

    def visitAndCondition(self, ctx):
        """Procesa condición con AND."""
        left = self.visit(ctx.condition(0))
        right = self.visit(ctx.condition(1))
        return f"({left} AND {right})"

    def visitOrCondition(self, ctx):
        """Procesa condición con OR."""
        left = self.visit(ctx.condition(0))
        right = self.visit(ctx.condition(1))
        return f"({left} OR {right})"

    def visitComparisonCondition(self, ctx):
        """
        Procesa condición de comparación (col = value, col > value, etc).

        Mapea operadores SQL a Cypher:
        - = -> =
        - != o <> -> <>
        - <, >, <=, >= -> <, >, <=, >=
        """
        column = ctx.columnName().getText()
        operator = self._get_operator(ctx.comparisonOp())
        value = self.visit(ctx.value())

        return f"n.{column} {operator} {value}"

    def visitParenCondition(self, ctx):
        """Procesa condición entre paréntesis."""
        return f"({self.visit(ctx.condition())})"

    def visitStringValue(self, ctx):
        """Procesa valor de cadena."""
        # Mantener las comillas simples para Cypher
        return ctx.getText()

    def visitNumberValue(self, ctx):
        """Procesa valor numérico."""
        return ctx.getText()

    def visitBooleanTrue(self, ctx):
        """Procesa valor booleano true."""
        return "true"

    def visitBooleanFalse(self, ctx):
        """Procesa valor booleano false."""
        return "false"

    def visitNullValue(self, ctx):
        """Procesa valor NULL."""
        return "null"

    def _get_operator(self, op_ctx):
        """
        Obtiene el operador Cypher equivalente al operador SQL.

        Args:
            op_ctx: Contexto del operador de comparación

        Returns:
            str: Operador Cypher equivalente
        """
        op_text = op_ctx.getText()

        # Mapeo de operadores SQL a Cypher
        operator_map = {
            "=": "=",
            "!=": "<>",
            "<>": "<>",
            "<": "<",
            ">": ">",
            "<=": "<=",
            ">=": ">=",
        }

        return operator_map.get(op_text, op_text)

    def _build_cypher_query(self):
        """
        Construye la consulta Cypher final.

        Formato básico según CORE-03:
        MATCH (n:TableName)
        [WHERE n.col = value]
        RETURN n.col1, n.col2 [o n para SELECT *]

        Returns:
            str: Consulta Cypher completa
        """
        if not self.table_name:
            raise ValueError("No se especificó nombre de tabla")

        # Construir cláusula MATCH
        cypher_parts = [f"MATCH (n:{self._capitalize_label(self.table_name)})"]

        # Agregar cláusula WHERE si hay condiciones
        if self.conditions:
            where_clause = " AND ".join(self.conditions)
            cypher_parts.append(f"WHERE {where_clause}")

        # Construir cláusula RETURN
        if "*" in self.columns:
            cypher_parts.append("RETURN n")
        else:
            return_cols = ", ".join([f"n.{col}" for col in self.columns])
            cypher_parts.append(f"RETURN {return_cols}")

        return "\n".join(cypher_parts)

    def _capitalize_label(self, label):
        """
        Capitaliza el label de Neo4j siguiendo convenciones.

        Args:
            label: Nombre de la tabla en SQL

        Returns:
            str: Label capitalizado para Neo4j
        """
        # Convención: Primera letra mayúscula
        return label.capitalize()


def translate_sql_to_cypher(sql_query: str) -> dict:
    """
    Función principal para traducir SQL a Cypher.

    Args:
        sql_query: Consulta SQL a traducir

    Returns:
        dict: Diccionario con 'cypher' (consulta traducida) y opcionalmente 'errors'

    Raises:
        ValueError: Si la consulta SQL es inválida
    """
    from antlr4 import CommonTokenStream, InputStream
    from antlr4.error.ErrorListener import ErrorListener

    from app.core.parser.generated.SQLSimpleLexer import SQLSimpleLexer
    from app.core.parser.generated.SQLSimpleParser import SQLSimpleParser

    class SQLErrorListener(ErrorListener):
        """Captura errores de parsing."""

        def __init__(self):
            super().__init__()
            self.errors = []

        def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
            self.errors.append(f"Línea {line}:{column} - {msg}")

    try:
        # Crear input stream
        input_stream = InputStream(sql_query)

        # Crear lexer con manejo de errores
        lexer = SQLSimpleLexer(input_stream)
        error_listener = SQLErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        # Crear stream de tokens
        token_stream = CommonTokenStream(lexer)

        # Crear parser con manejo de errores
        parser = SQLSimpleParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        # Parsear la consulta
        tree = parser.query()

        # Verificar errores de parsing
        if error_listener.errors:
            return {
                "cypher": None,
                "errors": error_listener.errors,
                "success": False,
            }

        # Traducir con el visitor
        visitor = SQLToCypherVisitor()
        cypher_query = visitor.visit(tree)

        return {"cypher": cypher_query, "errors": [], "success": True}

    except Exception as e:
        return {
            "cypher": None,
            "errors": [f"Error durante la traducción: {str(e)}"],
            "success": False,
        }
