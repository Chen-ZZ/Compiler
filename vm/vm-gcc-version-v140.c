//===========================================================================
// Processor Simulator - in "C"
// This program is a software equivalent of our CPU
// The code here is rather inelegant in places but does work.
// VM1 - Copyright 2000 - 2003 Giovanni Moretti G.Moretti@massey.ac.nz

/* Updates by Callum Lowcay (May 5, 2010):
  - new functions set_ioattrs and restore_ioattrs to set the terminal to
    non-canonical mode.
  - replaced non-standard getch and getche with getchar (with terminal in
    non-canonical mode they work the same)
  - replaced non-standard putch with standard putchar
  - Added line to detect incoming UNIX EOL and replace it with DOS EOL to
    maintain compatibility with TEST.OBJ
*/

char * version = "v1.4 - 2010";
//===========================================================================
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
//#include <conio.h>
#include <ctype.h>
#include <termios.h>

// EOL is the character returned by getche() for the <Enter> key
#define EOL_DOS  13
#define EOL_UNIX 10

#define acc M[0]
#define MEMORY_SIZE 4096
//===========================================================================

#define opLoad            0
#define opStore           1
#define opClear           2
#define opAdd             3
#define opIncrement       4
#define opSubtract        5
#define opDecrement       6
#define opCompare         7
#define opJump            8
#define opJumpGT          9
#define opJumpEQ         10
#define opJumpLT         11
#define opJumpNE         12
#define opReadInt        13
#define opWriteInt       14
#define opHalt           15
#define opLoadX          16
#define opStoreX         17
#define opLoadInd        18
#define opStoreInd       19
#define opReadch         20
#define opWritech        21
#define opCall           22
#define opReturn         23
#define opPush           24
#define opPop            25
#define opJumpI          26
#define opJumpGTI        27
#define opJumpEQI        28
#define opJumpLTI        29
#define opJumpNEI        30
#define opLoadV          31
#define opMpy            32
#define opDiv            33
#define opMod            34
#define opNot            35
#define opAnd            36
#define opOr             37
#define opCallI          38

// The size of the Opcodes Array
#define MaxOpcodes       39
//===========================================================================
    
int pc, M[MEMORY_SIZE], LT, EQ, GT; // Registers for Virtual Machine
int InstOverwrite[MEMORY_SIZE];     // So we can trap Overwrite of Instructions
int breakpoint;                     // Stop VM when this address reached
int trace;                          // Boolean, Display registers?
int mem_adr;                        // address for Change  Memory Command
int display_mem_adr;                // address for Display Memory Command
int interactive_mode = 1;           // Some output disabled when not Int'
int File_Load_Errors = 0;           // Used by LoadCode to remember errors
int AbortExecution;                  // Used to stop if invalid opcode ...

char opcodes[MaxOpcodes][20];       // The Opcode Strings
int  NumOpcodes = 0;                // Index of the next free slot in Opcodes
//===========================================================================

int  LoadCodefile (char *filename);
void OpcodeError(int lineno, char *line, char *msg, char * opcode, int loadadr);
void Initialise_VM_Registers();
void set_condition_codes(int value);
int  execute (int execution_count);

//===========================================================================
// Copy an Opcode String into the OpCodes Array at the correct place
//   This enables us to lookup opcodes by their value and get the string for
//   Disassembly - useful when displaying the next instruction;

void setup_opcode(char *opcode_string, int opcode) {

	strcpy(opcodes[opcode], opcode_string);

}
//==========================================================================
// Loadup Opcode and Opcode String Table - this keeps everything centralised
// and enables us to disassemble.

void Setup_Opcode_Strings() {
int i;
    for (i=0; i<MaxOpcodes; i++) strcpy(opcodes[i], "");  // Reset all opcodes to Null String
    setup_opcode("load"     , opLoad      );
    setup_opcode("store"    , opStore     );
    setup_opcode("clear"    , opClear     );
    setup_opcode("add"      , opAdd       );
    setup_opcode("increment", opIncrement );
    setup_opcode("subtract" , opSubtract  );
    setup_opcode("decrement", opDecrement );
    setup_opcode("compare"  , opCompare   );
    setup_opcode("jump"     , opJump      );
    setup_opcode("jumpgt"   , opJumpGT    );
    setup_opcode("jumpeq"   , opJumpEQ    );
    setup_opcode("jumplt"   , opJumpLT    );
    setup_opcode("jumpne"   , opJumpNE    );
    setup_opcode("readint"  , opReadInt   );
    setup_opcode("writeint" , opWriteInt  );
    setup_opcode("halt"     , opHalt      );
    setup_opcode("load-x"   , opLoadX     );
    setup_opcode("store-x"  , opStoreX    );
    setup_opcode("load-ind" , opLoadInd   );
    setup_opcode("store-ind", opStoreInd  );
    setup_opcode("readch"   , opReadch    );
    setup_opcode("writech"  , opWritech   );
    setup_opcode("call"     , opCall      );
    setup_opcode("return"   , opReturn    );
    setup_opcode("push"     , opPush      );
    setup_opcode("pop"      , opPop       );
    setup_opcode("jumpi"    , opJumpI     );
    setup_opcode("jumpgti"  , opJumpGTI   );
    setup_opcode("jumpeqi"  , opJumpEQI   );
    setup_opcode("jumplti"  , opJumpLTI   );
    setup_opcode("jumpnei"  , opJumpNEI   );
    setup_opcode("loadv"    , opLoadV     );
    setup_opcode("mpy"      , opMpy       );
    setup_opcode("div"      , opDiv       );
    setup_opcode("mod"      , opMod       );
    setup_opcode("not"      , opNot       );
    setup_opcode("and"      , opAnd       );
    setup_opcode("or"       , opOr        );
    setup_opcode("calli"    , opCallI     );
}    
//===========================================================================
// FIND_OPCODE
//   Given an opcode string, return its numeric (true opcode) value

int find_opcode(char * opcode_string) {
int i = 0;
  while (i < MaxOpcodes) 
    if (strcmp(opcodes[i], opcode_string) == 0) return(i);
    else i++;
  return -1;
}
//===========================================================================

void Display_Menu() {

    printf("\n    *** VM Simulator %s ***\n\n", version);
    printf("   G      Run until HALT or 10000 instructions\n");
    printf("   space  Single Step\n");
    printf("   T      Trace display toggle\n");
    printf("   B      Breakpoint set/clear (simulator stops)\n");

    printf("   D      Dump Memory contents to screen\n");
    printf("   R      Register Display\n");
    printf("   A      Set Accumulator\n");
    printf("   P      Set PC\n");
    printf("   M      Memory set\n");

    printf("   I      Initialise Simulator\n");
    printf("   L      Load Object File\n");
    printf("   Q      Quit\n\n");
}

//===========================================================================
// GET_COMMAND
// print a prompt and return a lower-cased single letter

char get_command () {
  char ch;
   printf("cmd> "); fflush(stdout);
   ch = getchar(); printf("\n");
   ch = tolower(ch);
   return ch;
}
//===========================================================================
// Get a number that already has a value. 
// Return either the new number or the old

int Get_one_num(int current_value) {
  int tmp;
  char reply[80];
  fflush(stdin);
  fgets(reply, 79, stdin);
  
  if (strlen(reply) == 1) /* just EOL */ 
     return(current_value);
  if (sscanf(reply, "%d%*c", &tmp)== 1) // Got a new value
    return tmp;
  else return current_value;            // return old value
}
//===========================================================================

void set (char * msg, int *adr) {
  printf("%s (%d) : ",msg, *adr);
  *adr = Get_one_num(*adr);
}

//===========================================================================
// Breakpoints are a way of letting the Simulator run at full speed until
// a certain (user-defined) point is reached in the Program.

void breakpoint_cmd () {
  printf("Breakpoint address (%d) - 0 to disable : ", breakpoint);
  breakpoint = Get_one_num(breakpoint);
}

//===========================================================================
void Clear_Memory() {
 int i;
  for (i=0; i<MEMORY_SIZE; i++){
	 M[i] = (MaxOpcodes+1)*2048;                 // Fill memory with HALT opcode
	 InstOverwrite[i] = 0;
  }
}

//===========================================================================
void Display_memory (int start_address) {
  int i, address;
  int ch;
  start_address = (start_address / 10) * 10;
  address = start_address;
  printf("      ");
  for (i=0; i<10; i++) printf("%5d ",i);
  for (i=0; i<10; i++) printf("%1d",i); printf("\n");
  do {
    printf("%4d: ",address);
    for (i=0; i<10; i++) printf("%5d ",M[address+i]);
    for (i=0; i<10; i++) {
      ch = M[address+i];
      if ((ch < 32) || (ch > 127)) ch = '.';
      printf("%c", ch);
    }
    printf("\n");
    address += 10;
  } while (address < start_address+50);
  printf("\n");
}

//===========================================================================

void Display_registers() {
  unsigned int opcode, adr, mdr;
  mdr = M[pc];
  adr      = mdr % 2048;     // Leave bottom 11 bits
  opcode   = mdr >> 11;     // Move opcode down
  if (interactive_mode) printf("\n");
  
  if (opcode < MaxOpcodes) 
    printf("PC= %04d %-9s %-5d",pc, opcodes[opcode],adr);
  else
    printf("PC= %04d Invalid(%d) %-5d",pc, opcode, adr);
    
  printf("   (ACC=%-5d, X=%04d, SP=%04d, BRK: %04d)\n", acc, M[1], M[2], breakpoint);
}

//===========================================================================
// Reset the Virtual Machine Registers to their Reset Value

void Initialise_VM_Registers() {
  pc    = 10;      // Always get 1st instruction from M[0]
  acc   = 0;       // Acc = 0
  M[1]  = 0;       // X  = 0
  M[2]  = 2000;    // SP = 2000
}

//===========================================================================

int LoadFile (char * fname) {
  char  filename[300];
  int   loaded_ok = 0;

  strcpy(filename, fname);

  if (strlen(filename) == 0) {  // If we have a filename, use it
    printf("Filename : "); 	 // otherwise ask
    gets(filename);
  }
  
  if (strlen(filename) > 1) {          // If name provided, try to load file
	   loaded_ok = LoadCodefile(filename); // Return value of attempted load to memory
      Initialise_VM_Registers();       // Reset PC, ACC, X & SP
  }
 return(loaded_ok); 
}

//===========================================================================
// functions to set and restore terminal mode
struct termios oldioattrs;
void restore_ioattrs() {
  tcsetattr(0, TCSANOW, &oldioattrs);
}
void set_ioattrs() {
  struct termios ioattrs;
  
  if(tcgetattr(0, &ioattrs) == 0) {
    memcpy(&oldioattrs, &ioattrs, sizeof(struct termios));
    // turn off cannonical mode, disables line editing though
    ioattrs.c_lflag &= ~(ICANON);
    tcsetattr(0, TCSANOW, &ioattrs);
  } else {
    printf("Could not set raw mode");
  }
  atexit(&restore_ioattrs);
}

//===========================================================================
int main(int argc, char *argv[]) {
  int op;
  char ch;
  
  Setup_Opcode_Strings();		// Load up Table of Opcodes 
  Initialise_VM_Registers();  // Define all Register Values
  trace      = 0;       // Tracing OFF
  breakpoint = 0;       // No breakpoint set
  
  // setup termios
	set_ioattrs();

  //---------------------------------------------------------------------
  // See if we're running NON-INTERACTIVELY (Load, Run & Quit)
  
  if (argc == 2) {				// Object Filename Supplied on command line
    interactive_mode = 0;			// Just run program (no menu displayed)
    if (LoadFile(argv[1])) 
      execute(50000); 				// Execute 10000 instructions and
      return 0;						// exit
  }

  //---------------------------------------------------------------------

  interactive_mode = 1;
  Clear_Memory();
  Display_Menu();
  printf("Press ? or h to get this menu\n");
  do {
    ch = get_command();
    if ((ch == '?') || (ch == 'h')) {Display_Menu(); continue; }
    switch (ch) {
      case 'g'  : op = execute(10000);                          break;
      case ' '  : op = execute(1);
                  if (!trace) Display_registers();              break;
      case 'd'  : printf("Memory address : ");
                  display_mem_adr = Get_one_num(display_mem_adr);
                  Display_memory(display_mem_adr);              break;
  
      case 'r'  : Display_registers();                          break;
  
      case 'a'  : set("Accumulator",    &M[0]);
                  set_condition_codes(0);                       break;
  
      case 'p'  : set("Program Counter",&pc);                   break;
  
      case 'm'  : printf("Change Memory Location : ");
                  mem_adr = Get_one_num(mem_adr);
                  set("New Value", &M[mem_adr]);                break;
  
      case 't'  : trace = !trace;
                  printf("Tracing is %s\n", trace?"ON":"OFF");  break;
  
      case 'i'  : Initialise_VM_Registers();                    break;
      case 'b'  : breakpoint_cmd();                             break;
      case 'l'  : LoadFile("");                                 break;
      case 'q'  : exit(0);
      default   : printf("\a");
    }
  } while (1);
  return 0;
}

//===========================================================================
// Set the Condition Codes based on a comparision with the supplied Value
//
// This is used in two ways:
//  1) by the COMPARE instruction - the value is it's argument eg compare 15
//     which compares the accumulator with 15
//
//  2) Whenever the accumulator is changed by any instruction
//     This lets you do a decrement of the accumulator and then do a JumpEQ
//     without having to do a COMPARE against zero first.

void set_condition_codes(int value) {
  LT = (acc <  value);
  EQ = (acc == value);
  GT = (acc >  value);
}

//===========================================================================
// SET the specified memory location to the defined value
// ONLY IF it's doesn't contain an instruction
//  ==> Detect attempts to overwrite instructions

void setmem(int adr, int value) {
  if (adr < 0 || adr >= MEMORY_SIZE){
	  printf("Instruction at %d tried to store %d in M[%d]\n", pc-1, value, adr);
	  AbortExecution = 1;
	  return; 
  };
  if (!InstOverwrite[adr]) 
    M[adr] = value;
  else {
	 printf("Attempted overwrite of opcode at M[%d] with %5d by instr at %5d: Stopped!\n", adr, value, pc-1);
	 AbortExecution = 1;
  }
}
//===========================================================================
// GET the specified memory location to the defined value
// ONLY IF it's doesn't contain an instruction
//  ==> Detect attempts to fetch instructions - usually erroneous

int getmem(int adr) {
  if (adr < 0 || adr >= MEMORY_SIZE){
	  printf("Instruction at %d tried to fetch M[%d]\n", pc-1, adr);
	  AbortExecution = 1;
	  return(0); 
  };
  return(M[adr]);
}
//===========================================================================

int execute (int execution_count) {
  int op, adr, mdr, tmp;
  AbortExecution = 0;
  do {
	mdr = getmem(pc);           // Fetch instruction
	adr  = mdr % 2048;     // Leave bottom 11 bits
	op   = mdr / 2048;     // Move opcode down
        if (trace) Display_registers();
        pc++;

  	switch (op) {
	   case opLoad      :  acc = getmem(adr);  set_condition_codes(0);    break; // load
      case opStore     :  setmem(adr, acc);
                     if (adr == 0)
                       set_condition_codes(0);          break; 	// store
	   case opClear     :  acc = 0;            set_condition_codes(0);    break;  // clear
      case opAdd       :  acc += getmem(adr); set_condition_codes(0);    break; // add
      case opIncrement :  setmem(adr, getmem(adr)+1);                    break; // incr
      case opSubtract  :  acc -= getmem(adr); set_condition_codes(0);    break; // Subtract
      case opDecrement :  setmem(adr, getmem(adr)-1);                                 break; // Decr

	   case opCompare   :  set_condition_codes(getmem(adr));              break;  // Compare

	   case opJump      :  pc = adr;                                 break;  // jump
	   case opJumpGT    :  if (GT) pc = adr;                         break;  //jumpGT
	   case opJumpEQ    :  if (EQ) pc = adr;                         break;  //jumpEQ
	   case opJumpLT    :  if (LT) pc = adr;                         break;  //jumpLT
	   case opJumpNE    :  if (!EQ) pc = adr;                        break;  //jumpNE

	   case opReadInt   :  printf("? ");
	                       scanf("%d%*c",&tmp);
	                       setmem(adr, tmp);		                    break;  //ReadInt
	   case opWriteInt  :  printf("%d ",getmem(adr));
                     fflush(stdout);                      break;  //WriteInt

	   case opHalt:     ; // Halt - handled at end

	   case opLoadX     :  M[1]   = getmem(adr);                          break;  //LoadX
	   case opStoreX    :  setmem(adr, M[1]);
	                       if (adr==0) /* ACC */
	               set_condition_codes(0);
                                                          break;  //StoreX
	   case opLoadInd   :  acc = getmem(adr+M[1]);
	             set_condition_codes(0);              break;  //LoadInd
	   case opStoreInd  :  setmem(adr+M[1], acc);                    break;  //StoreInd
	   case opReadch    :  acc=getchar();
	                       // Convert UNIX newline to DOS newline so as not to break
	                       // test.obj (which expects a DOS newline)
	                       if(acc == EOL_UNIX) acc = EOL_DOS;
                          if ((acc == EOL_DOS) || (acc == EOL_UNIX)) printf("\n");
                   set_condition_codes(0);
                   if (acc == 27) return op; //ESC - stop executing
                                                        break;  //ReadCh
	   case opWritech   :  if ((acc=='\n')||(acc==EOL_DOS)||(acc==EOL_DOS))
	                            printf("\n");
	             else putchar(acc);                 break;  //WriteCh

	   case opCall      :  setmem(++M[2], pc);  // Preincrement Stack
                     pc       = adr;                  break;  //Call

	   case opReturn    :  pc = getmem(getmem(2)); M[2]--;                break;  //Return
	
	   case opPush      :  M[2]++; setmem(getmem(2), getmem(adr));        break;  //Push (PreIncrement Stack)
	   
	   case opPop       :  setmem(adr, getmem(getmem(2))); M[2]--;
	                       if (adr == 0) set_condition_codes(0);          break;  //Pop (PostDecrement)
	   
      case opJumpI     :  pc = getmem(adr);                              break;  //JumpI
	   case opJumpGTI   :  if (GT) pc = getmem(adr);                      break;  //JumpGTI
	   case opJumpEQI   :  if (EQ) pc = getmem(adr);                      break;  //JumpEQI
	   case opJumpLTI   :  if (LT) pc = getmem(adr);                      break;  //JumpLTI
	   case opJumpNEI   :  if (!EQ) pc = getmem(adr);                     break;  //JumpNEI

	   case opLoadV     :  if (adr>1023) { //Top bit set, treat as negative
                       tmp = -1;
                       adr = (tmp &(~2047)) | (adr & 2047);
                     }
	                       acc = adr;  set_condition_codes(0);                 break; //LoadV

	   case opMpy       :  acc = acc * getmem(adr);  set_condition_codes(0);   break; // MPY
	   case opDiv       :  acc = acc / getmem(adr);  set_condition_codes(0);   break; // DIV
	   case opMod       :  acc = acc % getmem(adr);  set_condition_codes(0);   break; // MOD
	   case opNot       :  acc = ~ acc;              set_condition_codes(0);   break; // NOT
	   case opAnd       :  acc = acc & getmem(adr);  set_condition_codes(0);   break; // AND
	   case opOr        :  acc = acc | getmem(adr);  set_condition_codes(0);   break; // OR

	   case opCallI     :  M[2]++; setmem(getmem(2), pc);                     // Stack Return Address
	                       pc = getmem(adr);                          break;  // then CallI Indirect
      }

      execution_count--;
  } while ( (op!=opHalt) && (op<MaxOpcodes) && (execution_count>0) && (pc!=breakpoint) && !AbortExecution);
  if (op >= MaxOpcodes) printf("Invalid instruction encountered at PC=%d\n", pc-1);
  if (pc == breakpoint)  Display_registers();
  
  if (interactive_mode && (op == opHalt)) printf("\nProgram Terminated normally\n\n");
  return op;	// return last opcode executed
}

//===========================================================================
// Convert the supplied string to Lower Case

void lowcase (char s[]) {
  int i;
  for (i=0; i< strlen(s); i++)
     s[i] = tolower(s[i]);
}

//===========================================================================
// LoadCodefile from the specified object file into memory
//
// File format is address, opcode [argument]
// Lines with a # in Column 1 and blank lines are ignored

int LoadCodefile (char *filename) {
  char opcode_string[80], argstring[80];
  int loadadr, adr, opcode, things_on_line, lineno=0, is_negative;
  FILE *codefile;
  char line[120];

  codefile = fopen(filename, "r");
  if (codefile == NULL) {
     printf("Can't open %s\n", filename);
     return 0;
  }

  // printf("\nLoading Object file %s\n", filename);
  File_Load_Errors = 0;
  lineno = 0;
  Clear_Memory();
  while (fgets(line,119, codefile) != NULL) {
    lineno++;
    // printf("%s",line);
    //------------------------------------------------------------------------------------
    if (strlen(line) == 1) continue; // Ignore blank lines (just '\n')
    if ((strlen(line) > 1) && line[0] == '#') continue; // Ignore comment lines
    //------------------------------------------------------------------------------------
    if ((things_on_line = sscanf(line, "%d %s %s", &loadadr, opcode_string, argstring)) == 0) {
	    OpcodeError(lineno, line, "Line must start with an address", opcode_string, loadadr); 
	    continue;						// Skip this line
    }
    //------------------------------------------------------------------------------------
    if ( things_on_line == 1) {   // Just an address, no opcode
	    OpcodeError(lineno, line, "Opcode expected", opcode_string, loadadr); 
	    continue;						// Skip this line
    }

    //------------------------------------------------------------------------------------
    lowcase(opcode_string);             // Force opcode_string to Lowercase so case-insensitive
    is_negative = 0; // no minus sign in front of argument to LoadV
    adr         = 0; // Just in case this opcode doesn't define it

    //------------------------------------------------------------------------------------
    // If it's an opcode that needs an address, make sure there is one!
    if (! (  (strcmp(opcode_string, "clear"  )  == 0) || (strcmp(opcode_string, "halt"   )  == 0) ||
	          (strcmp(opcode_string, "readch" )  == 0) || (strcmp(opcode_string, "writech")  == 0) ||
	          (strcmp(opcode_string, "return" )  == 0) || (strcmp(opcode_string, "not"    )  == 0)
          ))
        if (things_on_line == 3) { // convert third argument to a number, allow for -
            if ((strlen(argstring) > 2) && (argstring[0]=='-')) {
              is_negative = 1;
              strcpy(argstring, &argstring[1]); // delete '-'
            }
            // Is the argument a single quoted character (eg 'A')
            if ((strlen(argstring)==3) && (argstring[0]=='\'')&&(argstring[2]=='\'')) {
	            
              adr = argstring[1]; 	// If so, return the letter as the value- odd but allowed ;-)
            }
            else //Try converting to a decimal integer 
              if (sscanf(argstring, "%d", &adr) != 1)
                OpcodeError(lineno, line,"Number expected for argument", opcode_string, loadadr);

            //If the argument had been preceded by a '-', negate the result
            if (is_negative) adr = -adr;

          }
          else {
	         // printf("things_on_line = %d\n", things_on_line);
	         OpcodeError(lineno, line,"Argument expected for", opcode_string, loadadr);
          }

    //------------------------------------------------------------------------------------
    if (strcmp(opcode_string, "constant" ) == 0)  
       M[loadadr]=adr;                               // Constant value to memory location
    else {
       opcode = find_opcode(opcode_string);

       if (opcode == -1)  OpcodeError(lineno, line, "Unknown Opcode", opcode_string, loadadr);
       else {
	      // Got a Valid opcode, move it to the top of the instruction and merge in the address 
         M[loadadr] = (opcode << 11) +(adr & 2047);
    //  printf("load address = %d	 ", loadadr);
         //  printf("Opcode       =>%s< - %d\n", opcode_string, op);
    //  printf("Arg Address  = %d\n\n", adr);
         //  printf("MemAdr:  %4d   %9s    %d\n", loadadr, opcode_string, adr);
         InstOverwrite[loadadr] = 1;	// Set a flag so we know this location contains an opcode
       }
    }
  } // while

  if (interactive_mode)
    if (File_Load_Errors ==0) printf("Object File Loaded Successfully\n");
    else                       printf("Object File had Errors\n");
  return !File_Load_Errors;
}

//===========================================================================

void OpcodeError(int lineno, char *line, char *msg, char * opcode_string, int loadadr) {
   printf("\nLine %4d: %s\n*** %s -%s- at %d\n", lineno, line, msg,opcode_string, loadadr);
   File_Load_Errors = 1;
}
//====================================================================================
/* CVS History

$Log: VM.C,v $
Revision 1.31  2004/02/18 02:03:44  gmoretti
Cosmetic changes to source code and fixed wierd EOL character in "vmtest.obj"

Revision 1.30  2003/06/05 03:54:38  gmoretti
Upgrade with Memory Instruction Overwrite Check (actually last commit), and fetch/store outside valid simulator memory addresses (currently 0-4095).

Revision 1.29  2003/06/05 02:34:07  gmoretti
*** empty log message ***

Revision 1.28  2002/09/17 00:54:23  gmoretti
Added an Invalid Opcode Check and Message - preload memory with a Bad Opcode so an errant program halts with an INVALID OPCODE message.

Revision 1.27  2002/09/17 00:06:14  gmoretti
Added EOL_DOS (value 13) and EOL_UNIX (value 10) so either will work as end-of-line characters in both READCH and WRITECH opcodes.

Revision 1.26  2002/09/16 23:47:22  gmoretti
Fixed minor error relating to status when loading a file in NON-interative mode - it
worked but gave an error.
Altered Get_One_Num so that just pressing <enter> will leave the old value intact.

Revision 1.25  2002/09/16 05:20:31  gmoretti
Lots of reorganising - now have interchange between opcode values and strings so we have a disassembler when single stepping - at last!

Revision 1.24  2002/09/16 01:40:34  gmoretti
Found a bug relating to running programs in NON-Interactive mode - the SP was set
but then reset to the NOP value by the LoadCodefile routine which (for safety) fills all
of memory with the HALT opcode. Now works properly in both interactive & Loadn'go modes.

Revision 1.23  2002/09/16 01:05:13  gmoretti
lots of tidying up. Moved initialisation in LoadFile, so that codefile can preset the registers (which are located in memory). This would be an odd thing to do but should be allowed.

*/

