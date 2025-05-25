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

def handle_builtin(cmd, args):
    match cmd:
        case "echo":
            print(" ".join(args))

        case "type":
            if not args:
                print(f"{cmd}: missing argument")

            for arg in args:
                if arg in builtin_commands:
                    print(f"{arg} is a shell builtin")
                    break

                executable = find_executable(arg)
                if executable:
                    print(f"{arg} is {executable}")
                else:
                    print(f"{arg}: not found")

        case "pwd":
            print(os.getcwd())

        case "cd":
            if not args:
                print("cd: missing argument")
            elif len(args) == 1:
                if args[0] == "~":
                    os.chdir(os.environ.get("HOME", ""))
                elif os.path.isdir(args[0]):
                    try:
                        os.chdir(args[0])
                    except Exception as e:
                        print(f"cd: {e}")
                else:
                    print(f"cd: {args[0]}: No such file or directory")
            else:
                print(f"cd: {' '.join(args)}: Invalid path.")
                
        case "exit":
            sys.exit(0)
        
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

        cmd, args = parse_input(user_input)
        error_msg = f"{cmd}: command not found"

        #handle empty input -> continue to next iteration if user just presses enter with no input
        if cmd == "":
            continue

        if cmd in builtin_commands:
            handle_builtin(cmd, args)
        else:
            executable = find_executable(cmd)
            if executable:
                subprocess.call([cmd] + args)
            else:
                print(error_msg)


if __name__ == "__main__":
    main()
