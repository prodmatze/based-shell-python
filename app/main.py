import sys


def main():
    sys.stdout.write("$ ")
    
    #wait for user input
    u_input = input()

    error_msg = f"{u_input}: command not found"
    print(error_msg)

if __name__ == "__main__":
    main()
