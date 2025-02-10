from graphviz import Digraph
import os

class ShuntingYard:
    """Class to convert an infix regular expression to postfix notation using the Shunting Yard algorithm."""

    def __init__(self, operators):
        self.operators = operators  # Dictionary with operators and their precedence/associativity.

    def add_concatenation_operator(self, expression):
        """Adds explicit concatenation operators ('.') in the infix expression."""
        result = []
        for i in range(len(expression) - 1):
            result.append(expression[i])
            if (expression[i].isalnum() or expression[i] == ')') and (expression[i + 1].isalnum() or expression[i + 1] == '('):
                result.append('.')
        result.append(expression[-1])
        return ''.join(result)

    def validate_expression(self, expression):
        """Validates the regular expression for common syntax errors."""
        stack = []
        last_token = None

        for token in expression:
            if token.isalnum():  # Operands
                last_token = token
            elif token in self.operators:
                if token == '*':  # Validation for unary '*' operator
                    if last_token is None or last_token in self.operators or last_token == '(':
                        raise ValueError(f"Operator '*' is missing a valid operand.")
                elif token in ['|', '.']:  # Validation for binary operators
                    if last_token is None or last_token in self.operators or last_token == '(':
                        raise ValueError(f"Operator '{token}' is missing a valid left operand.")
                    last_token = token
                else:
                    raise ValueError(f"Invalid use of operator: {token}")
            elif token == '(':
                stack.append(token)
                last_token = token
            elif token == ')':
                if not stack or stack[-1] != '(':
                    raise ValueError("Unmatched closing parenthesis.")
                stack.pop()
                last_token = token
            else:
                raise ValueError(f"Unexpected token: {token}")

        if stack:
            raise ValueError("Unmatched opening parenthesis.")
        if last_token in self.operators and last_token != '*':
            raise ValueError(f"Expression ends with an operator: '{last_token}'.")

    def to_postfix(self, expression):
        """Converts the infix regular expression to postfix notation."""
        expression = self.add_concatenation_operator(expression)  # Add explicit concatenation operators
        self.validate_expression(expression)

        output = []
        stack = []

        for token in expression:
            if token.isalnum():  # Operands
                output.append(token)
            elif token in self.operators:  # Operators
                while (stack and stack[-1] in self.operators and
                       ((self.operators[token]['associativity'] == 'L' and
                         self.operators[token]['precedence'] <= self.operators[stack[-1]]['precedence']) or
                        (self.operators[token]['associativity'] == 'R' and
                         self.operators[token]['precedence'] < self.operators[stack[-1]]['precedence']))):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # Remove '(' from stack

        while stack:
            output.append(stack.pop())

        return ''.join(output)

class ThompsonConstruction:
    """Class to build an NFA using Thompson's construction."""

    def __init__(self):
        self.state_count = 0
        self.transitions = []  # List of transitions (state, symbol, state)

    def create_state(self):
        """Creates a new state and returns its ID."""
        self.state_count += 1
        return self.state_count - 1

    def construct(self, postfix_expression):
        """Builds an NFA from a postfix regular expression."""
        stack = []

        for token in postfix_expression:
            if token.isalnum():  # Operands
                start = self.create_state()
                end = self.create_state()
                self.transitions.append((start, token, end))
                stack.append((start, end))
            elif token == '*':  # Kleene star
                nfa_start, nfa_end = stack.pop()
                start = self.create_state()
                end = self.create_state()
                self.transitions.append((start, 'λ', nfa_start))
                self.transitions.append((nfa_end, 'λ', nfa_start))
                self.transitions.append((nfa_end, 'λ', end))
                self.transitions.append((start, 'λ', end))
                stack.append((start, end))
            elif token == '.':  # Concatenation
                nfa2_start, nfa2_end = stack.pop()
                nfa1_start, nfa1_end = stack.pop()
                self.transitions.append((nfa1_end, 'λ', nfa2_start))
                stack.append((nfa1_start, nfa2_end))
            elif token == '|':  # Union
                nfa2_start, nfa2_end = stack.pop()
                nfa1_start, nfa1_end = stack.pop()
                start = self.create_state()
                end = self.create_state()
                self.transitions.append((start, 'λ', nfa1_start))
                self.transitions.append((start, 'λ', nfa2_start))
                self.transitions.append((nfa1_end, 'λ', end))
                self.transitions.append((nfa2_end, 'λ', end))
                stack.append((start, end))

        return stack[0]

    def display_transitions(self):
        """Displays the transitions of the constructed NFA."""
        print("Transitions:")
        for transition in self.transitions:
            print(f"State {transition[0]} --({transition[1]})--> State {transition[2]}")

    def display_graph(self, filename):
        """Generates and displays the graph of the finite automaton."""
        dot = Digraph()
        for i in range(self.state_count):
            dot.node(str(i), f"State {i}")
        for start, symbol, end in self.transitions:
            dot.edge(str(start), str(end), label=symbol)

        # Save the graph in the 'graphs' folder with the specified name
        filepath = os.path.join('graphs', filename)
        dot.render(filepath, format='png', cleanup=True)
        print(f"The NFA graph has been generated and saved as '{filepath}.png'.")

# Define operators and their precedence/associativity
operators = {
    '|': {'precedence': 1, 'associativity': 'L'},
    '.': {'precedence': 2, 'associativity': 'L'},
    '*': {'precedence': 3, 'associativity': 'R'}
}

# List of test expressions
example_expressions = [
    "a",                        # 1. Simple symbol, automaton for a single character
    "b",                        # 2. Simple symbol, automaton for a single character
    "c",                        # 3. Simple symbol, automaton for a single character
    "ab",                       # 4. Simple concatenation between two symbols
    "a|b",                      # 5. Simple union between two symbols
    "a.b",                      # 6. Explicit concatenation between two symbols
    "a*",                       # 7. Simple Kleene star applied to a symbol
    "(a|b)*",                   # 8. Kleene star applied to the union of two symbols
    "a.b|c",                    # 9. Combination of union and concatenation
    "a|(b.c)",                  # 10. Union between a symbol and a concatenation
    "a.b.c",                    # 11. Multiple concatenation between three symbols
    "(a|b).c",                  # 12. Concatenation applied to the union of two symbols
    "a.(b|c)*",                 # 13. Concatenation applied to the iteration of a union
    "(a.b)|c",                  # 14. Union between a concatenation and a symbol
    "(a|b).(c|d)*",             # 15. Concatenation between two unions, with iteration on the second
    "(a|b.c)*",                 # 16. Kleene star applied to the union of a concatenation
    "a.(b|c).d",                # 17. Concatenation applied to two unions and a symbol
    "a|(b|(c.d))",              # 18. Multiple unions between symbols and concatenations
    "(a.b)|(c.d)",              # 19. Union between two concatenations
    "((a|b).c).d",              # 20. Multiple concatenation applied to unions
    "a.(b.c|d.e)",              # 21. Concatenation with multiple unions
    "a|",                       # 22. Operator '|' without operand after
    "*a",                       # 23. Operator '*' without operand before
    "(a|b",                     # 24. Open parenthesis without closing
    "a(b|c))",                  # 25. Extra closing parenthesis
    "|a",                       # 26. Operator '|' at the beginning of the expression
    "a|b|",                     # 27. Operator '|' without operand at the end
    "a..b",                     # 28. Two consecutive dots for concatenation
    "(a.b|(c|d.e)*).f",         # 29. Complex concatenation with unions and iteration
    "((a|b)*.c)|d",             # 30. Iteration applied to union, concatenation, and external union
    "(a|b)*.c*",                # 31. Iteration applied to union and symbol
    "(((a|b).c)*.d)|(e.f.g)",   # 32. Complex concatenations and multiple unions
    "((a|b)*.(c|d))|(e.f)",     # 33. Union between complex concatenations
    "a|b*",                     # 34. Union between a symbol and iteration
    "a(b|c)*",                  # 35. Concatenation between a symbol and the iteration of a union
    "((a|b.b)*.(c|a.a)*|b.a).a", # 36. Complex concatenation between unions, iterations, and multiple concatenations
    "ba*|c"                      # 37. Union between a symbol concatenated with an iteration and a simple symbol
]

for idx, regex_infix in enumerate(example_expressions, 1):
    print(f"Example {idx}: Infix expression: {regex_infix}")
    try:
        shunting_yard = ShuntingYard(operators)
        regex_postfix = shunting_yard.to_postfix(regex_infix)
        print(f"Postfix expression: {regex_postfix}")
        thompson = ThompsonConstruction()
        start, end = thompson.construct(regex_postfix)
        print(f"Start state: {start}, Final state: {end}")
        thompson.display_transitions()
        thompson.display_graph(f"afn_graph_{idx}")
    except ValueError as e:
        print(f"Error in expression: {e}")
    except IndexError as e:
        print(f"Error in NFA construction: {e}")
    print("\n" + "-" * 50 + "\n")
