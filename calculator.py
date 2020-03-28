import string
import collections


def parse_command(line):
    """ Execute /help and /exit commands, throw Unknown command error otherwise. """

    if line == "/exit":
        print("Bye!")
    elif line == "/help":
        print("This calculator evaluates expressions with addition, subtraction,")
        print("multiplication, division, power, unary operators and parenthesis.")
        print("It can also assign and use variables. Variable names can contain only")
        print("Latin letters. Type \"/exit\" to quit.")
    else:
        print("Unknown command")


def parse_assignment(line):
    """ Assign value of expression on the right to variable on the left.

    Split assignment into two parts, evaluate right part and assign to variable in left part.
    If no variable in left part, throw Invalid expression error.
    If invalid variable in left part, throw Invalid identifier error.
    If no expression or invalid expression in right part, throw Invalid assignment error.
    If unknown variable in right part, throw Unknown variable error.
    """

    line = line.split("=", 1)
    if not line[0]:
        print("Invalid expression")
    elif not line[0].isalpha():
        print("Invalid identifier")
    else:
        if not line[1]:
            print("Invalid assignment")
        elif line[1].isalpha() and line[1] not in variables:
            print("Unknown variable")
        else:
            result = parse_expression(line[1])
            if result in ("Invalid expression", "Unknown variable"):
                print("Invalid assignment")
            else:
                variables[line[0]] = result


def parse_expression(infix):
    """ Turn infix notation into reverse Polish notation, then evaluate.

    If infix notation results in error, throw Invalid expression error.
    """

    rpn_list = infix_to_rpn(infix)
    if rpn_list == "Error":
        return "Invalid expression"
    result = rpn_to_result(rpn_list)
    return result


def infix_to_rpn(infix):
    """ Turn expression in infix notation into reverse Polish notation.

    Each cycle, first check for single unary operator, then for integers and variables,
    then for operators and parentheses. Append integers and variables to result list.
    Push operators and parentheses onto stack and pop to result list according to precedence.

    If unary operator is last or is not followed by integer or variable, throw error.
    If anything besides digits, Latin letters or operators/parenthesis is used, throw error.
    If several multiplication, division or power signs are used in a row, throw error.
    If closing parenthesis encountered while stack is empty, throw error.
    If opening parenthesis remaining in stack, throw error.
    """

    result = []
    stack = collections.deque()
    i = 0

    while i < len(infix):

        # Check for unary + or - at the beginning, after operators or opening parenthesis
        # Make sure that integer or variable follows unary operator
        if infix[i] in "+-" and (i == 0 or infix[i - 1] in "^*/+-("):
            if i == len(infix) - 1 or (infix[i + 1] not in string.digits
                                       and infix[i + 1] not in string.ascii_letters
                                       and infix[i + 1] != "("):
                return "Error"
            if infix[i] == "-":
                stack.append("#")
            i += 1

        # Check for integer or variable
        if i < len(infix) and (infix[i] in string.digits or infix[i] in string.ascii_letters):

            # Find end of integer and append it to result, reset sign to positive
            if infix[i] in string.digits:
                integer = 0
                while i < len(infix) and infix[i] in string.digits:
                    integer = integer * 10 + int(infix[i])
                    i += 1
                result.append(integer)

            # Find end of variable name and append it to result
            else:
                var_name = ""
                while i < len(infix) and infix[i] in string.ascii_letters:
                    var_name += infix[i]
                    i += 1
                result.append(var_name)

        # Check for unacceptable symbols
        elif i < len(infix) and infix[i] not in "+-*/^()":
            return "Error"

        # Check for operator or parentheses
        if i < len(infix) and infix[i] in "+-*/^()":

            # Push left parenthesis onto stack
            if infix[i] == "(":
                stack.append("(")
                i += 1

            # Resolve addition operator, ignore multiple pluses
            elif infix[i] == "+":
                while stack and stack[-1] in "+-*/^#":
                    result.append(stack.pop())
                stack.append("+")
                while i < len(infix) and infix[i] == "+":
                    i += 1

            # Resolve subtraction operator, depending on number of minuses
            elif infix[i] == "-":
                while stack and stack[-1] in "+-*/^#":
                    result.append(stack.pop())
                minuses = 0
                while i < len(infix) and infix[i] == "-":
                    minuses += 1
                    i += 1
                if minuses % 2:
                    stack.append("-")
                else:
                    stack.append("+")

            # Resolve multiplication or division operator
            elif infix[i] in "*/":
                if i < len(infix) - 1 and infix[i + 1] == infix[i]:
                    return "Error"
                while stack and stack[-1] in "*/^#":
                    result.append(stack.pop())
                stack.append(infix[i])
                i += 1

            # Resolve power operator
            elif infix[i] == "^":
                if i < len(infix) - 1 and infix[i + 1] == infix[i]:
                    return "Error"
                while stack and stack[-1] == "^#":
                    result.append(stack.pop())
                stack.append(infix[i])
                i += 1

            # Resolve right parenthesis
            elif infix[i] == ")":
                while stack and stack[-1] != "(":
                    result.append(stack.pop())
                if not stack:
                    return "Error"
                else:
                    stack.pop()
                    i += 1

    # Append all remaining operators from stack to result
    while stack:
        if stack[-1] == "(":
            return "Error"
        result.append(stack.pop())

    return result


def rpn_to_result(rpn_list):
    """ Calculate result of expression in reverse Polish notation.

    Take list of integers, variables and operators in reverse Polish notation as parameter.
    Push all integers and variables onto stack, resolve all operators accordingly.
    If unary operator encountered with empty stack, throw Invalid expression error.
    If operator encountered with less than two integers in stack, throw Invalid expression error.
    If division by zero encountered, throw Invalid expression error.
    If uninitialized variable name encountered, throw Unknown variable error.
    If stack not empty at the end, throw Invalid expression error.
    If empty list received as parameter, return empty string.
    """

    stack = collections.deque()
    for i in range(len(rpn_list)):
        if isinstance(rpn_list[i], int):
            stack.append(rpn_list[i])
        elif rpn_list[i] == "#":
            if not stack:
                return "Invalid expression"
            stack.append(-1 * stack.pop())
        elif rpn_list[i] in "+-*/^":
            if len(stack) < 2:
                return "Invalid expression"
            if rpn_list[i] == "+":
                stack.append(stack.pop() + stack.pop())
            elif rpn_list[i] == "*":
                stack.append(stack.pop() * stack.pop())
            elif rpn_list[i] == "^":
                power = stack.pop()
                stack.append(stack.pop() ** power)
            elif rpn_list[i] == "-":
                subtrahend = stack.pop()
                stack.append(stack.pop() - subtrahend)
            elif rpn_list[i] == "/":
                divisor = stack.pop()
                if divisor == 0:
                    return "Invalid expression"
                stack.append(stack.pop() // divisor)
        else:
            try:
                stack.append(variables[rpn_list[i]])
            except KeyError:
                return "Unknown variable"
    if len(stack) > 1:
        return "Invalid expression"
    if not len(stack):
        return ""
    return stack.pop()


variables = {}  # dictionary to hold variables
line = ""
while line != "/exit":
    line = "".join(input().split())  # remove all whitespace from expression
    if line:
        if line.startswith("/"):
            parse_command(line)
        elif "=" in line:
            parse_assignment(line)
        else:
            result = parse_expression(line)
            print(result, end="\n" if result else "")
