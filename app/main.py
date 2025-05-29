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

#3 default I/O Streams: stdin, stdout, stderr
#added std_info for misc prints/debugging
STD_IN = "stdin"
STD_OUT = "stdout"
STD_ERR = "stderr"
STD_INFO = "stdinfo"

#fallback for when stderr redirection is requested but there is no error
ERR_FALLBACK = "stderr_fallback"

def parse_input(user_input):
    tokens = shlex.split(user_input)
    if not tokens:
        return {}

    redirects = {}
    redirect_modes = {
        "stdout": "w",
        "stderr": "w"
    }
    args = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        #stdout redirection
        if token in [">", "1>", ">>", "1>>"]: 
            if i + 1 < len(tokens):
                redirects["stdout_file"] = tokens[i + 1]
                i += 2
                redirect_modes["stdout"] = "a" if token in [">>", "1>>"] else "w"
                continue
            else:
                print("Syntax error: expected filename after stdout redirection")
                return {}

        #stderr redirection
        elif token in ["2>", "2>>"]:
            if i + 1 < len(tokens):
                redirects["stderr_file"] = tokens[i + 1]
                i += 2
                redirect_modes["stderr"] = "a" if token == "2>>" else "w"
                continue
            else:
                print("Syntax error: expected filename after stderr redirection")
                return {}

        else:
            args.append(token)
            i += 1

    if not args:
        return {}

    return {
        "cmd": args[0],
        "args": args[1:],
        "redirects": redirects,
        "redirect_modes": redirect_modes
    }

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
    redirects = parsed_input["redirects"]
    redirect_modes = parsed_input.get("redirect_modes", {})

    outputs = []

    match cmd:
        case "echo":
            outputs.append((STD_OUT, " ".join(args)))

        case "type":
            if not args:
                outputs.append((STD_ERR, f"{cmd}: missing argument"))

            for arg in args:
                if arg in builtin_commands:
                    outputs.append((STD_OUT, f"{arg} is a shell builtin"))
                else:
                    executable = find_executable(arg)
                    if executable:
                        outputs.append((STD_OUT, f"{arg} is {executable}"))
                    else:
                        outputs.append((STD_ERR, f"{arg}: not found"))

        case "pwd":
            outputs.append((STD_OUT, os.getcwd()))

        case "cd":
            if not args:
                outputs.append((STD_ERR, "cd: missing argument"))
            elif len(args) == 1:
                if args[0] == "~":
                    home = os.environ.get("HOME")
                    if home:
                        os.chdir(home)
                    else:
                        outputs.append((STD_INFO, "cd: HOME not set"))
                elif os.path.isdir(args[0]):
                    try:
                        os.chdir(args[0])
                        #outputs.append((STD_OUT, ""))
                    except Exception as e:
                        outputs.append((STD_ERR, f"cd: {e}"))
                else:
                    outputs.append((STD_ERR, f"cd: {args[0]}: No such file or directory"))
            else:
                outputs.append((STD_ERR, f"cd: {' '.join(args)}: Invalid path."))
                
        case "exit":
            sys.exit(0)

    handle_outputs(outputs, redirects, redirect_modes)

    return None

def handle_outputs(outputs, redirects, redirect_modes):
    stdout_file = redirects.get("stdout_file")
    stderr_file = redirects.get("stderr_file")

    #open files only once, so a single stream doesnt overwrite file contents
    stdout_handle = open(stdout_file, redirect_modes.get("stdout", "w")) if stdout_file else None
    stderr_handle = open(stderr_file, redirect_modes.get("stderr", "w")) if stderr_file else None

    seen_stderr = False

    for stream, msg in outputs:
        if stream == STD_OUT:
            if stdout_handle:
                stdout_handle.write(msg + "\n")
            else:
                print(msg)

        elif stream == STD_ERR:
            seen_stderr = True
            if stderr_handle:
                stderr_handle.write(msg + "\n")
            else:
                print(msg)

    #fallback for when stderr redirection is requested but no error exists
    if stderr_file and not seen_stderr:
        stderr_handle.write("") if stderr_handle else None

    #cleanup/close file handlers
    if stdout_handle:
        stdout_handle.close()
    if stderr_handle:
        stderr_handle.close()

# def handle_outputs(outputs, redirects):
#     stdout_file = redirects.get("stdout_file", None)
#     stderr_file = redirects.get("stderr_file", None)
#     for stream, msg in outputs:
#         output = (stream, msg)
#         if stream == STD_OUT:
#             if stdout_file:
#                 handle_redirect(output, stdout_file)
#             else:
#                 print(msg)
#         if stream == STD_ERR:
#             if stderr_file:
#                 handle_redirect(output, stderr_file)
#             else:
#                 print(msg)
#     if stderr_file and STD_ERR not in (stream for stream, _ in outputs):
#         handle_redirect((ERR_FALLBACK, ""), stderr_file)
#
#     return None

def handle_redirect(output, out_file):
    stream, msg = output
    if stream == ERR_FALLBACK:
        with open(out_file, "w") as f:
            f.write(msg)  #no newline
    else:
        with open(out_file, "w") as f:
            f.write(msg + "\n")

    return None
        
def handle_external(parsed_input):
    cmd = parsed_input["cmd"]
    args = parsed_input["args"]
    redirects = parsed_input["redirects"]
    stdout_file = redirects.get("stdout_file")
    stderr_file = redirects.get("stderr_file")

    try:
        if stdout_file and stderr_file:
            with open(stdout_file, "w") as out, open(stderr_file, "w") as err:
                subprocess.run([cmd] + args, stdout=out, stderr=err)
        elif stdout_file:
            with open(stdout_file, "w") as out:
                subprocess.run([cmd] + args, stdout=out)
        elif stderr_file:
            with open(stderr_file, "w") as err:
                subprocess.run([cmd] + args, stderr=err)
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
