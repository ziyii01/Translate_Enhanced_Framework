import copy

import httpx

from TEF_log import log
from TEF_sub import Sub


FHJ_API_URL = "https://api.zhconvert.org"

class Tr:

    dir_path: str
    current_sub_list: list[Sub]

    @staticmethod
    def fhj_convert(
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
    def translate(sub: Sub, converter: str) -> Sub | None:

        response = Tr.fhj_convert(sub.text, converter)
        if response.status_code != 200:
            log.error(f"网址请求失败: {response.text}")
            return None

        response_json_data = response.json()
        if response_json_data["code"] != 0:
            log.error(f"繁化姬接口失败: {response_json_data['msg']}")
            return None

        else:
            new_sub = copy.deepcopy(sub)

            new_sub.lang = Tr.find_langTag_by_converter(converter)
            new_sub.splice_pathname()

            new_sub.text = response_json_data["data"]["text"]
            
            

            return new_sub


    @staticmethod
    def tr_and_overwrite(sub: Sub, converter: str, encoding: str = 'utf_8_sig') -> None:

        output_sub = Tr.translate(sub, converter)

        output_sub.encoding = encoding
        output_sub.overwrite_file()

        log.info(f'Translate the file "{sub.pathname}" to "{output_sub.pathname}" success')