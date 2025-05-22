from os.path import isfile
import sys
import os

builtin_commands = ["echo", "exit", "type"]

def parse_input(input):
    split_input = input.split(" ", 1)
    command = split_input[0]

    if len(split_input) > 1:
        param = split_input[1] 
    else:
        param = None

    return command, param

def find_executable(cmd):
    paths = os.environ.get("PATH", "").split(":")
    for path in paths:
        candidate = os.path.join(path, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None

def main():
    while True:
        sys.stdout.write("$ ")

        #wait for user input
        try:
            u_input = input().strip()           #strip to avoid errors with extra whitespaces (e.g " echo hello", "echo hello ")
        except EOFError:                        #CTRL-D (exit shell)
            print("BYE BYE")
            break
        except KeyboardInterrupt:               #CTRL-C 
            print("")
            continue

        command, argument = parse_input(u_input)
        error_msg = f"{command}: command not found"

        #handle empty input -> continue to next iteration if user just presses enter with no input
        if command == "":
            continue

        match command:
            case "echo":
                print(argument)

            case "type":
                if not argument:
                    print(f"{command}: missing argument")
                    continue

                if argument in builtin_commands:
                    print(f"{argument} is a shell builtin")
                else:
                    result = find_executable(argument)
                    if result:
                        print(f"{argument} is {result}")
                    else:
                        print(f"{argument}: not found")

            case "exit":
                break

            case _:
                print(error_msg)


if __name__ == "__main__":
    main()
