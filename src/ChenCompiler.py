#===================================================================================
# Chen Zheng COMP589-15D Project.
# Version 0.2
# Compiler v0.1 Definition of all tokens.
# Compiler v0.2 Initialization of symbol table for all tokens.
# Compiler v0.3 Lexical Analyser(the Scanner), set up print subroutine in the VM.
# Compiler v0.4 Lexical Analyser(the Scanner), expression processing.
#===================================================================================

import sys;

# from FileOperator import *; # Another way to import a py file.
 
#===================================================================================
### GLOBAL variables Deceleration. ###
compilerVersion = 0.4;

srcFileName = "../code/hello.txt";  # Path to the source code file.
outputFileName = "../code/hello.obj";  # path for the output machine code obj file.

src = [];  # The input file is stored as an array of string lines.
linenumber = 0;  # The current line number of source code.
charIndex = 0;  # The position of current character in the current line.
EOF = chr(0);  # The end of file character.

outputArray = [];  # Temporary array to hold all machine code/instructions.  
variableInitArray = []  # Temporary array to hold the code for initializing variables

varptr = 900  # Arbitrary base address of memory for variables, which starts from this address.
codeptr = 10  # Address to output next instruction (for machine code, 1-9 are reserved).
printStartAddress = 0;  # Address to start print subroutine.

token = None;  # A symbol, will be modified by each call of getToken().

# Reserved Token Symbols.
tokenNames = \
    [ "unknownToken", "codesym", "declare", "assignsym", "idsym", "varsym", "number",
     "leftbrace", "rightbrace", "leftbracket", "rightbracket",
     "equals", "plus", "minus", "multiply", "divide",
     "semicolon", "comma", "sharp",
     "print", "stringvalue", "endfile" ]
    # More symbol will be added.

# Define tokens as variables in the compiler.
unknownToken, codesym, declaresym, assignsym, idsym, varsym, number, \
leftbrace, rightbrace, leftbracket, rightbracket, \
equals, plus, minus, multiply, divide, \
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
        self.address = 0;

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
    addToSymTable('/', divide);
    
    addToSymTable(EOF, endfile);

def dumpSymbolTable():
    print("=== Symbol Table Contents ===");
    for name in symtable.keys():
        tempToken = symtable[name];
        if tempToken.token == idsym:  # Only print symbols from source code.
            printToken(tempToken);
   

# Open the source code file. 
def openSourceCode():
    global srcFileName;

    srcFile = open(srcFileName);
    src = srcFile.readlines();
    srcFile.close();
    
    return src;

# Save the output to an object file.        
def saveObjectCode():
    global outputFileName;
    global outputArray;
    
    f = open(outputFileName, "w")  # open connection to the output file.
    
    for s in outputArray:  # for each line in the output array append it to the file.
        f.write(s + "\n")
        
    f.close()  # close the connection to the output file.
            
# Printer function for given symbol.
def printToken(inputToken):
    if inputToken.token == idsym:  # For id symbols.
        print "Token = %10s, %-10s adr = %3d" % (tokenNames[inputToken.token], inputToken.name, inputToken.address);
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


# Display everything in the output array.
def DisplayObjectCode():
    print "*** Target VM Code Start ***"
    for line in outputArray:
        print line;
    print "*** Target VM Code End ***"
        



# Emit a line of object code to output array.
def emit(memoryAddress, operationCode, parameter):
    global codeptr;
    global outputArray;
    
    if (memoryAddress == 0):  # If no memory address given, this is a standard emit.
        memoryAddress = codeptr;  # Assign current code pointer for this line of instruction.
        codeptr = codeptr + 1;  # Increment code pointer by 1.
        
    instruction = "";  # Hold the instruction.
    if parameter != None:  # Instruction format if parameter provided.
        instruction = "%6d %-8s %-7d" % (memoryAddress, operationCode, parameter);
    else:  # Instruction format if none parameter provided.
        instruction = "%6d %-8s" % (memoryAddress, operationCode);
        
    outputArray.append(instruction);        

# Emit the object code for a string.
def emitString(string):
    global codeptr;
    
    codeptr = codeptr + 1;  # Reserved space for JUMP instruction to ignore string code lines.
    stringStart = codeptr;  # Remembering the begin of string memory address.
    
    for ch in string:  # For each character in the string, put into next memory location.
        emit(0, "constant", ord(ch));
        
    emit(0, "constant", 0);  # Put an 0 after the string memories as the end of it.
    emit(stringStart - 1, "jump", codeptr);  # Put jump instruction to jump over entire string.
     
    emit(0, "loadv", stringStart);  # Put the first character memory address into accumulator.
    emit(0, "store", 1);  # Put value in accumulator into register.

# Emit a line of comment to the object code. 
def emitComment(message):   
    global outputArray;
    comment = "## %s ##" % message;
    outputArray.append(comment);

# Initialization of all instructions.
def emitInit():
    global codeptr;
    global printStartAddress;
    
    emitComment("Start Of Object Code");
    codeptr = codeptr + 1;  # Researve blank memory address for jump to the actual instructions.
    
    emitComment("Reserved Print Subroutine");
    
    printStartAddress = codeptr;
    
    emit(0, "load-Ind", 0);
    emit(0, "jumpeq", printStartAddress + 5);
    emit(0, "writech", None);
    emit(0, "increment", 1);
    emit(0, "jump", printStartAddress);
    emit(0, "return", None);
    
#===================================================================================
# Variable declaration routines.
def variableInit(memadr, opcode, parameter):
    global variableInitArray
    variableInitArray.append([memadr, opcode, parameter])

def emitVraibleInit():
    global variableInitArray
    
    for line in variableInitArray:
        emit(line[0], line[1], line[2])


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
    while ch in ["\t", " ", "\n"]:  # Ignore tabs, spaces and new lines.
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
        
        token = symbol(ch, number, value=int(tempNumber));  # Set up the number token.
        
        return
    
    # Two character tokens.
    elif ch in [">", "<", "=", "!"]:
        ch2 = getCh();  # Get next character behind the '='.
    
        if ch2 == "=":
            token = lookup(ch + ch2);
        else:
            token = lookup(ch);
            ungetCh();
            
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
# Process variable declaration.
def variables():
    global varptr;
    
    getToken();  # Skip 'declare' keyword.
    
    while(token.token == idsym):  # If this token is an identifier.
        tempVar = token; 
        getToken();  # Skip this id token.
        
        # print token.name
        
        if token.token == assignsym:  # If there is a '=' after the identifier.
            getToken();  # Skip '=' token.
            
            if token.token == number:  # if the token is a number.
                variableInit(0, "loadv", token.value);
            else:  # If there is no number after '='.
                printError("Constant expected to assign a variable.");
                
            getToken();  # Skip number token.
            
        else:
            variableInit(0, "loadv", 0);
        
        if tempVar.address == 0:  # If var's address in empty means it's a new variable.
            symtable[tempVar.name].address = varptr;  # Assign memory address to this var.
            variableInit(0, "store", varptr);  # Store value in accumulator into memory address.
            varptr = varptr + 1;  # Increment the variable pointer by 1.
        else:
            printError("%c already declared before.");
        
        if token.token == semicolon:
            getToken();
            break;    
    
        if token.token == comma:
            getToken();
        else:
            printError("',' expected in variable declaration.");


#===================================================================================
# Process statements.
def stmtList():
    stmt();  # Process the first statement.
    
    while (token.token == semicolon):  # If there is a statement list, then process the next. 
        getToken();  # Skip semicolon.
        if token.token == rightbrace:  # End of statement list, break out while loop.
            break;
        
        stmt();  # Otherwise continue to process the statement(s).
    
# Single statement processing function.
def stmt():
    if token.token == printsym:
        printStmt();
    elif token.token == idsym:
        assignmentStmt();
    else: 
        printError("Start of a statement expected.");

# For each statement, there is a particular statement function.
def printStmt():
    emitComment("Start Print Statement");  # Comment to notify start of print statement.
    
    getToken();  # Skip the "print" key word.
    
    if token.token == leftbracket:  # "(" expected after "print".
        getToken();  # Skip "(".
    else: printError(" '(' expected after 'Print'");
    
    printItem();  # Process the current item after the bracket.
    
    while token.token == comma:
        getToken();
        printItem(); 
        
    if token.token == rightbracket:  # End of print statement.
        getToken();  # Skip ')'.
    else: printError("')' expected as the end of print. ");
    
        
# For each item inside the print brackets.
def printItem():
    global codeptr;
    global printStartAddress;
    
    if token.token == stringvalue:
        emitString(token.name);  # Put a string into memory.
        emit(0, "call", printStartAddress);
        getToken();  # Skip string token.
    else:
        # TODO : expressionStmt();
        sys.exit();
    
    emit(0, "loadv", 13);  # Put 13 to accumulator where 13 is a new line character.
    emit(0, "writech", 0);  # Display the value in accumulator as ascii to the console.


def assignmentStmt():
    emitComment("Start Assginment Statement");  # Comment to notify start of print statement
    which_ID = token             # Remember which ID on the left side of "="
    if lookup(which_ID.name) == None: # If this ID has not been declared, then error.
        printError("Udeclared variable detected.");
    
    getToken();  # Skip this ID token.
    
    if token.token == assignsym:
        getToken(); # Skip the '=' token.
    else:
        printError("'=' expected in an assignment statement.");
    
    expression();
    
    

#===================================================================================
# Process expression.
# Grammer of expression is expression = term operator term, term = factor operator factor.
def expression():
    term();  # Process the first term.
    
    while token.token in [plus, minus]:
        operator = token;  #
        getToken();  # Skip the '+' or '-' token.
        
        # Object code to calculate the left hand side result.
        
        term();  # Process the right hand side of the operator.
        # Object code to calculate the left hand side result, store the result.
        
        # # Object code to calculate the final result of both sides of the operator.
        if operator == plus:
            return None;
        elif operator == minus:
            return None;

# Process a term    
def term():
    factor();  # Process the left hand side of the operator.
    
    while token.token in [multiply, divide]:
        operator = token;  # Remember the operator.
        
        # Object code to calculate the left hand side result.
        
        getToken();  # Skip '*' or '/' token.
        factor();  # Process the right hand side of the operator, return the result.
        # Object code to calculate the left hand side result, store the result.
        
        # # Object code to calculate the final result of both sides of the operator.
        if operator == multiply:
            return None;
        elif operator == divide:
            return None;
        
# Process a factor
def factor():
    if token.token == idsym:  # If the factor is an ID token.
        idtoken = token;
        emit(0, "load", idtoken.address);  # Load the value in the ID address into ACC.
        getToken();  # Skip this number token.       
    
    elif token.token == number:  # If the factor is an number token.
        emit(0, "loadv", token.value);  # Load the value of this number into ACC.
        getToken();  # Skip this number token.    
    
    elif token.token == leftbracket:  # If this expression starts with an '('. 
        getToken();  # Skip the '('.
        expression();  # Call expression again.
        
        if token.token == rightbracket:  # ')' is expected on the right hand side.
            getToken();  # Skip the ')'.
        else: 
            printError("')' expected as the end of parenthesized expression.");
    
    else:
        printError("Start of factor error detected.");


#===================================================================================
# Main code processing function
def code():
    
    emitInit();  # Emit print subroutine into output array.
   
    emit(10, "jump", codeptr)  # Jump over the initial code and function definitions
    
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
     
    if token.token == declaresym:  # Process local variables are declaration. 
        variables();
    emitComment("Start Declaration")
    emitVraibleInit()  # Initialize all variables by creating blank memory spaces for them
    
    if token.token == leftbrace:  # "{" is the start of code statements.
        getToken();
    else: printError(" '{' missing...");
    
    stmtList();
    
    emit(0, "halt", None)  # emit halt to stop execution
    
#===================================================================================


#===================================================================================
# Main Function of the compiler, loads the source code file and output a object file.
def main():
    print("Compiler Version: "), compilerVersion;
    
    global srcFileName;
    global src;
    global outputFileName;
    global outputArray;
    
    src = openSourceCode();  # @UndefinedVariable
    
    initSymbolTable();
    
    code();  # Process the input source code.
    
    DisplayObjectCode();  # Display the machine code to a console.
    
    dumpSymbolTable();
    
    saveObjectCode();  # Save the machine code to a object file.
    
    sys.exit();



#===================================================================================
###### Compiler Main Call #####
main();
