import unittest
import os
from io import StringIO
from tests.unit.helpers import write_to_file, get_result_from_code_generator


class IfTestCase(unittest.TestCase):
    SAMPLE_FILE_PATH = "tests/sample1.txt"

    def setUp(self):
        if os.path.exists(self.SAMPLE_FILE_PATH):
            os.remove(self.SAMPLE_FILE_PATH)

    def tearDown(self):
        if os.path.exists(self.SAMPLE_FILE_PATH):
            os.remove(self.SAMPLE_FILE_PATH)

    def test_sample(self):
        input_string = """
            $
            $
            integer a, b, c;
            $
            if (a < b) a = c; endif
            $            
        """

        string_builder = StringIO()
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("LES\n")
        string_builder.write("JUMP0 7\n")
        string_builder.write("PUSHM 5002\n")
        string_builder.write("POPM 5000\n")
        string_builder.write("LABEL\n")
 
        expected_output = string_builder.getvalue()

        # Act
        write_to_file(self.SAMPLE_FILE_PATH, input_string)
        actual_output = get_result_from_code_generator(self.SAMPLE_FILE_PATH)

        # Assert
        self.assertEqual(actual_output, expected_output)

    def test_if_else(self):
        input_string = """
            $
            $
            integer a, b, c;
            $
            if (a == b ) c = 0; else a = 85; endif 
            $
        """
        string_builder = StringIO()
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("EQU\n")
        string_builder.write("JUMP0 8\n")
        string_builder.write("PUSHI 0\n")
        string_builder.write("POPM 5002\n")
        string_builder.write("JUMP 10\n")
        string_builder.write("PUSHI 85\n")
        string_builder.write("POPM 5000\n")
        string_builder.write("LABEL\n")
 
        expected_output = string_builder.getvalue()

        # Act
        write_to_file(self.SAMPLE_FILE_PATH, input_string)
        actual_output = get_result_from_code_generator(self.SAMPLE_FILE_PATH)

        # Assert
        self.assertEqual(actual_output, expected_output)

    def test_nested_if_else(self):
        input_string = """
        $
        $
            integer a, b, c;
            $
            if (a == b )
            {
                c = 0;
                print(c);
            }
            else 
            {
                a = 85;
                print(a);
                scan(a);
                if (a < 10)
                    print(999);
                endif
            }
            endif 
            $
        """
        string_builder = StringIO()
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("EQU\n")
        string_builder.write("JUMP0 10\n")
        string_builder.write("PUSHI 0\n")
        string_builder.write("POPM 5002\n")
        string_builder.write("PUSHM 5002\n")
        string_builder.write("SOUT\n")
        string_builder.write("JUMP 23\n")
        string_builder.write("PUSHI 85\n")
        string_builder.write("POPM 5000\n")
        string_builder.write("PUSHM 5000\n")
        string_builder.write("SOUT\n")
        string_builder.write("SIN\n")
        string_builder.write("POPM 5000\n")
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHI 10\n")
        string_builder.write("LES\n")
        string_builder.write("JUMP0 22\n")
        string_builder.write("PUSHI 999\n")
        string_builder.write("SOUT\n")
        string_builder.write("LABEL\n")
        string_builder.write("LABEL\n")
 
        expected_output = string_builder.getvalue()

        # Act
        write_to_file(self.SAMPLE_FILE_PATH, input_string)
        actual_output = get_result_from_code_generator(self.SAMPLE_FILE_PATH)

        # Assert
        self.assertEqual(actual_output, expected_output)

    def test_nested_ifs(self):
        input_string = """
            $ 
            $ 
            integer a, b, c, d;
            $ 
                if (a == b) 
                    if (a => b) 
                        if (a <= b) {
                            a = b + 1;
                            if (a != b) 
                                print(c);
                            else
                                print(d);
                            endif
                        }
                        else {
                            b = b + 3;
                            a = a * b;
                        }
                        endif
                    endif
                endif
            $
            """
        string_builder = StringIO()
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("EQU\n")
        string_builder.write("JUMP0 38\n")
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("GEQ\n")
        string_builder.write("JUMP0 37\n")
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("LEQ\n")
        string_builder.write("JUMP0 28\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("PUSHI 1\n")
        string_builder.write("A\n")
        string_builder.write("POPM 5000\n")
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("NEQ\n")
        string_builder.write("JUMP0 24\n")
        string_builder.write("PUSHM 5002\n")
        string_builder.write("SOUT\n")
        string_builder.write("JUMP 26\n")
        string_builder.write("PUSHM 5003\n")
        string_builder.write("SOUT\n")
        string_builder.write("LABEL\n")
        string_builder.write("JUMP 36\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("PUSHI 3\n")
        string_builder.write("A\n")
        string_builder.write("POPM 5001\n")
        string_builder.write("PUSHM 5000\n")
        string_builder.write("PUSHM 5001\n")
        string_builder.write("M\n")
        string_builder.write("POPM 5000\n")
        string_builder.write("LABEL\n")
        string_builder.write("LABEL\n")
        string_builder.write("LABEL\n")
        expected_output = string_builder.getvalue()

        # Act
        write_to_file(self.SAMPLE_FILE_PATH, input_string)
        actual_output = get_result_from_code_generator(self.SAMPLE_FILE_PATH)

        # Assert
        self.assertEqual(actual_output, expected_output)
if __name__ == '__main__':
    unittest.main()