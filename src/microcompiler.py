

""" Giovanni's MicroCompiler Demo

<program>       ::=     { <id> ; <vars > <stmtlist>  }
<vars>          ::=     V { <id> ; }                       % DECLARATIONS

<stmtlist>      ::=     <stmt> { ; <stmt> }
<stmt>          ::=     P <id>  |  <id> = <expr>      

<expr>          ::=     <factor> {  (+ | -)   <factor> }   % No precedence
<factor>                ::=     ID | Number                                                             

"""

import sys

#===============================================================================
# # Lexical Analyser - the "Scanner" - Define the TokenTypes
#===============================================================================

tokenNames =\
  [ "unknownToken", "idsym", "assignsym", "leftbrace", "rightbrace",
    "varsym", "semicolon", "whilesym", "leftbracket", "rightbracket",
    "printsym", "ifsym", "equals", "notequals", "lessthan", "greaterthan",
    "number", "plus", "minus", "endfile"]

# define the tokens as variables
unknownToken, idsym, assignsym, leftbrace, rightbrace,\
    varsym, semicolon, whilesym, leftbracket, rightbracket,\
    printsym, ifsym, equals, notequals, lessthan, greaterthan,\
    number, plus, minus, endfile = range(0, len(tokenNames))
              
#===============================================================================
class symbol:
#===============================================================================
    name      = None   # String representation
    token     = None;  # Corresponding token
    address   = 0;     # For variables, their runtime address
    value     = None   # on defined for numbers

    def __init__(self, name, token, value = 0):
        self.name    = name
        self.token   = token
        self.address = 0   # for identifiers, their address
        self.value   = value   # for numbers, their value

              
symtbl = {}; # The Symbol Table, a dictionary of symbols indexed by name

#======================================================================
# GLOBALS for output of Lexical Analyser
# Set by each call to GeToken()

token = None;   # A symbol

line      = "\n" # the complex source file as a string
charIndex = 0    # the position in the source

linenumber= 0    # The current  number

EOF = chr(0)
#======================================================================
# Run Time Code Generation Variables

varptr  = 500   # Arbitrary base address of memory for variables
codeptr = 10    # Address to output next instruction (for code)


#===============================================================================
#                    Symbol Table Management Routines
#===============================================================================

#===============================================================================
def addToSymTbl (name, token):
#===============================================================================
    symtbl[name] = symbol(name, token)  # Add a new symbol to the dictionary
    return symtbl[name]


#===============================================================================
def lookup (thisName): 
#===============================================================================
    "# Find a given identifier in the Symbol Table, Return the symtbl entry"
    if symtbl.has_key(thisName):  # thisName has been seen before
        return symtbl[thisName]   # return the symtbl entry
    else: return None


#===============================================================================
def initSymTbl():
#===============================================================================
    "# Initialise Symbol Table, and preload reserved words"
    addToSymTbl('var',   varsym)   # VAR
    addToSymTbl('while', whilesym) # WHILE
    addToSymTbl('print', printsym) # PRINT
    addToSymTbl('if',    ifsym)    # IF

    # Now add symbols - NB only single character symbols are here
    #                      multicharacter one like ">=" are still to do
    addToSymTbl( '=', assignsym)
    addToSymTbl( '#', notequals)
    addToSymTbl( '<', lessthan)
    addToSymTbl( '>', greaterthan)
    addToSymTbl( '{', leftbrace )
    addToSymTbl( '}', rightbrace)
    addToSymTbl( '(', leftbracket)
    addToSymTbl( ')', rightbracket)
    addToSymTbl( '+', plus )
    addToSymTbl( '-', minus)
    addToSymTbl( ';', semicolon)
    addToSymTbl( EOF, endfile)


#===============================================================================
#                       Scanner Diagnostics
#===============================================================================
def printToken(tok):
#===============================================================================
    " - display the specified token."
    if tok.token == idsym:
       print "Token = %10s,  %-10s  adr = %3d" %\
             (tokenNames[tok.token], tok.name, tok.address)
    elif tok.token == number:
       print "Token = %10s  %d" % (tokenNames[tok.token], tok.value)
    else:
       print "Token = %10s" %  tokenNames[tok.token]

#==============================?=================================================
def dumpSymTbl():
#===============================================================================
    """ Dump all the tokens in the symboltable """
    print(" *** Symbol Table ***")
    for name in symtbl.keys():  # keys is a list of the names (printable form of tokens)
        tok = symtbl[name]
        if tok.token == idsym:
            printToken(tok)

#===============================================================================
def getch():
#===============================================================================
    global line
    global charIndex
    global linenumber

    while True:
        if charIndex < len(line):        # See if used up current line
            ch = line[charIndex]        # if not, get character
            charIndex = charIndex+1     # & move pointer for next time
        else:
            # line = f.readline()
            # if  line == "": line = EOF
            print "--> ",
            line = raw_input() +"\n" # read new line, adding \n so it's like f.readline()
            charIndex = 0       # & reset character pointer
            linenumber = linenumber + 1
            continue
        
        if ch == "\n": 
            ch = " "                # A newline is a token separator
            
        if ch == '?':
            dumpSymTbl()
            continue
        return ch   

#===============================================================================
def ungetch():
#===============================================================================
    """ Unget the next character peeked at when building variables, numbers
        and when distinguishing between >= and > ...
    """    
    global charIndex;
    charIndex = charIndex-1;
    
#===============================================================================
def getoken():
#===============================================================================
    """ GETOKEN - Put next token into the global TOKEN """
    global token
    
    ch = getch()             # skip whitespace
    while ch in ["\t", " ", "\n"]: 
        ch = getch()    
    
    # If ch is alphabetic then this is start of reserved word or an identifier
    if ch.isalpha():  # Letter therefore it's either identifier or reserved word
        name = ""
        while ch.isalpha() or ch.isdigit() or ch == "_":
            name = name + ch
            ch = getch()

        ungetch()                             # let terminator be used next time
        
        token = lookup(name)                  # See if token's known
        if token is None:                     # if not
            token = addToSymTbl(name, idsym)  #   add as 'idsym'-IDENTIFIER

        return   # we've set token.token to either id or tokentype of reserved word
          
    #---------------------------------------------------------------------
    # If it's numeric return TOKEN=number & token.value = binary value
    elif ch.isdigit():
        # In the real version, build number and don't forget to end with ungetch()
        token = symbol(ch, number, value = int(ch)) # simplistic SINGLE DIGIT Ascii to Binary
        return
    #---------------------------------------------------------------------
    # Single character tokens
    elif ch in ["=",  "#",  "<",  ">",  "{", "}", "(", ")", "+" , "-" , ";", EOF]:
      token = lookup(ch)  # preloaded with appropriate token       
    else:
        print "Unknown character -->%s<- decimal %d" % (ch,ord(ch))
        sys.exit(1) # Abort Compilation

#======================================================================
# THE GRAMMAR

# <program>       ::=     { <id> ; <vars > <stmtlist>  }
# <vars>          ::=     var { <id> ; }                    % DECLARATIONS

# <stmtlist>      ::=     <stmt> { ; <stmt> }
# <stmt>          ::=     print <id>     
#                         <id> = <expr>  

# <expr>          ::=     <factor> {  (+ | -)   <factor> }   % No precedence
# <factor>        ::=     ID | Number                                                             

#======================================================================
#                  Centralised Parser Error Message handler
#======================================================================

#===============================================================================
def error (msg):
#===============================================================================
    print line
    print "-" * charIndex,"^"
    print("Error on  %d - %s\n" % (number, msg))       
    printToken(token)
    print("\n")

#===============================================================================
def emit (memadr, opcode, parameter):
#===============================================================================
    """EMIT CODE - Emit a  of code with a Parameter
    if first arg is zero - (the memory address), use and incr CODEPTR"""
    global codeptr
    
    if (memadr == 0):
        memadr = codeptr
        codeptr = codeptr+1
    print "%6d  %-8s %-7d" % (memadr, opcode, parameter)

#======================================================================
# VARIABLE DECLARATIONS
#   <vars>              ::=     V { <id> ; }

#===============================================================================
def vars() :
#===============================================================================
    global varptr;
    getoken(); #skip VARSYM - already been recognised
    while (token.token == idsym):
        if token.address != 0: 
           print("%c already declared\n", token.name);
        else:
           symtbl[token.name].address = varptr;
           varptr = varptr +1
      
        getoken(); #skip past identifier
        if token.token == semicolon: getoken()  #skip ;
        else: error("semicolon expected in declaration")  
        

#======================================================================
# STMTLIST 
# <stmtlist>  ::= <stmt> { ; <stmt> }    #optional multi-statements

#===============================================================================
def stmtList():
#===============================================================================
    stmt()
    while (token.token == semicolon):
        getoken()   #skip semicolon
        stmt()

#======================================================================
# STMT 

#===============================================================================
def stmt():
#===============================================================================
    """  <stmt> ::=  print <expression>  |  <id> = <expression>          
    """
    global codeptr
    
    thisStmtAdr = codeptr   # Jump DEMO - not part of Stmt
    
    if  token.token == printsym:
        printStmt() 
    elif token.token == idsym:
        assignStmt()
    else: 
        error("Expected start of a statement")
    
    emit (0, "jumpDemo-to start of statement:  jump", thisStmtAdr)  # Jump DEMO

#===============================================================================
def printStmt():
#===============================================================================
    """   <printStmt> ::= print <expression>"""
    
    getoken()             # skip "print"
    expression()          # on return, expr result (at runtime) will be in ACC
    emit(0, "output", 0)  # Memory address 0 is the ACC
   

#===============================================================================
def assignStmt():
#===============================================================================
    """
        <id> = <expression> 
    """
    whichidentifier = token      # Remember which ID on Left
    getoken()                    # Get token after identifier
    if token.token == assignsym:
         getoken()
    else:
         error("Expected = in assignment statement")
    expression()
    # Save result into LHS runtime address


#===============================================================================
def expression():
#===============================================================================
    """
       Leaves result in ACC at runtime 
       Use addresses 999 & 998 as Temporary variables
 
       <expression> ::=  <factor> {  (+ | -)  <factor> }
    """
    factor()
    while token.token == plus or token.token == minus: 
        op = token                        # remember +/-
        getoken()                         # skip past +/-
        emit(0, "store", 999)             # Save current result
        factor()                          # Evaluate next factor
        if op.token == plus:
            emit(0, "add", 999)
        else:  # Subtract - have to swap operand order
            emit(0, "store", 998)
            emit(0, "load" , 999)
            emit(0, "subtract", 998)      # Leaves result in Acc

#===============================================================================
def factor():
#===============================================================================
    """
      # FACTOR() - leaves result in ACC at runtime
          <factor> ::= identifier | number
    """

    if token.token == idsym: 
        emit(0, "load",  token.address)
        getoken()
    elif token.token == number: 
        emit(0, "loadv", token.value)
        getoken()    
    else:
        error("Start of Factor expected")      

        
#===============================================================================
def program():
#===============================================================================
    """ # PROGRAM - Start production of the grammar
        #  <program> ::= { <id> ; <vars > <stmtlist>  }
    """
    if token.token == leftbrace: getoken()
    else: error(" { expected")
    
    if token.token == idsym: getoken()
    else: error("Program name expected")
    
    if token.token == semicolon: getoken()
    else: error("Semicolon expected")
    
    if token.token == varsym   : vars()
    
    stmtList()
    
    if token.token == rightbrace: 
        print("\n*** Compilation finished ***\n")
    else: error(" } expected")


# Compiler main
#======================================================================
def main():
#======================================================================        
    global line
    global srcfile
    global charIndex
           
    initSymTbl()
#     srcfile = open("tiny.txt", r)
#     line = f.readline()        # readline
     
    line = """{  G;
                 var a; b; c;
                 print a;\n"""
    charIndex = 0

    debugScanner = False
    if debugScanner:   # Scanner Test Routine - Read a line and display the tokens
       getoken()                       
       while token.token is not None:   # Skeleton for testing Scanner
           printToken(token)
           getoken()       
       sys.exit(1)
    else:                              
       getoken()                       # Parse Program according to the grammar
       program()                       # Call start non-terminal handler

#===============================================================================
# Main Compiler starts here
#===============================================================================
print "Microcompiler.py v0.2"
main()

#   getoken()
        
#=======================================================================
# *** That's it folks - written by Giovanni Moretti - April 27, 2011 ***
#=======================================================================
