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
        -(void)setAccessibilityIdentifiers {
            $variable_set
        }
        """
        output = Analyzer.call_grep(file_path)
        class_name = re.compile("[\w-]+\.")
        var_name = re.compile("\*(.+?);")
        for line in iter(output.stdout.readline, b''):
            self.lines.append(str(line))
        for l in self.lines:
            if not class_name.findall(l)[0][:-1] in self.outlets:
                self.outlets[class_name.findall(l)[0][:-1]] = []
            if class_name.findall(l)[0][:-1] in self.outlets:
                if var_name.findall(l):
                    self.outlets[class_name.findall(l)[0][:-1]].append(var_name.findall(l)[0])

    def print_methods(self):
        for class_name, variables_array in self.outlets.items():
            function_body = ""
            for index, variable in enumerate(variables_array):
                tabs = "\t" if index != 0 else ""
                function_body += '%sself.%s.accessibilityIdentifier = @"%s";\n' % (tabs, variable, variable)
            self.functions.append(Template(self.function_template).substitute(dict(variable_set=function_body)))

        for function in self.functions:
            print(function)
            print()

    @staticmethod
    def call_grep(file_path):
        # return call(["grep", "-r", "-i", "--include", "\*.h", "--include", "\*m", "IBOutlet", file_path], shell=True)
        return Popen("grep -r -i --include \*.h --include \*.m IBOutlet %s" % file_path, shell=True, stdout=PIPE)

a = Analyzer(argv[1])
a.print_methods()
