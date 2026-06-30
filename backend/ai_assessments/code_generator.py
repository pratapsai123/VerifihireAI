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
        
        return (
            f"import sys\n\n"
            f"def {name}({args}):\n"
            f"    # Write your code here\n"
            f"    pass\n\n"
            f"if __name__ == '__main__':\n"
            f"    # Read all input from standard input\n"
            f"    input_data = sys.stdin.read().split()\n"
            f"    if not input_data: exit()\n\n"
            f"    # Parse your inputs here\n"
            f"    # Example: n = int(input_data[0])\n\n"
            f"    # result = {name}(...)\n"
            f"    # print(result)\n"
        )

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
        
        # Build automatic parsing logic for main method
        parsing_logic = []
        parsing_logic.append("Scanner sc = new Scanner(System.in);")
        
        call_args = []
        for p in params:
            p_name = p['name']
            p_type = p['type']
            
            if p_type == 'int':
                parsing_logic.append(f"        int {p_name} = sc.nextInt();")
                call_args.append(p_name)
            elif p_type == 'String':
                parsing_logic.append(f"        String {p_name} = sc.next();")
                call_args.append(p_name)
            elif p_type == 'int[]':
                # Assume standard [N, items...] or [items... if N is known]
                # If there's a previous 'int' parameter, we might use it as size, 
                # but usually CP-style inputs for arrays provide the size first.
                parsing_logic.append(f"        // Assuming next integer is the size of {p_name}")
                parsing_logic.append(f"        int {p_name}_size = sc.nextInt();")
                parsing_logic.append(f"        int[] {p_name} = new int[{p_name}_size];")
                parsing_logic.append(f"        for(int i=0; i<{p_name}_size; i++) {p_name}[i] = sc.nextInt();")
                call_args.append(p_name)
            elif p_type == 'String[]':
                parsing_logic.append(f"        int {p_name}_size = sc.nextInt();")
                parsing_logic.append(f"        String[] {p_name} = new String[{p_name}_size];")
                parsing_logic.append(f"        for(int i=0; i<{p_name}_size; i++) {p_name}[i] = sc.next();")
                call_args.append(p_name)
            elif p_type == 'List<String>':
                parsing_logic.append(f"        int {p_name}_size = sc.nextInt();")
                parsing_logic.append(f"        List<String> {p_name} = new ArrayList<>();")
                parsing_logic.append(f"        for(int i=0; i<{p_name}_size; i++) {p_name}.add(sc.next());")
                call_args.append(p_name)
            else:
                parsing_logic.append(f"        // TODO: Parse {p_name} ({p_type})")
                call_args.append("null")

        parsed_str = "\n".join(parsing_logic)
        call_str = ", ".join(call_args)
        
        return (
            f"import java.util.*;\n\n"
            f"public class Solution {{\n"
            f"    /**\n"
            f"     * Write your logic here.\n"
            f"     * Note: To preserve order during frequency counts, use LinkedHashMap.\n"
            f"     */\n"
            f"    public {java_ret} {name}({java_params}) {{\n"
            f"        // Your code here\n"
            f"        return {CodeGenerator._java_default(ret_type)};\n"
            f"    }}\n\n"
            f"    public static void main(String[] args) {{\n"
            f"        {parsed_str}\n\n"
            f"        Solution sol = new Solution();\n"
            f"        {java_ret} result = sol.{name}({call_str});\n\n"
            f"        System.out.println(result);\n"
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
        
        # Build automatic parsing logic
        parsing_logic = []
        parsing_logic.append("    const fs = require('fs');\n    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/);\n    let idx = 0;\n")
        
        call_args = []
        for p in params:
            p_name = p['name']
            p_type = p['type']
            
            if p_type == 'int':
                parsing_logic.append(f"    const {p_name} = parseInt(input[idx++], 10);")
                call_args.append(p_name)
            elif p_type in ['string', 'String']:
                parsing_logic.append(f"    const {p_name} = input[idx++];")
                call_args.append(p_name)
            elif p_type in ['int[]', 'number[]']:
                parsing_logic.append(f"    const {p_name}_size = parseInt(input[idx++], 10);")
                parsing_logic.append(f"    const {p_name} = input.slice(idx, idx + {p_name}_size).map(x => parseInt(x, 10));\n    idx += {p_name}_size;")
                call_args.append(p_name)
            elif p_type in ['String[]', 'string[]']:
                parsing_logic.append(f"    const {p_name}_size = parseInt(input[idx++], 10);")
                parsing_logic.append(f"    const {p_name} = input.slice(idx, idx + {p_name}_size);\n    idx += {p_name}_size;")
                call_args.append(p_name)
            else:
                parsing_logic.append(f"    // TODO: Parse {p_name}")
                call_args.append("null")

        parsed_str = "\n".join(parsing_logic)
        call_str = ", ".join(call_args)

        return (
            f"function {name}({args}) {{\n"
            f"    // Your code here\n\n"
            f"}}\n\n"
            f"function main() {{\n"
            f"{parsed_str}\n\n"
            f"    const result = {name}({call_str});\n"
            f"    console.log(result);\n"
            f"}}\n\n"
            f"main();\n"
        )

    @staticmethod
    def _cpp(name, params, ret_type):
        cpp_params = ", ".join([f"{p['type']} {p['name']}" for p in params])
        
        # Build automatic parsing logic
        parsing_logic = []
        call_args = []
        
        for p in params:
            p_name = p['name']
            p_type = p['type']
            
            if p_type == 'int':
                parsing_logic.append(f"    int {p_name};\n    cin >> {p_name};")
                call_args.append(p_name)
            elif p_type == 'string' or p_type == 'String':
                parsing_logic.append(f"    string {p_name};\n    cin >> {p_name};")
                call_args.append(p_name)
            elif p_type == 'int[]' or p_type == 'vector<int>':
                parsing_logic.append(f"    int {p_name}_size;\n    cin >> {p_name}_size;")
                parsing_logic.append(f"    vector<int> {p_name}({p_name}_size);\n    for(int i=0; i<{p_name}_size; i++) cin >> {p_name}[i];")
                call_args.append(p_name)
            elif p_type == 'vector<string>':
                parsing_logic.append(f"    int {p_name}_size;\n    cin >> {p_name}_size;")
                parsing_logic.append(f"    vector<string> {p_name}({p_name}_size);\n    for(int i=0; i<{p_name}_size; i++) cin >> {p_name}[i];")
                call_args.append(p_name)
            else:
                parsing_logic.append(f"    // TODO: Parse {p_name}")
                call_args.append("/* TODO */")

        parsed_str = "\n".join(parsing_logic)
        call_str = ", ".join(call_args)
        
        return (
            f"#include <iostream>\n#include <vector>\n#include <string>\n#include <algorithm>\n\n"
            f"using namespace std;\n\n"
            f"class Solution {{\n"
            f"public:\n"
            f"    {ret_type} {name}({cpp_params}) {{\n"
            f"        // Your code here\n"
            f"        return {{}};\n"
            f"    }}\n"
            f"}};\n\n"
            f"int main() {{\n"
            f"    ios_base::sync_with_stdio(false);\n"
            f"    cin.tie(NULL);\n\n"
            f"{parsed_str}\n\n"
            f"    Solution sol;\n"
            f"    {ret_type} result = sol.{name}({call_str});\n\n"
            f"    cout << result << endl;\n"
            f"    return 0;\n"
            f"}}"
        )

    @staticmethod
    def _csharp(name, params, ret_type):
        cs_params = ", ".join([f"{p['type']} {p['name']}" for p in params])
        
        # Simple C# parsing (using Console.In.ReadToEnd for simplicity)
        return (
            f"using System;\nusing System.Collections.Generic;\nusing System.Linq;\n\n"
            f"public class Solution {{\n"
            f"    public {ret_type} {name}({cs_params}) {{\n"
            f"        // Your code here\n"
            f"        return default({ret_type});\n"
            f"    }}\n\n"
            f"    public static void Main(string[] args) {{\n"
            f"        // For C#, reading all at once is safest for CP-style input\n"
            f"        string allInput = Console.In.ReadToEnd();\n"
            f"        string[] tokens = allInput.Split(new[] {{ ' ', '\\n', '\\r' }}, StringSplitOptions.RemoveEmptyEntries);\n"
            f"        if (tokens.Length == 0) return;\n\n"
            f"        var sol = new Solution();\n"
            f"        // Basic token usage - parsing logic can be expanded here\n"
            f"        // var result = sol.{name}(...);\n"
            f"        // Console.WriteLine(result);\n"
            f"    }}\n"
            f"}}"
        )
