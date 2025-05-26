from os.path import isfile
import sys
import os
import subprocess
import shlex

builtin_commands = ["echo", "exit", "type", "pwd", "cd"]
builtin_operators = [">", "1>", "<"]

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

    if any(op in tokens for op in [">", "1>"]):
        if ">" in tokens:
            index = tokens.index(">")
        else:
            index = tokens.index("1>")
        result["operator"] = ">"
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
    output = ""

    match cmd:
        case "echo":
            output = " ".join(args)

        case "type":
            output_lines = []
            if not args:
                output = f"{cmd}: missing argument"

            for arg in args:
                if arg in builtin_commands:
                    output_lines.append(f"{arg} is a shell builtin")
                else:
                    executable = find_executable(arg)
                    if executable:
                        output_lines.append(f"{arg} is {executable}")
                    else:
                        output_lines.append(f"{arg}: not found")
            output = "\n".join(output_lines)

        case "pwd":
            output = os.getcwd()

        case "cd":
            if not args:
                output = "cd: missing argument"
            elif len(args) == 1:
                if args[0] == "~":
                    home = os.environ.get("HOME")
                    if home:
                        os.chdir(home)
                    else:
                        output = "cd: HOME not set"
                elif os.path.isdir(args[0]):
                    try:
                        os.chdir(args[0])
                        output = ""
                    except Exception as e:
                        output = f"cd: {e}"
                else:
                    output = f"cd: {args[0]}: No such file or directory"
            else:
                output = f"cd: {' '.join(args)}: Invalid path."
                
        case "exit":
            sys.exit(0)

    if redirect and file:
        with open(file, "w") as f:
            f.write(output + "\n")
    else:
        print(output if output else "")
        
def handle_external(parsed_input):
    cmd = parsed_input["cmd"]
    args = parsed_input["args"]
    redirect = parsed_input["redirect"]
    file = parsed_input["file"]

    try:
        if redirect:
            if not file:
                print(f"Redirection operator used, but no file specified")
            else:
                with open(file, "w") as f:
                    subprocess.run([cmd] + args, stdout=f)
        else:
            subprocess.run([cmd] + args)
    except FileNotFoundError:
        print(f"{cmd}: command not found")

def prompt():
    sys.stdout.write("$ ")
    sys.stdout.flush()
        
def main():
    while True:
        prompt()

        #wait for user input
        # try:
        #     user_input = input().strip()           #strip to avoid errors with extra whitespaces (e.g " echo hello", "echo hello ")
        # except EOFError:                        #CTRL-D (exit shell)
        #     print("BYE BYE")
        #     break
        # except KeyboardInterrupt:               #CTRL-C 
        #     print("")
        #     continue
        try:
            user_input = sys.stdin.readline()
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
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
