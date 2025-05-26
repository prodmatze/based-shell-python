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

    if ">" or "1>" in tokens:
        if ">" in tokens:
            index = tokens.index(">")
            result["operator"] = ">"
        else:
            index = tokens.index("1>")
            result["operator"] = "1>"

        result["args"] = tokens[1:index]
        result["file"] = tokens[index+1] if len(tokens) > index + 1 else None
        result["redirect"] = True
    else:
        result["args"] = tokens[1:]

    return result

def check_operators(args):
    hit_operator = False
    pre_args = []
    post_args = []
    operator = None

    for arg in args:
        if hit_operator == False:
            if arg in builtin_operators:
                operator = arg
                hit_operator = True
            pre_args.append(arg)
        else:
            post_args.append(arg)

    return pre_args, post_args, operator

def handle_operator(args):
    active_operator = None

    for operator in builtin_operators:
        if operator in args:
            active_operator = operator 
        else:
            return [], [], None

    split_args = args.split(active_operator)

    return split_args[0], split_args[1], active_operator

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
            if not args:
                output = f"{cmd}: missing argument"

            for arg in args:
                if arg in builtin_commands:
                    output = f"{arg} is a shell builtin"
                else:
                    executable = find_executable(arg)
                    if executable:
                        output = f"{arg} is {executable}"
                    else:
                        output = f"{arg}: not found"

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
        print(output)
        
def handle_external(parsed_input):
    cmd = parsed_input["cmd"]
    args = parsed_input["args"]
    redirect = parsed_input["redirect"]
    file = parsed_input["file"]

    try:
        if redirect and file:
            with open(file, "w") as f:
                subprocess.run([cmd] + args, stdout=f)
        else:
            subprocess.run([cmd] + args)
    except FileNotFoundError:
        print(f"{cmd}: command not found")

        
def main():
    while True:
        sys.stdout.write("$ ")

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
        args = parsed_input.get("args", None)
        redirect = parsed_input.get("redirect", False)
        operator = parsed_input.get("operator", None)
        file = parsed_input.get("file", None)

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
