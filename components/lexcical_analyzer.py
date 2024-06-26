from common.enums import TokenType
from common.reserved_words_symbols import KEYWORDS, SEPARATORS, SIMPLE_OPERATORS, COMPOUND_OPERATORS, DECIMAL_SEPARATOR, COMMENT_DELIMITER_BEGIN, COMMENT_DELIMITER_END
from dataclasses import dataclass
from components.FSM import FSM
from common.helpers import FileStream

@dataclass
class Token:
    """
    Represents a token in a programming language lexer.

    Attributes:
        lexeme (str): The textual representation of the token.
        token_type (TokenType): The type of the token.
    """

    lexeme: str
    token_type: TokenType


class Lexer:
    def __init__(self, file_path):
        """
        Initializes an instance of the FileReader class with the content of the specified file.

        Parameters:
            file_path (str): The path to the file to be read.

        Raises:
            FileNotFoundError: If the specified file_path does not exist.
            IOError: If an error occurs while attempting to read the file.
        """
        # Create Finite State Machines for IntegerReal and Identifier
        int_real_FSM = self.__build_int_real_FSM()
        identifier_FSM = self.__build_identifier_FSM()

        # Stop signs
        stop_signs = self.__get_stop_signs()
        
        self.tokens = list() # Store extracted tokens
        self.__current_index = -1  # Current index for token retrieval

        # Open the file in read mode
        filestream = FileStream(file_path)
        inside_comment = False # keeps track of whether we are currently inside a comment block

        try:
            # Read the first character
            current_char = filestream.read(1)

            # Loop until the end of file
            while current_char:

                # ****************************************
                # ***** COMMENT BLOCK BEGIN Checking *****
                # ****************************************
                if not inside_comment and current_char == COMMENT_DELIMITER_BEGIN[0]:
                    next_char = filestream.read(1)
                    if next_char == COMMENT_DELIMITER_BEGIN[1]:
                        inside_comment = True
                    else:
                        filestream.unread(next_char)
                        self.tokens.append(Token(current_char, TokenType.UNKNOWN))

                # ****************************************
                # ******* COMMENT BLOCK END Checking *****
                # ****************************************
                elif inside_comment and current_char == COMMENT_DELIMITER_END[0]:
                    next_char = filestream.read(1)

                    if next_char == COMMENT_DELIMITER_END[1]:
                        inside_comment = False
                    else:
                        filestream.unread(next_char)
                
                # ****************************************
                # **** IGNORE WHITESPACES & COMMENTS *****
                # ****************************************
                elif current_char == ' ' or current_char == '\n' or current_char == '\t' or inside_comment:
                    pass

                # ****************************************
                # ********* INT OR REAL Checking *********
                # ****************************************
                elif current_char.isdigit() or current_char == DECIMAL_SEPARATOR:
                    # Call FSM
                    result = int_real_FSM.traceDFSM(current_char, filestream, stop_signs)

                    if not result.accepted :
                        self.tokens.append(Token(result.lexeme, TokenType.UNKNOWN))
                    elif result.accepted_states[0] == 'B':
                        self.tokens.append(Token(result.lexeme, TokenType.INTEGER))
                    elif result.accepted_states[0] == 'D':
                        self.tokens.append(Token(result.lexeme, TokenType.REAL))

                # ****************************************
                # ********** IDENTIFIER Checking *********
                # ****************************************
                elif current_char.isalpha():
                    # Call FSM
                    result = identifier_FSM.traceDFSM(current_char, filestream, stop_signs)

                    if not result.accepted:
                        self.tokens.append(Token(result.lexeme, TokenType.UNKNOWN))
                    elif result.lexeme in KEYWORDS:
                        self.tokens.append(Token(result.lexeme, TokenType.KEYWORD))
                    else:
                        self.tokens.append(Token(result.lexeme, TokenType.IDENTIFIER))

                # ****************************************
                # ********* SEPARATOR Checking ***********
                # ****************************************
                elif current_char in SEPARATORS:
                    self.tokens.append(Token(current_char, TokenType.SEPARATOR))
                
                # ****************************************
                # ********** OPERATOR Checking ***********
                # ****************************************
                elif current_char in stop_signs:
                    # ----- COMPOUND_OPERATORS -----
                    next_char = filestream.read(1)
                    buffer = current_char + next_char
                    if buffer in COMPOUND_OPERATORS:
                        self.tokens.append(Token(buffer, TokenType.OPERATOR))
                    
                    # ----- SIMPLE_OPERATORS -----
                    elif current_char in SIMPLE_OPERATORS:
                        self.tokens.append(Token(current_char, TokenType.OPERATOR))
                        filestream.unread(next_char)
                    else:
                        filestream.unread(next_char)
                        
                        # Create a copy of the list of stop signs
                        new_stop_signs = stop_signs.copy()

                        # Remove the current character from the list of stop signs
                        new_stop_signs.remove(current_char)

                        # Call the Finite State Machine (FSM) function to consume the remaining characters
                        result = identifier_FSM.traceDFSM(current_char, filestream, new_stop_signs)

                        self.tokens.append(Token(result.lexeme, TokenType.UNKNOWN))
                
                # ****************************************
                # *************** ILLEGAL ****************
                # ****************************************
                else:
                    # Call the Finite State Machine (FSM) function to consume the remaining characters
                    result = identifier_FSM.traceDFSM(current_char, filestream, stop_signs)

                    self.tokens.append(Token(result.lexeme, TokenType.UNKNOWN))


                # Read the next character
                current_char = filestream.read(1)
        finally:
            # Close the file
            filestream.close()

    def get_next_token(self):
        """
        Retrieve the next token from the list of extracted tokens.

        Returns:
            Token or None: The next token object or None if end of tokens reached.
        """
        if self.__current_index < len(self.tokens) - 1:
            self.__current_index += 1
            return self.tokens[self.__current_index]
        else:
            return None
        
    def __get_stop_signs(self):
        new_set = set()

        # Extract the first character of each separator
        new_set.update({item[0] for item in SEPARATORS})

        # Extract the first character of each operator
        new_set.update({item[0] for item in SIMPLE_OPERATORS})

        # Extract the first character of each operator
        new_set.update({item[0] for item in COMPOUND_OPERATORS})

        # Add a space character and newline character
        new_set.update({' ', '\n', COMMENT_DELIMITER_BEGIN[0]})

        return new_set

    def __build_int_real_FSM(self):
        """
        Builds a Finite State Machine (FSM) to recognize integer and real numbers.

        Regular Expression: d+ | (d+.d+)

        Returns:
            FSM: A Finite State Machine instance configured to recognize integer and real numbers.
        """

        # FSM Configurations
        sigma = ['d', '.']
        states = ['A', 'B', 'C', 'D', 'E']
        initial_state = 'A'
        accepting_states = ['B', 'D']  # B: Integer, D: Real
        transition_table = [['B', 'E'],
                            ['B', 'C'],
                            ['D', 'E'],
                            ['D', 'E'],
                            ['E', 'E']]

        # Mapping function
        def char_to_symbol(char):
            if char.isdigit():
                return 'd'
            elif char.isalpha():
                return 'l'
            else:
                return char

        # Create an FSM instance
        fsm = FSM(sigma, states, initial_state,
                  accepting_states, transition_table, char_to_symbol)

        return fsm

    def __build_identifier_FSM(self):
        """
        Builds a Finite State Machine (FSM) to recognize identifiers.

        Regular Expression: l(l|d|_)*
        Where 'l' represents a letter, 'd' represents a digit, and '_' represents an underscore.

        Returns:
            FSM: A Finite State Machine instance configured to recognize identifiers.

        """
        # FSM Configurations
        sigma = ['l', 'd', '_']
        states = ['A', 'B', 'C', 'D', 'E', 'F']
        initial_state = 'A'
        accepting_states = ['B', 'C', 'D', 'E']
        transition_table = [['B', 'F', 'F'],
                            ['C', 'D', 'E'],
                            ['C', 'D', 'E'],
                            ['C', 'D', 'E'],
                            ['C', 'D', 'E'],
                            ['F', 'F', 'F']]

        # Mapping function
        def char_to_symbol(char):
            if char.isdigit():
                return 'd'
            elif char.isalpha():
                return 'l'
            else:
                return char

        # Create an FSM instance
        fsm = FSM(sigma, states, initial_state,
                  accepting_states, transition_table, char_to_symbol)

        return fsm