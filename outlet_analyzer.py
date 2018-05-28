#!/usr/local/bin/python3

from subprocess import call, PIPE, Popen
from sys import argv
from pprint import pprint
from string import Template
import re

class Analyzer:
    def __init__(self, file_path):
        self.outlets = {}
        self.lines = []
        self.functions = []
        self.function_template = """
        // $class_name
        -(void)setAccessibilityIdentifiers {
        $variable_set
        }
        """
        output = Analyzer.call_grep(file_path)
        class_name_expr = re.compile("[\w-]+\.")
        var_name = re.compile("\*(.+?);")
        for line in iter(output.stdout.readline, b''):
            self.lines.append(str(line))
        for line in self.lines:
            class_name = class_name_expr.findall(line)[0][:-1] 
            if not class_name in self.outlets:
                self.outlets[class_name] = []
            if class_name in self.outlets:
                if var_name.findall(line):
                    self.outlets[class_name].append(var_name.findall(line)[0])

    def print_methods(self):
        for class_name, variables_array in self.outlets.items():
            function_body = ""
            for index, variable in enumerate(variables_array):
                function_body += '\tself.%s.accessibilityIdentifier = @"%s";\n\t' % (variable, variable)
            self.functions.append(Template(self.function_template).substitute(dict(variable_set=function_body, class_name=class_name)))

        for index, function in enumerate(self.functions):
            print(function)
            print('<-------------------->', index)
            print()

    @staticmethod
    def call_grep(file_path):
        return Popen("grep -r -i --include \*.h --include \*.m IBOutlet %s" % file_path, shell=True, stdout=PIPE)

a = Analyzer(argv[1])
a.print_methods()
