import os
import sys
import locale
import codecs

import chardet
import httpx
from loguru import logger as log
log.remove()
log.add(sys.stderr, format="<green>{time:YYYY.MM.DD HH:mm:ss.SS}</green><blue><level> [{level}] {message}</level></blue>", level="INFO")


URL_ROOT = "https://api.zhconvert.org"



def get_all_ass_path(dir_path: str) -> list[str]:
    return [
        os.path.join(dir_path, filename)
        for filename in os.listdir(dir_path)
        if filename.endswith(".ass")
    ]

def match_suffix_in_list(all_list: list[str], suffix: str) -> list[str]:
    return [
        pathname
        for pathname in all_list
        if pathname.endswith(suffix)
    ]

def get_encoding_by_text(pathname: str) -> str | None:
    with open(pathname, "rb") as file:
        text_data = file.read()
        encoding = chardet.detect(text_data)["encoding"]

    if encoding == None:
        log.warning(f'Can not find the encoding from "{pathname}", auto use UTF-8')
        return 'utf8'

    if encoding == 'GB2312' or encoding == 'cp936':
        encoding = 'gb18030-2000'
    
    if not encoding.startswith("UTF") and not encoding == 'gb18030-2000':
        locale_encoding = locale.getencoding()
        log.warning(f'Auto find the encoding is {encoding}, it may be {locale_encoding} ({codecs.lookup(locale_encoding).name}), has been auto changed it')
        encoding = locale_encoding
    
    log.info(f"Auto find the encoding is {encoding} ({codecs.lookup(encoding).name})")
    return encoding


class Zhconvert:
    @staticmethod
    def convert(
        text: str,
        converter: str,
        apiKey = "",
        outputFormat = "json",
        prettify = "false",
    ) -> httpx.Response:
        """
        converter:
        Simplified、 Traditional、 China、 Hongkong、 Taiwan、 Pinyin （拼音化） Bopomofo （注音化）、 Mars （火星化）、 WikiSimplified （維基簡體化）、 WikiTraditional （維基繁體化）
        """
        api = '/convert'
        return httpx.post(
            f"{URL_ROOT}/{api}",
            data={
                "text": text,
                "converter": converter,
                "apiKey": apiKey,
                "outputFormat": outputFormat,
                "prettify": prettify,
            },
        )
    
    @staticmethod
    def find_langTag_by_converter(converter: str) -> str | None:
        lang_tag: str | None = None

        if converter == "Simplified":
            lang_tag = "zh-Hans"
        elif converter == "Traditional":
            lang_tag = "zh-Hant"
        elif converter == "Hongkong":
            lang_tag = "zh-Hant-HK"
        elif converter == "Taiwan":
            lang_tag = "zh-Hant-TW"

        return lang_tag

    @staticmethod
    def translate(input_pathname: str, converter: str) -> bool:
        if not os.path.exists(input_pathname):
            log.error(f'The input file "{input_pathname}" is not exist')
            return False
        
        encoding = get_encoding_by_text(input_pathname)
        
        with open(input_pathname, "rt", encoding = encoding) as file:
            text_data = file.read()
        response = Zhconvert.convert(text_data, converter)
        if response.status_code != 200:
            log.error(f"网址请求失败: {response.text}")
            return False
        response_json_data = response.json()
        if response_json_data["code"] != 0:
            log.error(f"繁化姬接口失败: {response_json_data['msg']}")
            return False
        else:
            last_dot_index = input_pathname.rfind('.')
            second_last_dot_index = input_pathname.rindex('.', 0, last_dot_index)
            output_pathname = f'{input_pathname[:second_last_dot_index]}.{Zhconvert.find_langTag_by_converter(converter)}.ass'

            if os.path.exists(output_pathname):
                log.warning(f'The output file "{output_pathname}" already exists, auto overwrite it')

            with open(output_pathname, "wt", encoding = 'utf_8_sig') as file:
                file.write(response_json_data["data"]["text"])
            
            log.info(f'Translate the file "{input_pathname}" to "{output_pathname}" success')
            return True


def run_command(command: str):
    global dir_path, all_ass_list, zh_hans_ass_list
    
    command = command.lower().strip()

    if command == "help":
        print(
            "Help:\n"
            "  You can input command or use the argument value to run"
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
        exit()
    
    elif command == "list":
        show_list(all_ass_list, "All ASS files")
        show_list(zh_hans_ass_list, "All zh-Hans ASS files")

    elif command == "flush":
        all_ass_list, zh_hans_ass_list = get_zh_hans_ass_list()

    elif command == "tr all" or command == "translate all":
        for pathname in zh_hans_ass_list:
            Zhconvert.translate(pathname, 'Traditional')

    elif command[:2] == "cd":
        new_path = command.replace("cd","").strip()
        if os.path.isdir(new_path):
            os.chdir(new_path)
            dir_path = os.getcwd()
        else:
            log.error(f'The path "{new_path}" has error')

    elif command == "cls" or command == "clear":
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    elif command[0] == '$':
        exec(command[1:].lstrip().replace(r"\N","\n"))

    else:
        pathname = command + ".zh-Hans.ass"
        if os.path.exists(pathname):
            Zhconvert.translate(pathname, 'Traditional')
        else:
            log.warning(f'Can not find the file "{pathname}", cancel the translation')


if __name__ == "__main__":
    # get_encoding_by_text(r'c:\Users\op200\Documents\test\新建 文本文档.txt')

    dir_path = os.getcwd()

    def get_zh_hans_ass_list():
        all_ass_list = get_all_ass_path(dir_path)
        zh_hans_ass_list = match_suffix_in_list(all_ass_list, ".zh-Hans.ass")
        return all_ass_list, zh_hans_ass_list
    
    def show_list(list: list[str], list_name: str):
        print(f'{list_name}:')
        for str in list:
            print(f'  {str}')

    
    all_ass_list, zh_hans_ass_list = get_zh_hans_ass_list()
    
    for argv in sys.argv[1:]:
        run_command(argv)

    while True:
        run_command(input(f'{dir_path}> Input command>'))
