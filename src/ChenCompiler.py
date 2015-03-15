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
compilerVersion = 0.3;

srcFileName = "../code/hello.txt";  # Path to the source code file.
outputFileName = "../code/hello.obj";  # path for the output machine code obj file.

src = [];  # The input file is stored as an array of string lines.
linenumber = 0;  # The current line number of source code.
charIndex = 0;  # The position of current character in the current line.
EOF = chr(0);  # The end of file character.

outputArray = [];  # An temporary array to hold all machine code/instructions.  

varptr = 900  # Arbitrary base address of memory for variables, which starts from this address.
codeptr = 10  # Address to output next instruction (for machine code, 1-9 are reserved).

token = None;  # A symbol, will be modified by each call of getToken().
ignoreCharacters = ["\t", " ", "\n"];  # Ignore tabs, spaces and new lines.

# Reserved Token Symbols.
tokenNames = \
    [ "unknownToken", "codesym", "declare", "assignsym", "idsym", "varsym", "number",
     "leftbrace", "rightbrace", "leftbracket", "rightbracket",
     "equals", "plus", "minus", "multiply", "devine",
     "semicolon", "comma", "sharp",
     "print", "stringvalue", "endfile" ]
    # More symbol will be added.

# Define tokens as variables in the compiler.
unknownToken, codesym, declaresym, idsym, varsym, number, \
assignsym, leftbrace, rightbrace, leftbracket, rightbracket, \
equals, plus, minus, multiply, devine, \
semicolon, comma, sharp, \
printsym, stringvalue, endfile = range(0, len(tokenNames));

class symbol:
    name = None;  # String representation
    token = None;  # Corresponding reserved token or code defined token.
    value = None;  # For number tokens.
    address = 0;  # For variables, their runtime address
    
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
    else: 
        return None;

# Initializes the symbol table by adding all the predefined tokens.
def initSymbolTable():
    addToSymTable('code', codesym);
    addToSymTable('declare', declaresym);
    addToSymTable('var', varsym);
    addToSymTable('print', printsym);
    
    addToSymTable(',', comma);
    addToSymTable(';', semicolon);
    addToSymTable('#', sharp);
    addToSymTable('{', leftbrace);
    addToSymTable('}', rightbrace);
    addToSymTable('(', leftbracket);
    addToSymTable(')', rightbracket);
    
    
    addToSymTable('=', assignsym);
    addToSymTable('==', equals);
    addToSymTable('+', plus);
    addToSymTable('-', minus);
    addToSymTable('*', multiply);
    addToSymTable('/', devine);
    
    addToSymTable(EOF, endfile);

def dumpSymbolTable():
    print("=== Symbol Table Contents ===");
    for name in symtable.keys():
        tempToken = symtable[name];
        if tempToken.token == idsym: # Only print symbols from source code.
            printToken(tempToken);
            
# Printer function for given symbol.
def printToken(inputToken):
    if inputToken.token == idsym:  # For id symbols.
        print "Token = %10s %-10s adr = %3d" % (tokenNames[inputToken.token], inputToken.name, inputToken.address);
    elif inputToken.token == number:  # For numbers.
        print "Token = %10s %d" % (tokenNames[inputToken.token], inputToken.value);
    else:  # Other symbols.
        print "Token = %10s" % tokenNames[inputToken.token];

# Printer function for compiling time error messages.
def printError(msg):
    global linenumber;
    
    print ("*" * 20, "ERROR: " + msg, "*" * 23);  # Print header
    print ("Line Number: %d" % (linenumber + 1));  # Print which line the error is.
    printToken(token);  # Print the token the error occurred on
    print ("*" * 50);  # Print footer

#===================================================================================

#===============================================================================
# Scanner routines
#===============================================================================
# Get the next valid character.
def getCh():
    global charIndex;
    global linenumber;
    global src;
    
    while True:  # Loop until valid character is found.
        if linenumber < len(src): 
            line = src[linenumber];  # Pick up a line from source file.
        else:
            sys.exit(1);  # No more source lines to process, exit.
            
        if charIndex < len(line):  # If it is the end of current line,
            ch = line[charIndex];  # if not, get the character.
            charIndex += 1;  # And move the line pointer to next char for next loop.
        else:
            charIndex = 0;  # if it is the end of current line, reset the character pointer.
            linenumber += 1;  # Increment of line number, to next line.
            continue;
        
        if ch == "#":  # Ignore the comment symbol and the characters after it.
            while ch != "\n":
                ch = line[charIndex];
                charIndex += 1;
            
        if ch == "\n":
            ch = " ";  # A new line, reset the ch variable.
            
        if ch == "?":  # If ch is ?, display the symbol table.
            dumpSymbolTable();
            continue;
        
        return ch;

# Jump back a character.
def ungetCh():
    global charIndex;
    charIndex = charIndex - 1;
    
# Get the next valid token.
def getToken():
    global token;
    global tokenNames;
    
    ch = getCh();  # Get next character.
    while ch in ignoreCharacters:  # Ignore tabs, spaces and new lines.
        ch = getCh(); 
        
    # If this character is alphabetic then it's a start of a token, either reserved or id.
    if ch.isalpha():  
        tempName = "";  # Temp variable to hold and build the whole token string.
        while ch.isalpha() or ch.isdigit() or ch == "_":  # Building String while it's a valid ch.
            tempName = tempName + ch; 
            ch = getCh();
        
        ungetCh();  # Jump back to the previous character since it's not used.
        
        tempName = tempName.lower();  # This compiler is not case sensitive.
        token = lookup(tempName);  # See if this is a reserved token or known token.
        if token is None:  # if not known, then add it to symbol table.
            token = addToSymTable(tempName, idsym);
        
        return;
    
    # If this character is numeric then return Token = number & token.value = binary value.
    elif ch.isdigit():
        tempNumber = "";
        while ch.isdigit():
            tempNumber = tempNumber + ch;
            ch = getCh();
        
        ungetCh();  # Jump back to the previous character since it's not used. 
        
        token = symbol(ch, number, value=intern(tempNumber));  # Set up the number token.
        
        return
    
    # If this character is a quotation ", then return Token = string & token.value = string_value.
    elif ch == '"':
        tempString = "";
        ch = getCh();
        
        while ch != '"':
            tempString = tempString + ch; 
            ch = getCh();
        
        token = symbol(tempString, stringvalue);
        return
    
    # If this character is one of those special characters
    elif ch in ["#", "{", "}", "(", ")", "[", "]", "+", "-", "*", "/", ",", ";", EOF]:
        token = lookup(ch);
    
    else:
        printError("Unknown character detected!");
        sys.exit(1);


#===================================================================================
# Main list of statements processing function
def stmtList():
    stmt();
    
# Single statement processing function.
def stmt():
    if token.token == printsym:
        printStmt();

# For each statement, there is a particular statement function.
def printStmt():
    getToken();
    
        
#===================================================================================


#===================================================================================
# Main code processing function
def code():
    getToken();  # Get the first token of the input file.
    # printToken(token);
    
    if token.token == codesym:  # Skip CODE keyword.
        getToken();
    else: printError("CODE keyword missing...");
    
    if token.token == idsym:  # Identifier expected to be the code name.
        getToken();
    else: printError("Code name missing...");
    
    if token.token == semicolon:  # Semicolon is the end of each line.
        getToken();
    else: printError("Semicolen missing...");
    
    if token.token == leftbrace:  # "{" is the start of code statements.
        getToken();
    else: printError(" '{' missing...");
    
    stmtList();
    
    
#===================================================================================


#===================================================================================
# Main Function of the compiler, loads the source code file and output a object file.
def main():
    print(compilerVersion);
    
    global srcFileName;
    global src;
    
    initSymbolTable();
    
    srcFile = open(srcFileName);
    src = srcFile.readlines();
    srcFile.close();
    
    
    code();  # Process the input source code.
    # printObj() # Display the machine code to a console.
    # saveObj() # Save the machine code to a object file.
    
    dumpSymbolTable();
    
    sys.exit();



#===================================================================================
###### Compiler Main Call #####
main();
