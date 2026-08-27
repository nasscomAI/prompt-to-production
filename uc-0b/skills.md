name: C_Code_Debugger

description: Analyzes C source code to identify syntax errors, logical bugs, and memory leaks while providing optimized corrections.

input: A raw string containing C source code or a .c file path.

output: A structured JSON object containing a list of identified errors, line numbers, and the corrected code snippet.

error_handling: If the input is not valid C code or is empty, the system returns a "Syntax Error: Undefined Input" message and requests a valid code block.

name: Physics_Formula_Solver

description: Calculates experimental values for physics topics like the Hall effect, lasers, and the photoelectric effect using standard physical constants.

input: A dictionary of known variables (e.g., current, magnetic field, wavelength) and the target variable to solve for.

output: A numerical value with appropriate SI units and a brief explanation of the derivation.

error_handling: If required variables are missing or values are physically impossible (e.g., negative Kelvin), it returns an "Incomplete Data" error and lists the missing parameters.
