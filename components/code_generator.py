from components.lexcical_analyzer import Lexer
from components.syntax_analyzer import Parser
from components.symbol_table import SymbolTable
from components.instruction_table import InstructionTable
from dataclasses import dataclass


class CodeGenerator:

    def __init__(self, lexer: Lexer, initial_memory_address=5000):
        """
        Initializes the IntermediateCodeGenerator object.
        """
        self.__symbol_table = SymbolTable(initial_memory_address)
        self.__instruction_table = InstructionTable(initial_address=1)
        self.__parser = Parser(lexer=lexer, debug_print=False)

    def generate_assembly_code(self):
        """
        Get the generated code.

        Returns:
        - str: The generated code as a string.
        """
        self.__parser.enable_code_generation(symbol_table=self.__symbol_table,
                                             instruction_table=self.__instruction_table)
        self.__parser.parse()
        return self.__instruction_table.get_generated_code()

    def print_symbol_table(self):
        """
        Prints the symbol table.
        """
        self.__symbol_table.print_table()

    def print_instruction_table(self):
        """
        Prints the instruction table.
        """
        self.__instruction_table.print_table()