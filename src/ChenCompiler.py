#===================================================================================
# Chen Zheng COMP589-15D Project.
# Version 0.2
# Compiler v0.1 Definition of all tokens.
# Compiler v0.2 Initialization of symbol table for all tokens.
# Compiler v0.3 Lexical Analyser, the Scanner, print Hello World.
#===================================================================================

import sys
#===================================================================================
### GLOBAL variables Deceleration. ###

srcFileName = "../programs/simple_hello.txt";  # Path to the source code file.
outputFileName = "../programs/simple_hello.obj";  # path for the output machine code obj file.

src = [];  # The input file is stored as an array of string lines.
linenumber = 0;  # The current line number of source code.
charIndex = 0;  # The position of current character in the current line.
EOF = chr(0);  # The end of file character.

outputArray = [];  # An temporary array to hold all machine code/instructions.  

varptr = 900  # Arbitrary base address of memory for variables, which starts from this address.
codeptr = 10  # Address to output next instruction (for machine code, 1-9 are reserved).

token = None;
# Reserved Token Symbols.
tokenNames = \
    [ "unknownToken", "code", "declare","assignsym", "idsym", "varsym",
      "assignsym", "leftbrace", "rightbrace",
     "equals", "plus", "minus", "multiply", "devine",
     "print", "endfile" ]
    # More symbol will be added.

# Define tokens as variables in the compiler.
unknownToken, codesym, declaresym, idsym, varsym, \
assignsym, leftbrace, rightbrace, \
equals, plus, minus, multiply, devine, \
printsym, endfile = range(0, len(tokenNames));

class symbol:
    name = None;
    token = None;
    value = None;
    
    def __init__(self, name, token, value=0):
        self.name = name;
        self.token = token;
        self.value = value;

    def __call__(self):
        self.token.__str__;

symtable = {};  # The Symbol table, a dictionary of predefined symbols, indexed by name.
#===================================================================================


#===================================================================================
### Symbol Table Management Routines. ### 

# Adds a symbol entry to the symbol table.
def addToSymTable(name, token):
    symtable[name] = symbol(name, token);
    return symtable[name];

# Looks up a given token symbol in the predefined symbol table and returns if it's found.
def lookup(thisName):
    if symtable.has_key(thisName):
        return symtable[thisName];
    else: return None;

# Initializes the symbol table by adding all the predefined tokens.
def initSymbolTable():
    addToSymTable('code', codesym);
    addToSymTable('declare', declaresym);
    addToSymTable('var', varsym);
    addToSymTable('print', printsym);
    
    addToSymTable('=', assignsym);
    addToSymTable('==', equals);
    addToSymTable('+', plus);
    addToSymTable('-', minus);
    addToSymTable('*', multiply);
    addToSymTable('/', devine);
    
    addToSymTable(EOF, endfile);

#===================================================================================



#===================================================================================
# Main Function of the compiler, loads the source code file and output a object file.
def main():
    global srcFileName;
    global src;
    
    initSymbolTable();
    
    srcFile = open(srcFileName);
    src = srcFile.readlines();
    srcFile.close();
    
    #code() # Process the input source code.
    #saveObj() # Output the machine code to a object file.
    
    sys.exit();