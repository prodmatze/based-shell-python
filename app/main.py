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

def main():


    paths = os.environ.get("PATH", "").split(":")

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

        command, param = parse_input(u_input)
        error_msg = f"{command}: command not found"

        #handle empty input -> continue to next iteration if user just presses enter with no input
        if command == "":
            continue

        match command:
            case "echo":
                print(param)

            case "type":
                if paths:
                    for path in paths:
                        if os.path.isfile(path) and os.access(path, os.X_OK):
                            print(f"{param} is {path}")
                            continue
                        else:
                            print(f"{param}: not found")
                            continue

                if param in builtin_commands:
                    print(f"{param} is a shell builtin")
                else:
                    print(f"{param}: not found")

            case "exit":
                break

            case _:
                print(error_msg)



if __name__ == "__main__":
    main()
