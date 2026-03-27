import re

class CodeGenerator:
    """
    Utility to generate syntactically correct starter code (boilerplate) 
    for various languages based on function metadata.
    """

    @staticmethod
    def generate_starter_code(lang, func_name, params, return_type="void"):
        """
        Generates boilerplate for a specific language.
        params: list of dicts like {'name': 'arr', 'type': 'int[]'}
        """
        lang = lang.lower().strip()
        
        if lang == 'python':
            return CodeGenerator._python(func_name, params)
        elif lang == 'java':
            return CodeGenerator._java(func_name, params, return_type)
        elif lang == 'javascript':
            return CodeGenerator._javascript(func_name, params)
        elif lang == 'cpp':
            return CodeGenerator._cpp(func_name, params, return_type)
        elif lang == 'csharp':
            return CodeGenerator._csharp(func_name, params, return_type)
        elif lang == 'sql':
            return "-- Write your SQL query here\n"
        
        return f"// Starter code for {lang} not implemented.\n// Function: {func_name}\n"

    @staticmethod
    def _python(name, params):
        args = ", ".join([p['name'] for p in params])
        return f"def {name}({args}):\n    # Write your code here\n    pass\n"

    @staticmethod
    def _java(name, params, ret_type):
        # Map types to Java types
        type_map = {
            'int[]': 'int[]', 'String[]': 'String[]', 'int': 'int', 
            'String': 'String', 'boolean': 'boolean', 'void': 'void',
            'double': 'double', 'float': 'float', 'long': 'long',
            'List<Integer>': 'List<Integer>', 'List<String>': 'List<String>',
            'Integer': 'Integer', 'Boolean': 'Boolean'
        }
        java_params = ", ".join([f"{type_map.get(p['type'], 'Object')} {p['name']}" for p in params])
        java_ret = type_map.get(ret_type, 'Object')
        
        return (
            f"public class Solution {{\n"
            f"    public {java_ret} {name}({java_params}) {{\n"
            f"        // Write your code here\n"
            f"        return {CodeGenerator._java_default(ret_type)};\n"
            f"    }}\n"
            f"}}"
        )

    @staticmethod
    def _java_default(ret_type):
        if ret_type == 'boolean': return 'false'
        if ret_type in ['int', 'double', 'float']: return '0'
        if ret_type == 'void': return ''
        return 'null'

    @staticmethod
    def _javascript(name, params):
        args = ", ".join([p['name'] for p in params])
        return f"function {name}({args}) {{\n    // Write your code here\n\n}}\n"

    @staticmethod
    def _cpp(name, params, ret_type):
        cpp_params = ", ".join([f"{p['type']} {p['name']}" for p in params])
        return (
            f"#include <iostream>\n#include <vector>\n#include <string>\n\n"
            f"using namespace std;\n\n"
            f"class Solution {{\n"
            f"public:\n"
            f"    {ret_type} {name}({cpp_params}) {{\n"
            f"        // Write your code here\n"
            f"    }}\n"
            f"}};"
        )

    @staticmethod
    def _csharp(name, params, ret_type):
        cs_params = ", ".join([f"{p['type']} {p['name']}" for p in params])
        return (
            f"using System;\n\n"
            f"public class Solution {{\n"
            f"    public {ret_type} {name}({cs_params}) {{\n"
            f"        // Write your code here\n"
            f"        return {CodeGenerator._java_default(ret_type)};\n"
            f"    }}\n"
            f"}}"
        )
