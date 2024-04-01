from common.enums import TokenType
from components.lexcical_analyzer import Lexer, Token


class Parser:
    def __init__(self, lexer: Lexer, debug_print=False):
        """
        Initializes the Parser object.

        Parameters:
        - lexer (Lexer): A Lexer object that generates tokens for parsing.
        - debug_print (bool): A flag indicating whether to print a text to the console for debugging purposes.
        """
        self.__lexer = lexer
        self.__current_token = None  # Used to store extracted token from the Lexer
        self.__debug_print = debug_print
        self.__message_logs = list()

    def debug_print(self, text=str()):
        """
        Print the provided text if debug_print flag is True.

        Parameters:
        - text (str): The text to be printed.
        """
        if self.__debug_print:
            print(text)

    def debug_print_current_token(self):
        """
        Prints information about the current token if debug_print flag is True
        """
        if self.__debug_print:
            tokentype = self.__current_token.token_type.name.capitalize()
            print(
                f"Token: {tokentype:<20} Lexeme: {self.__current_token.lexeme}")

    def parse(self):
        """
        Parses the input by tokenizing it with the lexer and applying grammar rules.

        Returns:
            bool: True if parsing is successful, False otherwise.
        """
        parsing_result = False  # Initialize parsing result to False

        try:
            # Get the first token
            self.__current_token = self.__lexer.get_next_token()
            if self.__current_token is None:
                raise ValueError(f"The input is empty")

            # Apply the entry point rule, <Rat24S>
            self.__r1_Rat24S()

            # Set parsing_result to True, indicating that the parsing process was successful
            #  and there are no more tokens to be processed.
            # Otherwise, raise a ValueError
            if self.__current_token is None:
                parsing_result = True  # Parsing successful
            else:
                self.__log_current_token()
                raise ValueError(
                    f"Expected End Of File, but found {self.__current_token.lexeme}")
        except Exception as err:
            self.__log('-' * 50)
            print("\033[91m", end="")  # Print ANSI escape code for red color
            self.__log(f"Error: {err}\nParsing failed")
            print("\033[0m", end="")  # Print ANSI escape code to reset
        finally:
            return parsing_result

    def get_logs(self):
        """
        Retrieves the message logs generated during parsing.

        Returns:
            list: A list of messages logged during parsing.
        """
        return self.__message_logs
    
    def __log(self, text=str()):
        """
        Logs a text entry to the internal log list.

        Parameters:
        - text (str): The text to be added to the log. Default is an empty string.
        """
        self.__message_logs.append(text)
        if self.__debug_print:
            print(text)

    def __log_current_token(self):
        """
        Logs information about the current token, including its token type and lexeme.
        """
        tokentype = self.__current_token.token_type.name.capitalize()
        text = f"Token: {tokentype:<20} Lexeme: {self.__current_token.lexeme}"
        self.__message_logs.append(text)
        if self.__debug_print:
            print(text)

    def __match(self, expected_lexeme: str):
        """
        Compares the current token's lexeme with the expected lexeme.

        If the lexemes match, then advance to the next token using the lexer.get_next_token() method. 

        Otherwise, raise a ValueError indicating that the expected lexeme was not found.

        Parameters:
            expected_lexeme (str): The expected lexeme to match against the current token's lexeme.

        Raises:
            ValueError: If the current token's lexeme does not match the expected character.

        Returns:
            None
        """

        if self.__current_token.lexeme == expected_lexeme:
            self.__current_token = self.__lexer.get_next_token()
        else:
            raise ValueError(
                f'Expected {expected_lexeme}, found {self.__current_token.lexeme}')

    def __r1_Rat24S(self):
        """
        Applies the grammar rule 1:
        <Rat24S> -> $ 
                    <Opt Function Definitions> 
                    $ 
                    <Opt Declaration List> 
                    $ 
                    <Statement List> 
                    $
        """
        # Match the beginning of <Rat24S>, indicated by "$".
        self.__log_current_token()
        self.__match("$")

        # Apply rule 2 <Opt Function Definitions>
        self.__log("<Rat24S> -> <Opt Function Definitions>")
        self.__r2_optional_function_definitions()

        # Match the end of <Opt Function Definitions>, indicated by "$".
        self.__log_current_token()
        self.__match("$")

        # Apply rule 10 <Opt Declaration List>
        self.__log("<Rat24S> -> <Opt Declaration List>")
        self.__r10_optional_declaration_list()

        # Match the end of <Opt Function Definitions>, indicated by "$".
        self.__log_current_token()
        self.__match("$")

        # Apply rule 14 <Statement List>
        self.__r14a_statement_list()

        # Match the end of <Rat24S>, indicated by "$".
        self.__log_current_token()
        self.__match("$")

    def __r2_optional_function_definitions(self):
        """
        Applies the grammar rule 2: 
        <Opt Function Definitions> -> <Function Definitions> | ε
        """
        if self.__current_token.lexeme == "function":
            self.__log(
                "<Opt Function Definitions> -> <Function Definitions>")
            self.__r3a_function_definitions()
        else:
            self.__log("<Opt Function Definitions> -> ε")

    def __r3a_function_definitions(self):
        """
        Applies the production rule 3a: 
        <Function Definitions> -> <Function> <Function Definitions Prime>
        """
        self.__log(
            "<Function Definitions> -> <Function> <Function Definitions Prime>")
        self.__r4_function()
        self.__r3b_function_definitions_prime()

    def __r3b_function_definitions_prime(self):
        """
        Applies the production rule 3b: 
        <Function Definitions Prime> -> <Function Definitions> | ε
        """
        if self.__current_token.lexeme == "function":
            self.__log(
                "<Function Definitions Prime> -> <Function Definitions>")
            self.__r4_function()
        else:
            self.__log("<Function Definitions Prime> -> ε")

    def __r4_function(self):
        """
        Applies the production rule 4: 
        <Function> ::= function <Identifier> ( <Opt Parameter List> ) 
                                <Opt Declaration List> <Body>
        """
        self.__log_current_token()

        # Match the beginning of <Function>, indicated by "function".
        self.__match("function")  # Match and Move to the next token

        # Check if function's name exists
        if self.__current_token.token_type == TokenType.IDENTIFIER:
            self.__log(
                "<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
            self.__log_current_token()
            self.__match(self.__current_token.lexeme)  # Move to the next token

            # After the function's name, there must be an open parenthesis '('
            self.__log_current_token()
            self.__match("(")
            self.__r5_optional_parameter_list()

            # After the function's params, there must be a close parenthesis ')'
            self.__log_current_token()
            self.__match(")")

            self.__r10_optional_declaration_list()
            self.__r9_body()
        # Handle error: Function's name does not exist
        else:
            raise ValueError(
                f"Expected an Identifier, but found {self.__current_token.token_type}")

    def __r5_optional_parameter_list(self):
        """
        Applies the grammar rule 5: 
        <Opt Parameter List> -> <Parameter List> | ε
        """
        if self.__current_token.token_type == TokenType.IDENTIFIER:
            self.__log("<Opt Parameter List> -> <Parameter List>")
            self.__r6_parameter_list()
        else:
            self.__log("<Opt Parameter List> -> ε")

    def __r6_parameter_list(self):
        """
        Applies production rule r6
        <PL> -> <P> <P'>

        Notes:
        PL = <Parameter List>
        P  = <Parameter>
        P' = <Parameter Prime> 
        """
        self.__log_current_token()
        self.__log("<Parameter List> -> <Parameter> <Parameter Prime> ")
        self.__r7_parameter()
        self.__r6b_parameter_prime()
        
        #raise NotImplementedError("Must implement this method!")
    def __r6b_parameter_prime(self):
        """
        Applies production rule r6b
        <P'> -> ,<PL> | ε

        P' = Parameter Prime
        PL = Parameter List
        ε  = Epsilon
        """
        if self.__current_token.lexeme == ",":
            self.__log(f"<Parameter Prime> -> {self.__current_token.lexeme} <Parameter List>")
            self.__match(self.__current_token.lexeme)
            self.__log_current_token
            self.__r6_parameter_list()
        else:
            self.__log("<Parameter Prime> -> ε")


    def __r7_parameter(self):
        self.__log("<Parameter> -> <IDs> <Qualifier>")
        self.__r13_ids()
        self.__r8_qualifier()
        #raise NotImplementedError("Must implement this method!")

    def __r8_qualifier(self):
        if (self.__current_token.lexeme == "integer" or self.__current_token.lexeme == "boolean"  or 
        self.__current_token.lexeme == "real"):
            self.__log(f"<Qualifier> -> {self.__current_token.lexeme}")
            self.__match(self.__current_token.lexeme)
        else:
            text1 = f"Qualifier is missing."
            text2 = f"Expected token integer, real, or boolean, but found {self.__current_token.lexeme}"
            raise SyntaxError(f"{text1}\n{text2}")

    def __r9_body(self):
        self.__log_current_token()
        self.__match('{')
        self.__log("<Body> -> { <Statement List> }")
        self.__r14a_statement_list()
        self.__log_current_token()
        self.__match('}')

    def __r10_optional_declaration_list(self):
        if (self.__current_token.lexeme == "integer"
            or self.__current_token.lexeme == "real"
                or self.__current_token.lexeme == "boolean"):
            self.__log("<Opt Declaration List> -> <Declaration List>")
            self.__r11_declaration_list()
        else:
            self.__log("<Opt Declaration List> -> ε")

    def __r11_declaration_list(self):
        """
        Applies the production rule 11: 
        <Declaration List> -> <Declaration> ; <Declaration List Prime>
        """
        if (self.__current_token.lexeme == "integer"
            or self.__current_token.lexeme == "real"
                or self.__current_token.lexeme == "boolean"):            
            self.__log("<Declaration List> -> <Declaration> ;")
            self.__r12_declaration()
            self.__log_current_token()
            self.__match(";")
            self.__r11b_declaration_list_prime()

    def __r11b_declaration_list_prime(self):
        """
        Applies the production rule 11: 
        <Declaration List Prime> -> <Declaration List> | ε
        """
        if (self.__current_token.lexeme == "integer"
            or self.__current_token.lexeme == "real"
                or self.__current_token.lexeme == "boolean"):
            self.__log("<Declaration List Prime> -> <Declaration>")
            self.__r11_declaration_list()
        else:
            self.__log("<Declaration List Prime> -> ε")

    def __r12_declaration(self):
        """
        Applies the grammar rule 12: 
        <Declaration> ::= <Qualifier > <IDs>
        """
        self.__log("<Declaration> ::= <Qualifier > <IDs>")
        self.__log_current_token()
        self.__r8_qualifier()
        self.__r13_ids()

    def __r13_ids(self):
        """
        Applies the production rule 13a: 
        <IDs> -> <Identifier> <IDs Prime>
        """
        self.__log_current_token()
        if self.__current_token.token_type == TokenType.IDENTIFIER:
            self.__log("<IDs> -> <Identifier> <IDs Prime>")
            self.__match(self.__current_token.lexeme)
            self.__r13b_ids_prime()
        else:
            raise ValueError(
                f"Expected an Identifier, but found {self.__current_token.token_type}")

    def __r13b_ids_prime(self):
        """
        Applies the production rule 13b: 
        <IDs Prime> -> , <IDs> | ε
        """
        if self.__current_token.lexeme == ",":
            self.__log("<IDs Prime> -> , <IDs>")
            self.__match(self.__current_token.lexeme)  # Move to the next token
            self.__r13_ids()
        else:
            self.__log("<IDs Prime> -> ε")

    def __r14a_statement_list(self):
        """
        Applies the production rule 14a:
        <Statement List> -> <Statement> <Statement List Prime>
        """
        self.__log(
            "<Statement List> -> <Statement> <Statement List Prime>")
        self.__r15_statement()
        self.__r14b_statement_list_prime()

    def __r14b_statement_list_prime(self):
        """
        Applies the grammar rule 14b:
        <Statement List Prime> -> <Statement> | ε
        """
        first_of_statement = ("{", "if", "return", "print", "scan", "while")
        lexeme = self.__current_token.lexeme.lower()

        if (self.__current_token.token_type == TokenType.IDENTIFIER
                or lexeme in first_of_statement):
            self.__log("<Statement List Prime> -> <Statement>")
            self.__r15_statement()

    def __r15_statement(self):
        """
        Applies the grammar rule 15:
        <Statement> -> <Compound> | <Assign> | 
                        <If> | <Return> | 
                        <Print> | <Scan> | <While>
        """
        lexeme = self.__current_token.lexeme.lower()
        #  Check if the current token is an opening brace for a compound statement
        if lexeme == "{":
            self.__r16_compound()
        # Check if the current token is an identifier for an assignment statement
        elif self.__current_token.token_type == TokenType.IDENTIFIER:
            self.__log_current_token()
            self.__log("<Statement> -> <Assign>")
            self.__match(self.__current_token.lexeme)  # Move to the next token
            self.__r17_assign()
        # Check if the current token is the "if" keyword for an if statement
        elif lexeme == "if":
            self.__r18_if()
        elif lexeme == "return":
            self.__r19_return()
        elif lexeme == "print":
            self.__r20_print()
        elif lexeme == "scan":
            self.__r21_scan()
        elif lexeme == "while":
            self.__r22_while()
        else:
            text_1 = f"Statement is missing."
            text_2 = f"Expected a <Statement>, but found {self.__current_token.lexeme}"
            raise SyntaxError(f"{text_1}\n{text_2}")

    def __r16_compound(self):
        self.__log("<Compound> -> { <Statement List> }")
        self.__match('{')
        self.__r14a_statement_list()
        self.__match('}')

    def __r17_assign(self):
        """
        Applies the grammar rule 17:
        <Assign> -> <Identifier> = <Expression> ;
        """
        self.__log("<Assign> -> <Identifier> = <Expression> ;")

        if self.__current_token.lexeme == "=":
            self.__log_current_token()
            self.__match(self.__current_token.lexeme)  # Move to the next token
            self.__r25a_expression()

            # Match the end of <Assign>, indicated by a semicolon ";".
            self.__match(";")  # Match & Move to the next token
        else:
            text_1 = f"Assignment operator is missing."
            text_2 = f"Expected `=`, but found {self.__current_token.lexeme}"
            raise SyntaxError(f"{text_1}\n{text_2}")

    def __r18_if(self):
        raise NotImplementedError("Must implement this method!")

    def __r19_return(self):
        """
        Applies the production rule 19a:
        R --> rR'

        R = <Return>
        r = return
        R` = <Return Prime>
        """

        
        self.__log_current_token()
        self.__match("return")
        self.__log(f"<Return> -> return <Return Prime>")
        self.__r19_return_b_prime()
        
    def __r19_return_b_prime(self):
        """
        R' --> ; | E

        R' = <Return Prime>
        ; = symbol ;
        E = <Expression>
        """

        # Check to see if the current token is a separator, ;
        if self.__current_token.lexeme == ";":
            self.__log(f"<Return Prime> -> ;")
            self.__match(self.__current_token.lexeme) # Move to the next token

        
        # Check to see if <Expression>, after left-recursion, leads E -> TE'
        else:
            self.__log(f"<Return Prime> -> <Expression>;")
            self.__r25a_expression()
            self.__match(';')
        
    def __r20_print(self):
        self.__log(f"<Print> -> print ( <Expression> );")
        self.__match("print")
        self.__log_current_token()
        self.__match('(')
        self.__r25a_expression()
        self.__log_current_token()
        self.__match(')')
        self.__match(';')


    def __r21_scan(self):
        raise NotImplementedError("Must implement this method!")

    def __r22_while(self):
        """
        Applies the grammar rule 24: 
        <While> -> while ( <Condition> ) <Statement> endwhile

        Raises:
            SyntaxError: 
        """
        self.__log_current_token()
        self.__log("<While> -> while ( <Condition> ) <Statement> endwhile")

        # Match the beginning of <While>, indicated by "while".        
        self.__match("while")

        # Match the open parenthesis, indicated by "(".
        self.__log_current_token()
        self.__match("(")

        # Apply rule 23 <Condition>
        self.__r23_condition()

        # Match the close parenthesis, indicated by ")".
        self.__log_current_token()
        self.__match(")")

        # Apply rule 15 <Statement>
        self.__r15_statement()

         # Match the end of <While>, indicated by "endwhile".
        self.__log_current_token()
        self.__match("endwhile")

    def __r23_condition(self):
        """
        Applies the grammar rule 23: 
        <Condition> -> <Expression> <Relop> <Expression>
        """
        self.__log("<Condition> -> <Expression> <Relop> <Expression>")
        self.__r25a_expression()
        self.__r24_relop()
        self.__r25a_expression()

    def __r24_relop(self):
        """
        Applies the grammar rule 24: 
        <Relop> -> == | != | > | < | <= | =>

        Raises:
            SyntaxError: If the current token is not a valid relational operator.
        """
        relation_operators = {"==", "!=", ">", "<", "<=", "=>"}
        lexeme = self.__current_token.lexeme.lower()

        if lexeme in relation_operators:
            self.__log_current_token()
            self.__log(f"<Relop> -> {self.__current_token.lexeme}")
            self.__match(self.__current_token.lexeme)
        else:
            text1 = f"Relation operator is missing."
            text2 = f"Expected `{relation_operators}`, but found {self.__current_token.lexeme}"
            raise SyntaxError(f"{text1}\n{text2}")

    def __r25a_expression(self):
        """
        Applies the production rule 25a: 
        E -> TE'

        Notes:
        E is <Expression>
        E' is <Expression Prime>
        T is <Term>
        """

        self.__log_current_token()
        self.__log("<Expression> -> <Term> <Expression Prime>")

        self.__r26a_term()
        self.__r25b_expression_prime()

    def __r25b_expression_prime(self):
        """
        Applies the production rule 25b: 
        E' -> +TE' | -TE' | ε

        Notes:
        E' is <Expression Prime>
        T is <Term>
        """
        # Check for '+' or '-' case
        if self.__current_token.lexeme == "+" or self.__current_token.lexeme == "-":
            self.__log_current_token()
            self.__log(
                f"<Expression Prime> -> {self.__current_token.lexeme} <Term> <Expression Prime>")
            self.__match(self.__current_token.lexeme)  # Move to the next token
            
            self.__r26a_term()
            self.__r25b_expression_prime()
        # Handle Epsilon case
        else:
            self.__log("<Expression Prime> -> ε")

    def __r26a_term(self):
        """
        Applies the production rule 26a:
        T -> FT'

        Notes:
        F is <Factor>
        T is <Term>
        T' is <Term Prime>
        """
        # self.__log_current_token()
        self.__log("<Term> -> <Factor> <Term Prime>")

        self.__r27_factor()
        self.__r26b_term_prime()

    def __r26b_term_prime(self):
        """
        Applies the production rule 26b:
        T' -> *FT' | /FT' | ε

        Notes:
        F is <Factor>
        T is <Term>
        T' is <Term Prime>
        """

        # Check for '*' or '/' case
        if self.__current_token.lexeme == "*" or self.__current_token.lexeme == "/":
            self.__log_current_token()

            # Generate and print production rule text
            text = f"<Term Prime> -> {self.__current_token.lexeme} <Factor> <Term Prime>"
            self.__log(text)

            self.__match(self.__current_token.lexeme)  # Move to the next token

            # Apply production rules for Factor and Term Prime recursively
            self.__r27_factor()
            self.__r26b_term_prime()
        # Handle Epsilon case
        else:
            self.__log("<Term Prime> -> ε")

    def __r27_factor(self):
        """
        Applies the grammar rule 27:
        <Factor> -> - <Primary> | <Primary>
        """
        text_to_print = ""

        if self.__current_token.lexeme == "-":
            self.__match(self.__current_token.lexeme)  # Move to the next token
            text_to_print = "<Factor> -> - "            
        else:
            text_to_print = "<Factor> -> "
        
        primary_type = self.__r28_primary()      

        if primary_type:
            text_to_print = f"{text_to_print} {primary_type}"
            self.__log(text_to_print)

    def __r28_primary(self):
        """
        Applies the grammar rule 28:
        <Primary> -> <Identifier> <Primary Prime> | 
                    <Integer> | ( <Expression> ) |
                    <Real> | true | false

        Returns:
            str: The text representing the parsed primary token
        """
        text = ""

        # Case 1: IDENTIFIER
        if self.__current_token.token_type == TokenType.IDENTIFIER:
            self.__match(self.__current_token.lexeme)  # Move to the next token
            text = self.__r28b_primary_prime()
            text = f"<Identifier> {text}"
        # Case 2: INTEGER, REAL
        elif (self.__current_token.token_type == TokenType.INTEGER
                or self.__current_token.token_type == TokenType.REAL
            ):
            text = f"<{self.__current_token.token_type.name}>"
            self.__match(self.__current_token.lexeme)  # Move to the next token
        # Case 3: "true" or "false"
        elif (self.__current_token.lexeme == "true" or self.__current_token.lexeme == "false"):
            text = self.__current_token.lexeme
            self.__match(self.__current_token.lexeme)  # Move to the next token
        # Case 4: ( <Expression> )
        elif self.__current_token.lexeme == "(":
            self.__log("<Primary Prime> -> ( <Expression> )")
            self.__match(self.__current_token.lexeme)  # Move to the next token
            self.__r25a_expression()
            self.__match(")")  # Match and Move to the next token
            self.__log("<Primary Prime> -> ( <Expression> )")
        # Handle error: The current token does not match any expected types
        else:
            raise ValueError(
                f'Expected `ID, Number, (Expression), boolean`, but found {self.__current_token.token_type}')

        return text

    def __r28b_primary_prime(self):
        """
        Applies the grammar rule 28:
        <Primary Prime> -> ( <IDs> ) | ε
        """
        text = ""
        if (self.__current_token.lexeme == "("):
            # After the function's name, there must be an open parenthesis '('
            self.__log_current_token()
            self.__match("(")  # Match and Move to the next token

            self.__r13_ids()

            # After the function's params, there must be a close parenthesis ')'
            self.__log_current_token()
            self.__match(")")  # Match and Move to the next token
            text = "( <IDs> )"

        return text