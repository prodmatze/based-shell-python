from os.path import isfile
import sys
import os
import subprocess
import shlex
from itertools import chain

builtin_commands = ["echo", "exit", "type", "pwd", "cd"]
builtin_operators = {
    "stdout_ops": [">", "1>"],
    "stderr_ops": ["2>"]
}

STD_OUT = "std_out"
STD_ERR = "std_err"
STD_INFO = "std_info"

def parse_input(user_input):
    tokens = shlex.split(user_input)
    
    if not tokens:
        return {}

    result = {
        "cmd": tokens[0], 
        "args": [],
        "redirect": False,
        "operator": None,
        "file": None
    }

    if any(op in tokens for op in builtin_operators["stdout_ops"]):
        if ">" in tokens:
            index = tokens.index(">")
        else:
            index = tokens.index("1>")
        result["operator"] = "1>"
        result["redirect"] = True

        result["args"] = tokens[1:index]
        if index + 1 >= len(tokens):
            print("Syntax error, no file provided for redirection")
        else:
            result["file"] = tokens[index+1]

    elif any(op in tokens for op in builtin_operators["stderr_ops"]):
        if "2>" in tokens:
            index = tokens.index("2>")
        result["operator"] = "2>"
        result["redirect"] = True

        result["args"] = tokens[1:index]
        if index + 1 >= len(tokens):
            print("Syntax error, no file provided for redirection")
        else:
            result["file"] = tokens[index+1]

    else:
        result["args"] = tokens[1:]

    return result

def find_executable(arg):
    paths = os.environ.get("PATH", "").split(":")
    for path in paths:
        candidate = os.path.join(path, arg)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None

def handle_builtin(parsed_input):
    cmd = parsed_input["cmd"]
    args = parsed_input["args"]
    redirect = parsed_input["redirect"]
    file = parsed_input["file"]
    operator = parsed_input.get("operator", None)
    output = []

    match cmd:
        case "echo":
            output = STD_OUT, " ".join(args)

        case "type":
            out_lines = []

            if not args:
                output = STD_ERR, f"{cmd}: missing argument"

            for arg in args:
                if arg in builtin_commands:
                    out_lines += [STD_OUT, f"{arg} is a shell builtin"]
                else:
                    executable = find_executable(arg)
                    if executable:
                        out_lines += [STD_OUT, f"{arg} is {executable}"]
                    else:
                        out_lines += [STD_ERR, f"{arg}: not found"]
            output = list(chain(out_lines)) #maybe use *out_lines, dunno

        case "pwd":
            output = STD_OUT, os.getcwd()

        case "cd":
            if not args:
                output = STD_ERR, "cd: missing argument"
            elif len(args) == 1:
                if args[0] == "~":
                    home = os.environ.get("HOME")
                    if home:
                        os.chdir(home)
                    else:
                        output = STD_INFO, "cd: HOME not set"
                elif os.path.isdir(args[0]):
                    try:
                        os.chdir(args[0])
                        output = ""
                    except Exception as e:
                        output = STD_ERR, f"cd: {e}"
                else:
                    output = STD_ERR, f"cd: {args[0]}: No such file or directory"
            else:
                output = STD_ERR, f"cd: {' '.join(args)}: Invalid path."
                
        case "exit":
            sys.exit(0)

    if redirect and file:
        # with open(file, "w") as f:
        #     f.write(output + "\n")
        handle_redirect(output, file, operator)
        if output[0] == STD_OUT and operator == "2>":
            print(output[1])
    elif output:
        print(output[1])

def handle_redirect(output, file, operator):
    match operator:
        case "1>":
            with open(file, "w") as f:
                f.write(output[1] + "\n")
        case "2>":
                with open(file, "w") as f:
                    if output[0] == STD_ERR:
                        f.write(output + "\n")
                    else:
                        f.write("")


    return None

        
def handle_external(parsed_input):
    cmd = parsed_input["cmd"]
    args = parsed_input["args"]
    redirect = parsed_input["redirect"]
    file = parsed_input["file"]
    operator = parsed_input.get("operator", None)

    try:
        if redirect:
            if not file:
                print(f"Redirection operator used, but no file specified")
            elif operator == "1>":
                with open(file, "w") as f:
                    subprocess.run([cmd] + args, stdout=f)
            elif operator == "2>":
                with open(file, "w") as f:
                    subprocess.run([cmd] + args, stderr=f)

        else:
            subprocess.run([cmd] + args)
    except FileNotFoundError:
        print(f"{cmd}: command not found")
        
def main():
    while True:
        print("$ ", end="", flush=True)

        #wait for user input
        try:
            user_input = input().strip()           #strip to avoid errors with extra whitespaces (e.g " echo hello", "echo hello ")
        except EOFError:                        #CTRL-D (exit shell)
            print("BYE BYE")
            break
        except KeyboardInterrupt:               #CTRL-C 
            print("")
            continue

        parsed_input = parse_input(user_input)


        cmd = parsed_input.get("cmd", None)

        error_msg = f"{cmd}: command not found"

        #handle empty input -> continue to next iteration if user just presses enter with no input
        if cmd == "" or not cmd:
            continue

        if cmd in builtin_commands:
            handle_builtin(parsed_input)
        else:
            executable = find_executable(cmd)
            if executable:
                handle_external(parsed_input)
            else:
                print(error_msg)


if __name__ == "__main__":
    main()
