# Generated from SQLSimple.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SQLSimpleParser import SQLSimpleParser
else:
    from SQLSimpleParser import SQLSimpleParser

# This class defines a complete generic visitor for a parse tree produced by SQLSimpleParser.

class SQLSimpleVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SQLSimpleParser#query.
    def visitQuery(self, ctx:SQLSimpleParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#selectStatement.
    def visitSelectStatement(self, ctx:SQLSimpleParser.SelectStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#SelectAll.
    def visitSelectAll(self, ctx:SQLSimpleParser.SelectAllContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#SelectColumns.
    def visitSelectColumns(self, ctx:SQLSimpleParser.SelectColumnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#whereClause.
    def visitWhereClause(self, ctx:SQLSimpleParser.WhereClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#ComparisonCondition.
    def visitComparisonCondition(self, ctx:SQLSimpleParser.ComparisonConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#ParenCondition.
    def visitParenCondition(self, ctx:SQLSimpleParser.ParenConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#OrCondition.
    def visitOrCondition(self, ctx:SQLSimpleParser.OrConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#AndCondition.
    def visitAndCondition(self, ctx:SQLSimpleParser.AndConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#Equal.
    def visitEqual(self, ctx:SQLSimpleParser.EqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#NotEqual.
    def visitNotEqual(self, ctx:SQLSimpleParser.NotEqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#LessThan.
    def visitLessThan(self, ctx:SQLSimpleParser.LessThanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#GreaterThan.
    def visitGreaterThan(self, ctx:SQLSimpleParser.GreaterThanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#LessThanOrEqual.
    def visitLessThanOrEqual(self, ctx:SQLSimpleParser.LessThanOrEqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#GreaterThanOrEqual.
    def visitGreaterThanOrEqual(self, ctx:SQLSimpleParser.GreaterThanOrEqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#tableName.
    def visitTableName(self, ctx:SQLSimpleParser.TableNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#columnName.
    def visitColumnName(self, ctx:SQLSimpleParser.ColumnNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#StringValue.
    def visitStringValue(self, ctx:SQLSimpleParser.StringValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#NumberValue.
    def visitNumberValue(self, ctx:SQLSimpleParser.NumberValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#BooleanTrue.
    def visitBooleanTrue(self, ctx:SQLSimpleParser.BooleanTrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#BooleanFalse.
    def visitBooleanFalse(self, ctx:SQLSimpleParser.BooleanFalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLSimpleParser#NullValue.
    def visitNullValue(self, ctx:SQLSimpleParser.NullValueContext):
        return self.visitChildren(ctx)



del SQLSimpleParser