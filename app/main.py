import sys

def parse_input(input):
    split_input = input.split(" ", 1)
    command = split_input[0]

    if len(split_input) > 1:
        param = split_input[1] 
    else:
        param = None

    return command, param

def main():
    

    while True:
        sys.stdout.write("$ ")
        #wait for user input
        u_input = input()
        command, param = parse_input(u_input)

        error_msg = f"{u_input}: command not found"

        match command:
            case "echo":
                print(param)
            case "exit":
                break
            case _:
                print(error_msg)



if __name__ == "__main__":
    main()
