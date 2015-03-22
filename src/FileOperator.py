# Open the source code file. 
def openSourceCode(srcFileName):

    srcFile = open(srcFileName);
    src = srcFile.readlines();
    srcFile.close();
    
    return src;

# Save the output to an object file.        
def saveObjectCode(outputFileName, outputArray):

    
    f = open(outputFileName, "w")   # open connection to the output file.
    
    for s in outputArray:           # for each line in the output array append it to the file.
        f.write(s + "\n")
        
    f.close()                       # close the connection to the output file.