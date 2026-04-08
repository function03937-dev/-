# How to Run This Code
## Project Overview
This code implements Radix Sort for 1D arrays and supports sorting a 2D matrix by a specified column. It also includes examples for number sorting, document ID sorting, student grade matrix analysis, and Tic-Tac-Toe board diagonal check.

## Requirements
- Python 3.x
- NumPy (only for the student grades example)

Install NumPy if you haven’t:
pip install numpy

## How to Run
1. Save the code as T2 code.py
2. Open terminal or command prompt
3. Go to the folder where the file is located
4. Run:
python "T2 code.py"
If you have both Python 2 and 3, use:
python3 "T2 code.py"

You can also run it directly in IDEs like PyCharm or VS Code.

## What the Output Shows
- Original matrix and matrix sorted by column 0 using Radix Sort
- Sorted document ID list
- Sorted integer list
- Average score per student and highest score per subject
- Whether player X wins on the diagonal in Tic-Tac-Toe

## Custom Usage
- To sort your own 1D list: call radix_sort(your_list)
- To sort your own matrix by column: call sort_matrix_by_column(your_matrix, column_index)
- Modify the example matrices and lists to test your own data

## Notes
- Radix Sort only works for non-negative integers
- Column index must be valid (start from 0)
- The student grades example requires NumPy