import os
import shlex
import sys
from typing import Generator


from TEF_log import log
from TEF_sub import Sub
from TEF_tr import Tr


PROJECT_NAME = "Translate Enhanced Framework"
PROJECT_VERSION = "1.1"
PROJECT_URL = "https://github.com/ziyii01/use_zhconvert"


def get_all_sub_path(dir: str) -> list[Sub]:
    """
    Input a dir, search all subtitles paths
    """
    return [
        Sub(pathname=os.path.join(dir, filename))
        for filename in os.listdir(dir)
        if filename.endswith((".ass", ".srt", ".ssa"))
    ]


def run_command(command: list[str] | str):
    if isinstance(command, list):
        cmd_list = command

    elif isinstance(command, str):
        try:
            cmd_list = [
                cmd.strip('"').strip("'").replace("\\\\", "\\")
                for cmd in shlex.split(command, posix=False)
            ]
        except ValueError as e:
            log.error(e)
            return False

    cmd_list.append("")

    match cmd_list[0]:
        case "v" | "ver" | "version":
            print(f"{PROJECT_NAME} {PROJECT_VERSION}")

        case "h" | "help":
            print(
                f"{PROJECT_NAME}\nVersion: {PROJECT_VERSION}\n{PROJECT_URL}\n"
                "\n"
                "\n"
                "Help:\n"
                "  You can input command or use the argument value to run\n"
                "\n"
                "\n"
                "Commands:\n"
                "  v / ver / version\n"
                "    Show version\n"
                "\n"
                "  h / help\n"
                "    Show help\n"
                "\n"
                "  exit\n"
                "    Exit this program\n"
                "\n"
                "  list\n"
                "    Show found list\n"
                "\n"
                "  flush\n"
                "    Search the list again\n"
                "\n"
                "  tr / translate <options>\n"
                "    options:\n"
                "      all [<find lang> [<target lang>]]:\n"
                "        Translate all zh-Hans ass to zh-Hant\n"
                "        Or Specify language\n"
                "        e.g. tr all zh-Hans zh-Hant\n"
                "      <file pathname> <target lang>:\n"
                "        Translate the file\n"
                "\n"
                "  cd <string>\n"
                "    Change current path\n"
                "\n"
                "  cls / clear\n"
                "    Clear screen\n"
                "\n"
                "  $ <string>\n"
                "    Execute the code string directly after the $\n"
                '    The string "\\N" will be changed to real "\\n"\n'
                "\n"
                "  <string>\n"
                "    Translate a file with matching prefixe (e.g. ep num) into zh-Hant\n"
            )

        case "exit":
            sys.exit()

        case "list":
            show_list(Tr.current_sub_list, "All ASS files")
            show_list(
                (
                    sub
                    for sub in Tr.current_sub_list
                    if sub.lang == "zh-Hans" and sub.suffix == "ass"
                ),
                "All zh-Hans ASS files",
            )

        case "flush":
            Tr.current_sub_list = get_all_sub_path(Tr.dir_path)

        case "cd":
            new_path = cmd_list[1]
            if os.path.isdir(new_path):
                os.chdir(new_path)
                Tr.dir_path = os.getcwd()
                Tr.current_sub_list = get_all_sub_path(Tr.dir_path)
            else:
                log.error(f'The path "{new_path}" has error')

        case "cls" | "clear":
            if os.name == "nt":
                os.system("cls")
            else:
                os.system("clear")

        case str() as s if len(s.rstrip()) > 0 and s.rstrip()[0] == "$":
            try:
                exec(" ".join(cmd_list)[1:].lstrip().replace(r"\N", "\n"))
            except Exception as e:
                log.error(f"Your input command has error:\n{e}")

        case "tr" | "translate":
            match cmd_list[1]:
                case "all":
                    if not cmd_list[2]:
                        find_lang = Tr.LangTag.zh_Hans
                        target_lang = Tr.LangTag.zh_Hant
                    else:
                        try:
                            find_lang = Tr.LangTag(cmd_list[2])
                            target_lang = (
                                Tr.LangTag.zh_Hant
                                if not cmd_list[3]
                                else Tr.LangTag(cmd_list[3])
                            )
                        except Exception as e:
                            log.error(e)
                            return False

                    progress = 1
                    sub_run_tuple = tuple(
                        sub
                        for sub in Tr.current_sub_list
                        if sub.lang == find_lang.value and sub.suffix == "ass"
                    )
                    for sub in sub_run_tuple:
                        log.info(
                            f"Translate all ({find_lang.value} -> {target_lang.value}) ass: {progress} / {len(sub_run_tuple)} ..."
                        )
                        Tr.tr_and_overwrite(sub, target_lang)
                        progress = progress + 1

                case _:
                    if not cmd_list[1]:
                        log.error("File pathname is empty")
                        return False
                    if not os.path.exists(cmd_list[1]):
                        log.error(f"File {cmd_list[1]} not exist")
                        return False
                    if not (target_lang := cmd_list[2]):
                        log.error("Need target lang")
                        return False

                    try:
                        sub = Sub(pathname=cmd_list[1])
                        Tr.tr_and_overwrite(sub, Tr.LangTag(cmd_list[2]))

                    except Exception as e:
                        log.error(f"{cmd_list[1]} -> '{cmd_list[2]}' failed: {e}")

        case _:
            try:
                sub = list(
                    filter(
                        lambda sub: sub.prefix == cmd_list[0]
                        and sub.lang == "zh-Hans"
                        and sub.suffix == "ass",
                        Tr.current_sub_list,
                    )
                )[0]
                if os.path.exists(sub.pathname):
                    log.info(f'Translate "{sub.pathname}"')
                    Tr.tr_and_overwrite(sub, Tr.LangTag.zh_Hant)
                else:
                    log.warning(
                        f'Can not find the file "{sub.pathname}", cancel the translation'
                    )

            except Exception as e:
                log.error(f"{cmd_list[0]}.zh-Hans.ass -> 'zh-Hant' failed: {e}")

    return True


if __name__ == "__main__":
    Tr.dir_path = os.getcwd()
    Tr.current_sub_list = get_all_sub_path(Tr.dir_path)

    def show_list(list: list[Sub] | tuple[Sub] | Generator[Sub], list_name: str):
        print(f"{list_name}:")
        for sub in list:
            print(f"  {sub.pathname} ({sub.encoding})")

    if len(sys.argv) > 1:
        run_command(sys.argv[1:])
        sys.exit()

    while True:
        try:
            command = input(f"{Tr.dir_path}> TEF command>")
        except:  # noqa: E722
            log.info("Manually force exit")
            sys.exit()

        if not run_command(command):
            log.warning("Stop run command")
