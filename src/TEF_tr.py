import os
import locale
import codecs

import httpx
import chardet

from TEF_log import log
from TEF_sub import Sub



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



FHJ_API_URL = "https://api.zhconvert.org"

class Tr:

    dir_path:str
    current_sub_list: list[Sub]

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
        
        max_timeout_times = 3
        for time in range(1, max_timeout_times+1):
            try:
                response = httpx.post(
                    FHJ_API_URL+"/convert",
                    data={
                        "text": text,
                        "converter": converter,
                        "apiKey": apiKey,
                        "outputFormat": outputFormat,
                        "prettify": prettify,
                    }, 
                )
            except httpx.ConnectTimeout:
                log.error(f"Tr.convert Timeout, trying to reconnect. Times of reconnect: {time}. Remaining reconnect times: {max_timeout_times-time}.")

        return response
    
    @staticmethod
    def find_langTag_by_converter(converter: str) -> str:
        lang_tag: str = "Unknow"

        if converter == "Simplified":
            lang_tag = "zh-Hans"
        if converter == "China":
            lang_tag = "zh-Hans-CN"
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
        response = Tr.convert(text_data, converter)
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
            output_pathname = f'{input_pathname[:second_last_dot_index]}.{Tr.find_langTag_by_converter(converter)}.ass'

            if os.path.exists(output_pathname):
                log.warning(f'The output file "{output_pathname}" already exists, auto overwrite it')

            with open(output_pathname, "wt", encoding = 'utf_8_sig') as file:
                file.write(response_json_data["data"]["text"])
            
            log.info(f'Translate the file "{input_pathname}" to "{output_pathname}" success')
            return True
