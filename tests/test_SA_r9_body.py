import unittest
import os
from common.enums import TokenType
from components.lexcical_analyzer import Lexer, Token
from components.syntax_analyzer import Parser
from tests.helpers import write_to_file, get_result_from_parser


class BodyTestCase(unittest.TestCase):
    SAMPLE_FILE_PATH = "tests/sample1.txt"

    def setUp(self) -> None:
        if os.path.exists(self.SAMPLE_FILE_PATH):
            os.remove(self.SAMPLE_FILE_PATH)

    def tearDown(self) -> None:
        if os.path.exists(self.SAMPLE_FILE_PATH):
            os.remove(self.SAMPLE_FILE_PATH)

    
    def test_body(self):
        # Arrange
        input_string = "$ function abc() { a= b + z; } $ $ num = 1; $"
        expected_output = True

        # Act
        write_to_file(self.SAMPLE_FILE_PATH, input_string)
        actual_output = get_result_from_parser(self.SAMPLE_FILE_PATH)

        # Assert
        self.assertEqual(actual_output, expected_output)


    def test_body_no_closing_brace(self):
        input_string = "$$ function abc() { a- 2; $"
        with open(self.SAMPLE_FILE_PATH, 'w') as file:
            file.write(input_string)
        
        lexer = Lexer(self.SAMPLE_FILE_PATH)
        parser = Parser(lexer, debug_print=True)
        parser.debug_print()
        parser.debug_print()
        parsing_success = parser.parse()

        self.assertFalse(parsing_success)

    def test_body_no_opening_brace(self):
        input_string = "$ function abc() a - -5;}$"
        with open(self.SAMPLE_FILE_PATH, 'w') as file:
            file.write(input_string)

        lexer = Lexer(self.SAMPLE_FILE_PATH)
        parser = Parser(lexer, debug_print=True)
        parser.debug_print()
        parser.debug_print()
        parsing_success = parser.parse()

        self.assertFalse(parsing_success)

    def test_body_no_braces(self):
        input_string = "$$ function abc() a - c; $"
        with open(self.SAMPLE_FILE_PATH, 'w') as file:
            file.write(input_string)

        lexer = Lexer(self.SAMPLE_FILE_PATH)
        parser = Parser(lexer, debug_print=True)
        parser.debug_print()
        parser.debug_print()
        parsing_success = parser.parse()

        self.assertFalse(parsing_success)



if __name__ == '__main__':
    unittest.main()
    
