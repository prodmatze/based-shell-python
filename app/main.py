import sys

def parse_command(input):
    split_input = input.split(" ", 1)
    command = split_input[0]

    return command

def main():
    

    while True:
        sys.stdout.write("$ ")
        #wait for user input
        u_input = input()
        command = parse_command(u_input)

        error_msg = f"{u_input}: command not found"

        if command == "exit":
            break

        print(error_msg)


if __name__ == "__main__":
    main()
