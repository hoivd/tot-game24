# prompts.py

PROPOSE_PROMPT = '''Generate all valid one-step Game of 24 moves.
The output must be exhaustive.
Do not omit valid operations.

Rules:
- Pick two numbers.
- Use + - * /
- Include both orders for - and /
- No divide by zero
- Remove duplicates
- One line only per move

Format:
a op b = c (left: remaining numbers)


For Example:
Input: 4 7 8 8
Possible next steps:
4 + 7 = 11 (left: 8 8 11)
8 - 4 = 4 (left: 4 7 8)
8 / 4 = 2 (left: 2 7 8)
7 * 8 = 56 (left: 4 8 56)

Input: 4 7 8
Possible next steps:
4 + 7 = 11 (left: 8 11)
7 - 4 = 3 (left: 3 8)
8 / 4 = 2 (left: 2 7)
7 * 8 = 56 (left: 4 56)

Input: 3 8
Possible next steps:
3 + 8 = 11 (left: 11)
8 - 3 = 5 (left: 5)
8 / 3 = 2.666667 (left: 2.666667)
3 * 8 = 24 (left: 24)

Input: {input}

Possible next steps: 
'''
# Explain: "explain the reasoning"

VALUE_PROMPT = '''Evaluate if given numbers can reach 24 (sure/likely/impossible)
10 14
10 + 14 = 24
sure
11 12
11 + 12 = 23
12 - 11 = 1
11 * 12 = 132
11 / 12 = 0.91
impossible
4 4 10
4 + 4 + 10 = 8 + 10 = 18
4 * 10 - 4 = 40 - 4 = 36
(10 - 4) * 4 = 6 * 4 = 24
sure
4 9 11
9 + 11 + 4 = 20 + 4 = 24
sure
5 7 8
5 + 7 + 8 = 12 + 8 = 20
(8 - 5) * 7 = 3 * 7 = 21
I cannot obtain 24 now, but numbers are within a reasonable range
likely
5 6 6
5 + 6 + 6 = 17
(6 - 5) * 6 = 1 * 6 = 6
I cannot obtain 24 now, but numbers are within a reasonable range
likely
10 10 11
10 + 10 + 11 = 31
(11 - 10) * 10 = 10
10 10 10 are all too big
impossible
1 3 3
1 * 3 * 3 = 9
(1 + 3) * 3 = 12
1 3 3 are all too small
impossible
INPUT:
{input}

Result:

Response: "finally answer (sure/likely/impossible)"
'''

# Explain: "explain the reasoning"