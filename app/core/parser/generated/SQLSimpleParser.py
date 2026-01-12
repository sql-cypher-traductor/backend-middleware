# Generated from SQLSimple.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,24,84,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,3,1,27,8,1,1,2,
        1,2,1,2,1,2,5,2,33,8,2,10,2,12,2,36,9,2,3,2,38,8,2,1,3,1,3,1,3,1,
        4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,52,8,4,1,4,1,4,1,4,1,4,1,4,
        1,4,5,4,60,8,4,10,4,12,4,63,9,4,1,5,1,5,1,5,1,5,1,5,1,5,3,5,71,8,
        5,1,6,1,6,1,7,1,7,1,8,1,8,1,8,1,8,1,8,3,8,82,8,8,1,8,0,1,8,9,0,2,
        4,6,8,10,12,14,16,0,0,89,0,18,1,0,0,0,2,21,1,0,0,0,4,37,1,0,0,0,
        6,39,1,0,0,0,8,51,1,0,0,0,10,70,1,0,0,0,12,72,1,0,0,0,14,74,1,0,
        0,0,16,81,1,0,0,0,18,19,3,2,1,0,19,20,5,0,0,1,20,1,1,0,0,0,21,22,
        5,1,0,0,22,23,3,4,2,0,23,24,5,2,0,0,24,26,3,12,6,0,25,27,3,6,3,0,
        26,25,1,0,0,0,26,27,1,0,0,0,27,3,1,0,0,0,28,38,5,15,0,0,29,34,3,
        14,7,0,30,31,5,16,0,0,31,33,3,14,7,0,32,30,1,0,0,0,33,36,1,0,0,0,
        34,32,1,0,0,0,34,35,1,0,0,0,35,38,1,0,0,0,36,34,1,0,0,0,37,28,1,
        0,0,0,37,29,1,0,0,0,38,5,1,0,0,0,39,40,5,3,0,0,40,41,3,8,4,0,41,
        7,1,0,0,0,42,43,6,4,-1,0,43,44,3,14,7,0,44,45,3,10,5,0,45,46,3,16,
        8,0,46,52,1,0,0,0,47,48,5,17,0,0,48,49,3,8,4,0,49,50,5,18,0,0,50,
        52,1,0,0,0,51,42,1,0,0,0,51,47,1,0,0,0,52,61,1,0,0,0,53,54,10,4,
        0,0,54,55,5,4,0,0,55,60,3,8,4,5,56,57,10,3,0,0,57,58,5,5,0,0,58,
        60,3,8,4,4,59,53,1,0,0,0,59,56,1,0,0,0,60,63,1,0,0,0,61,59,1,0,0,
        0,61,62,1,0,0,0,62,9,1,0,0,0,63,61,1,0,0,0,64,71,5,9,0,0,65,71,5,
        10,0,0,66,71,5,11,0,0,67,71,5,12,0,0,68,71,5,13,0,0,69,71,5,14,0,
        0,70,64,1,0,0,0,70,65,1,0,0,0,70,66,1,0,0,0,70,67,1,0,0,0,70,68,
        1,0,0,0,70,69,1,0,0,0,71,11,1,0,0,0,72,73,5,19,0,0,73,13,1,0,0,0,
        74,75,5,19,0,0,75,15,1,0,0,0,76,82,5,20,0,0,77,82,5,21,0,0,78,82,
        5,6,0,0,79,82,5,7,0,0,80,82,5,8,0,0,81,76,1,0,0,0,81,77,1,0,0,0,
        81,78,1,0,0,0,81,79,1,0,0,0,81,80,1,0,0,0,82,17,1,0,0,0,8,26,34,
        37,51,59,61,70,81
    ]

class SQLSimpleParser ( Parser ):

    grammarFileName = "SQLSimple.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'='", "<INVALID>", "'<'", "'>'", "'<='", 
                     "'>='", "'*'", "','", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "SELECT", "FROM", "WHERE", "AND", "OR", 
                      "TRUE", "FALSE", "NULL", "EQ", "NEQ", "LT", "GT", 
                      "LTE", "GTE", "ASTERISK", "COMMA", "LPAREN", "RPAREN", 
                      "IDENTIFIER", "STRING_LITERAL", "NUMBER", "WS", "LINE_COMMENT", 
                      "BLOCK_COMMENT" ]

    RULE_query = 0
    RULE_selectStatement = 1
    RULE_selectList = 2
    RULE_whereClause = 3
    RULE_condition = 4
    RULE_comparisonOp = 5
    RULE_tableName = 6
    RULE_columnName = 7
    RULE_value = 8

    ruleNames =  [ "query", "selectStatement", "selectList", "whereClause", 
                   "condition", "comparisonOp", "tableName", "columnName", 
                   "value" ]

    EOF = Token.EOF
    SELECT=1
    FROM=2
    WHERE=3
    AND=4
    OR=5
    TRUE=6
    FALSE=7
    NULL=8
    EQ=9
    NEQ=10
    LT=11
    GT=12
    LTE=13
    GTE=14
    ASTERISK=15
    COMMA=16
    LPAREN=17
    RPAREN=18
    IDENTIFIER=19
    STRING_LITERAL=20
    NUMBER=21
    WS=22
    LINE_COMMENT=23
    BLOCK_COMMENT=24

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def selectStatement(self):
            return self.getTypedRuleContext(SQLSimpleParser.SelectStatementContext,0)


        def EOF(self):
            return self.getToken(SQLSimpleParser.EOF, 0)

        def getRuleIndex(self):
            return SQLSimpleParser.RULE_query

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuery" ):
                return visitor.visitQuery(self)
            else:
                return visitor.visitChildren(self)




    def query(self):

        localctx = SQLSimpleParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_query)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 18
            self.selectStatement()
            self.state = 19
            self.match(SQLSimpleParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SelectStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SELECT(self):
            return self.getToken(SQLSimpleParser.SELECT, 0)

        def selectList(self):
            return self.getTypedRuleContext(SQLSimpleParser.SelectListContext,0)


        def FROM(self):
            return self.getToken(SQLSimpleParser.FROM, 0)

        def tableName(self):
            return self.getTypedRuleContext(SQLSimpleParser.TableNameContext,0)


        def whereClause(self):
            return self.getTypedRuleContext(SQLSimpleParser.WhereClauseContext,0)


        def getRuleIndex(self):
            return SQLSimpleParser.RULE_selectStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSelectStatement" ):
                return visitor.visitSelectStatement(self)
            else:
                return visitor.visitChildren(self)




    def selectStatement(self):

        localctx = SQLSimpleParser.SelectStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_selectStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 21
            self.match(SQLSimpleParser.SELECT)
            self.state = 22
            self.selectList()
            self.state = 23
            self.match(SQLSimpleParser.FROM)
            self.state = 24
            self.tableName()
            self.state = 26
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 25
                self.whereClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SelectListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SQLSimpleParser.RULE_selectList

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class SelectColumnsContext(SelectListContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.SelectListContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def columnName(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SQLSimpleParser.ColumnNameContext)
            else:
                return self.getTypedRuleContext(SQLSimpleParser.ColumnNameContext,i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(SQLSimpleParser.COMMA)
            else:
                return self.getToken(SQLSimpleParser.COMMA, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSelectColumns" ):
                return visitor.visitSelectColumns(self)
            else:
                return visitor.visitChildren(self)


    class SelectAllContext(SelectListContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.SelectListContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ASTERISK(self):
            return self.getToken(SQLSimpleParser.ASTERISK, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSelectAll" ):
                return visitor.visitSelectAll(self)
            else:
                return visitor.visitChildren(self)



    def selectList(self):

        localctx = SQLSimpleParser.SelectListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_selectList)
        self._la = 0 # Token type
        try:
            self.state = 37
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [15]:
                localctx = SQLSimpleParser.SelectAllContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 28
                self.match(SQLSimpleParser.ASTERISK)
                pass
            elif token in [19]:
                localctx = SQLSimpleParser.SelectColumnsContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 29
                self.columnName()
                self.state = 34
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==16:
                    self.state = 30
                    self.match(SQLSimpleParser.COMMA)
                    self.state = 31
                    self.columnName()
                    self.state = 36
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhereClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(SQLSimpleParser.WHERE, 0)

        def condition(self):
            return self.getTypedRuleContext(SQLSimpleParser.ConditionContext,0)


        def getRuleIndex(self):
            return SQLSimpleParser.RULE_whereClause

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWhereClause" ):
                return visitor.visitWhereClause(self)
            else:
                return visitor.visitChildren(self)




    def whereClause(self):

        localctx = SQLSimpleParser.WhereClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_whereClause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 39
            self.match(SQLSimpleParser.WHERE)
            self.state = 40
            self.condition(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SQLSimpleParser.RULE_condition

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class ComparisonConditionContext(ConditionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ConditionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def columnName(self):
            return self.getTypedRuleContext(SQLSimpleParser.ColumnNameContext,0)

        def comparisonOp(self):
            return self.getTypedRuleContext(SQLSimpleParser.ComparisonOpContext,0)

        def value(self):
            return self.getTypedRuleContext(SQLSimpleParser.ValueContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComparisonCondition" ):
                return visitor.visitComparisonCondition(self)
            else:
                return visitor.visitChildren(self)


    class ParenConditionContext(ConditionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ConditionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LPAREN(self):
            return self.getToken(SQLSimpleParser.LPAREN, 0)
        def condition(self):
            return self.getTypedRuleContext(SQLSimpleParser.ConditionContext,0)

        def RPAREN(self):
            return self.getToken(SQLSimpleParser.RPAREN, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParenCondition" ):
                return visitor.visitParenCondition(self)
            else:
                return visitor.visitChildren(self)


    class OrConditionContext(ConditionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ConditionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def condition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SQLSimpleParser.ConditionContext)
            else:
                return self.getTypedRuleContext(SQLSimpleParser.ConditionContext,i)

        def OR(self):
            return self.getToken(SQLSimpleParser.OR, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrCondition" ):
                return visitor.visitOrCondition(self)
            else:
                return visitor.visitChildren(self)


    class AndConditionContext(ConditionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ConditionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def condition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SQLSimpleParser.ConditionContext)
            else:
                return self.getTypedRuleContext(SQLSimpleParser.ConditionContext,i)

        def AND(self):
            return self.getToken(SQLSimpleParser.AND, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAndCondition" ):
                return visitor.visitAndCondition(self)
            else:
                return visitor.visitChildren(self)



    def condition(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = SQLSimpleParser.ConditionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 8
        self.enterRecursionRule(localctx, 8, self.RULE_condition, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [19]:
                localctx = SQLSimpleParser.ComparisonConditionContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 43
                self.columnName()
                self.state = 44
                self.comparisonOp()
                self.state = 45
                self.value()
                pass
            elif token in [17]:
                localctx = SQLSimpleParser.ParenConditionContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 47
                self.match(SQLSimpleParser.LPAREN)
                self.state = 48
                self.condition(0)
                self.state = 49
                self.match(SQLSimpleParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 61
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,5,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 59
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
                    if la_ == 1:
                        localctx = SQLSimpleParser.AndConditionContext(self, SQLSimpleParser.ConditionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_condition)
                        self.state = 53
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 54
                        self.match(SQLSimpleParser.AND)
                        self.state = 55
                        self.condition(5)
                        pass

                    elif la_ == 2:
                        localctx = SQLSimpleParser.OrConditionContext(self, SQLSimpleParser.ConditionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_condition)
                        self.state = 56
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 57
                        self.match(SQLSimpleParser.OR)
                        self.state = 58
                        self.condition(4)
                        pass

             
                self.state = 63
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class ComparisonOpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SQLSimpleParser.RULE_comparisonOp

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class LessThanContext(ComparisonOpContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ComparisonOpContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LT(self):
            return self.getToken(SQLSimpleParser.LT, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLessThan" ):
                return visitor.visitLessThan(self)
            else:
                return visitor.visitChildren(self)


    class NotEqualContext(ComparisonOpContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ComparisonOpContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NEQ(self):
            return self.getToken(SQLSimpleParser.NEQ, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNotEqual" ):
                return visitor.visitNotEqual(self)
            else:
                return visitor.visitChildren(self)


    class LessThanOrEqualContext(ComparisonOpContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ComparisonOpContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LTE(self):
            return self.getToken(SQLSimpleParser.LTE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLessThanOrEqual" ):
                return visitor.visitLessThanOrEqual(self)
            else:
                return visitor.visitChildren(self)


    class EqualContext(ComparisonOpContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ComparisonOpContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EQ(self):
            return self.getToken(SQLSimpleParser.EQ, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEqual" ):
                return visitor.visitEqual(self)
            else:
                return visitor.visitChildren(self)


    class GreaterThanContext(ComparisonOpContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ComparisonOpContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def GT(self):
            return self.getToken(SQLSimpleParser.GT, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGreaterThan" ):
                return visitor.visitGreaterThan(self)
            else:
                return visitor.visitChildren(self)


    class GreaterThanOrEqualContext(ComparisonOpContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ComparisonOpContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def GTE(self):
            return self.getToken(SQLSimpleParser.GTE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGreaterThanOrEqual" ):
                return visitor.visitGreaterThanOrEqual(self)
            else:
                return visitor.visitChildren(self)



    def comparisonOp(self):

        localctx = SQLSimpleParser.ComparisonOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_comparisonOp)
        try:
            self.state = 70
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [9]:
                localctx = SQLSimpleParser.EqualContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 64
                self.match(SQLSimpleParser.EQ)
                pass
            elif token in [10]:
                localctx = SQLSimpleParser.NotEqualContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 65
                self.match(SQLSimpleParser.NEQ)
                pass
            elif token in [11]:
                localctx = SQLSimpleParser.LessThanContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 66
                self.match(SQLSimpleParser.LT)
                pass
            elif token in [12]:
                localctx = SQLSimpleParser.GreaterThanContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 67
                self.match(SQLSimpleParser.GT)
                pass
            elif token in [13]:
                localctx = SQLSimpleParser.LessThanOrEqualContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 68
                self.match(SQLSimpleParser.LTE)
                pass
            elif token in [14]:
                localctx = SQLSimpleParser.GreaterThanOrEqualContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 69
                self.match(SQLSimpleParser.GTE)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TableNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(SQLSimpleParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return SQLSimpleParser.RULE_tableName

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTableName" ):
                return visitor.visitTableName(self)
            else:
                return visitor.visitChildren(self)




    def tableName(self):

        localctx = SQLSimpleParser.TableNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_tableName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(SQLSimpleParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(SQLSimpleParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return SQLSimpleParser.RULE_columnName

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnName" ):
                return visitor.visitColumnName(self)
            else:
                return visitor.visitChildren(self)




    def columnName(self):

        localctx = SQLSimpleParser.ColumnNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_columnName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            self.match(SQLSimpleParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SQLSimpleParser.RULE_value

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class NullValueContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NULL(self):
            return self.getToken(SQLSimpleParser.NULL, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNullValue" ):
                return visitor.visitNullValue(self)
            else:
                return visitor.visitChildren(self)


    class NumberValueContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(SQLSimpleParser.NUMBER, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumberValue" ):
                return visitor.visitNumberValue(self)
            else:
                return visitor.visitChildren(self)


    class BooleanFalseContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FALSE(self):
            return self.getToken(SQLSimpleParser.FALSE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBooleanFalse" ):
                return visitor.visitBooleanFalse(self)
            else:
                return visitor.visitChildren(self)


    class StringValueContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING_LITERAL(self):
            return self.getToken(SQLSimpleParser.STRING_LITERAL, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStringValue" ):
                return visitor.visitStringValue(self)
            else:
                return visitor.visitChildren(self)


    class BooleanTrueContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a SQLSimpleParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def TRUE(self):
            return self.getToken(SQLSimpleParser.TRUE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBooleanTrue" ):
                return visitor.visitBooleanTrue(self)
            else:
                return visitor.visitChildren(self)



    def value(self):

        localctx = SQLSimpleParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_value)
        try:
            self.state = 81
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [20]:
                localctx = SQLSimpleParser.StringValueContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 76
                self.match(SQLSimpleParser.STRING_LITERAL)
                pass
            elif token in [21]:
                localctx = SQLSimpleParser.NumberValueContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 77
                self.match(SQLSimpleParser.NUMBER)
                pass
            elif token in [6]:
                localctx = SQLSimpleParser.BooleanTrueContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 78
                self.match(SQLSimpleParser.TRUE)
                pass
            elif token in [7]:
                localctx = SQLSimpleParser.BooleanFalseContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 79
                self.match(SQLSimpleParser.FALSE)
                pass
            elif token in [8]:
                localctx = SQLSimpleParser.NullValueContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 80
                self.match(SQLSimpleParser.NULL)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[4] = self.condition_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def condition_sempred(self, localctx:ConditionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 3)
         




