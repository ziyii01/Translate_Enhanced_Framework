import os
import sys


from TEF_log import log
from TEF_sub import Sub
from TEF_tr import Tr


PROJECT_NAME = "Translate Enhanced Framework"
PROJECT_VERSION = "0.4.1"
PROJECT_URL = "https://github.com/ziyii01/use_zhconvert"


def get_all_sub_path(dir_path: str) -> list[Sub]:
    """
    Input a path, search all subtitles paths
    """
    return [
        Sub(pathname=os.path.join(dir_path, filename))
        for filename in os.listdir(dir_path)
        if filename.endswith((".ass", ".srt", ".ssa"))
    ]


def run_command(command: str):
    
    command = command.lower().strip()

    if command == "help":
        print(
            f"{PROJECT_NAME}\nVersion: {PROJECT_VERSION}\n{PROJECT_URL}\n"
            "\n"
            "Help:\n"
            "  You can input command or use the argument value to run\n"
            "\n"
            "Commands:\n"
            "  exit\n"
            "    Exit this program\n"
            "  list\n"
            "    Show found list\n"
            "  flush\n"
            "    Search the list again\n"
            "  tr all / translate all\n"
            "    Translate all zh-Hans ass to zh-Hant\n"
            "  cd <string>\n"
            "    Change current path\n"
            "  cls / clear\n"
            "    Clear screen\n"
            "  $ <string>\n"
            "    Execute the code string directly after the $\n"
            '    The string "\\N" will be changed to real "\\n"\n'
            "  <string>\n"
            "    Translate a file with matching prefixe (e.g. ep num) into zh-Hant\n"
        )

    elif command == "exit":
        sys.exit()
    
    elif command == "list":
        show_list(Tr.current_sub_list, "All ASS files")
        show_list(
            (sub for sub in Tr.current_sub_list
             if sub.lang == "zh-Hans" and sub.suffix == "ass"),
            "All zh-Hans ASS files"
        )

    elif command == "flush":
        Tr.current_sub_list = get_all_sub_path(Tr.dir_path)

    elif command == "tr all" or command == "translate all":
        for pathname in (sub.pathname for sub in Tr.current_sub_list
                         if sub.lang == "zh-Hans" and sub.suffix == "ass"):
            Tr.translate(pathname, 'Traditional')

    elif command[:2] == "cd":
        new_path = command.replace("cd","").strip()
        if os.path.isdir(new_path):
            os.chdir(new_path)
            Tr.dir_path = os.getcwd()
        else:
            log.error(f'The path "{new_path}" has error')

    elif command == "cls" or command == "clear":
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    elif command[0] == '$':
        try:
            exec(command[1:].lstrip().replace(r"\N","\n"))
        except Exception as e:
            log.error("Your input command has error:")
            print(repr(e))

    else:
        pathname = command + ".zh-Hans.ass"
        if os.path.exists(pathname):
            Tr.translate(pathname, 'Traditional')
        else:
            log.warning(f'Can not find the file "{pathname}", cancel the translation')


if __name__ == "__main__":
    
    Tr.dir_path = os.getcwd()
    Tr.current_sub_list = get_all_sub_path(Tr.dir_path)

    # def get_zh_hans_ass_list():
    #     all_ass_list = get_all_ass_path(dir_path)
    #     zh_hans_ass_list = match_suffix_in_list(all_ass_list, ".zh-Hans.ass")
    #     return all_ass_list, zh_hans_ass_list
    
    def show_list(list: list[Sub] | tuple[Sub], list_name: str):
        print(f'{list_name}:')
        for sub in list:
            print(f'  {sub.pathname}')

    
    # all_ass_list, zh_hans_ass_list = get_zh_hans_ass_list()
    
    for argv in sys.argv[1:]:
        run_command(argv)

    while True:
        try:
            command = input(f'{Tr.dir_path}> TEF command>')
        except:
            log.info("Manually force exit")
            sys.exit()
        run_command(command)
