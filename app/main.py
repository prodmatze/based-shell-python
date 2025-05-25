from os.path import isfile
import sys
import os
import subprocess
import shlex

builtin_commands = ["echo", "exit", "type", "pwd", "cd"]
cwd = os.getcwd()

def parse_input(user_input):
    tokens = shlex.split(user_input)
    
    if not tokens:
        return None, []

    cmd = tokens[0]
    args = tokens[1:]

    return cmd, args

def find_executable(cmd):
    paths = os.environ.get("PATH", "").split(":")
    for path in paths:
        candidate = os.path.join(path, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None

def handle_builtin(cmd, args, curr_dir):
    match cmd:
        case "echo":
            print(" ".join(args))

        case "type":
            if not args[0]:
                print(f"{cmd}: missing argument")
            for arg in args:

                if arg in builtin_commands:
                    print(f"{args[0]} is a shell builtin")
                    break

                executable = find_executable(arg)
                if executable:
                    print(f"{arg} is {executable}")

                else:
                    print(f"{arg}: not found")

        case "pwd":
            print(curr_dir)

        case "cd":
            if len(args) <= 1:
                if os.path.isdir(args[0]):
                    curr_dir = args[0]
                else:
                    print(f"cd: {args[0]}: No such file or directory")
            else:
                print(f"cd: {' '.join(args)}: Invalid path.")
                
        case "exit":
            sys.exit(0)
        
    return curr_dir


def main():
    cwd = os.getcwd()
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

        cmd, args = parse_input(user_input)
        error_msg = f"{cmd}: command not found"

        #handle empty input -> continue to next iteration if user just presses enter with no input
        if cmd == "":
            continue

        if cmd in builtin_commands:
            cwd = handle_builtin(cmd, args, cwd)
        else:
            executable = find_executable(cmd)
            if executable:
                subprocess.call([cmd] + args)
            else:
                print(error_msg)


if __name__ == "__main__":
    main()
