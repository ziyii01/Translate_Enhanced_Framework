import copy
import enum

import httpx

from TEF_log import log
from TEF_sub import Sub


FHJ_API_URL = "https://api.zhconvert.org"


class Tr:
    dir_path: str
    current_sub_list: list[Sub]

    class LangTag(enum.Enum):
        Unknow = "Unknow"
        zh_Hans = "zh-Hans"
        zh_Hans_CN = "zh-Hans-CN"
        zh_Hant = "zh-Hant"
        zh_Hant_HK = "zh-Hant-HK"
        zh_Hant_TW = "zh-Hant-TW"

    class FhjConverter(enum.Enum):
        Simplified = "Simplified"
        Traditional = "Traditional"
        China = "China"
        Hongkong = "Hongkong"
        Taiwan = "Taiwan"
        Pinyin = "Pinyin"  # 拼音化
        Bopomofo = "Bopomofo"  # 注音化
        Mars = "Mars"  # 火星化
        WikiSimplified = "WikiSimplified"  # 維基簡體化
        WikiTraditional = "WikiTraditional"  # 維基繁體化

    @staticmethod
    def fhj_get_res(
        text: str,
        langTag: LangTag,
        apiKey="",
        outputFormat="json",
        prettify="false",
    ) -> httpx.Response | None:
        match langTag:
            case Tr.LangTag.zh_Hans:
                converter = Tr.FhjConverter.Simplified

            case Tr.LangTag.zh_Hans_CN:
                converter = Tr.FhjConverter.China

            case Tr.LangTag.zh_Hant:
                converter = Tr.FhjConverter.Traditional

            case Tr.LangTag.zh_Hant_HK:
                converter = Tr.FhjConverter.Hongkong

            case Tr.LangTag.zh_Hant_TW:
                converter = Tr.FhjConverter.Taiwan

            case _:
                converter = Tr.LangTag.Unknow

        response = None
        TIMEOUT_MAX_TIME = 3
        for time in range(1, TIMEOUT_MAX_TIME + 1):
            timeout_global = 5 + time * 2
            timeout_read = 20 * time**2
            try:
                response = httpx.post(
                    FHJ_API_URL + "/convert",
                    data={
                        "text": text,
                        "converter": converter.value,
                        "apiKey": apiKey,
                        "outputFormat": outputFormat,
                        "prettify": prettify,
                    },
                    timeout=httpx.Timeout(timeout_global, read=timeout_read),
                )
                break
            except httpx.ConnectTimeout:
                log.error(
                    f"Tr.convert httpx.ConnectTimeout, trying to reconnect. Times of reconnect: {time}. Remaining reconnect times: {TIMEOUT_MAX_TIME - time}. {timeout_global=}, {timeout_read=}"
                )
            except httpx.ReadTimeout:
                log.error(
                    f"Tr.convert httpx.ReadTimeout, trying to reconnect. Times of reconnect: {time}. Remaining reconnect times: {TIMEOUT_MAX_TIME - time}. {timeout_global=}, {timeout_read=}"
                )

        return response

    @staticmethod
    def translate(sub: Sub, lang_tag: LangTag) -> Sub | None:
        response = Tr.fhj_get_res(sub.text, lang_tag)

        if response is None:
            log.error("翻译失败")
            return None

        if response.status_code != 200:
            log.error(f"网址请求失败: {response.text}")
            return None

        response_json_data = response.json()
        if response_json_data["code"] != 0:
            log.error(f"繁化姬接口失败: {response_json_data['msg']}")
            return None

        else:
            new_sub = copy.deepcopy(sub)

            new_sub.lang = lang_tag.value
            new_sub.splice_pathname()

            new_sub.text = response_json_data["data"]["text"]

            return new_sub

    @staticmethod
    def tr_and_overwrite(
        sub: Sub, target_lang_tag: LangTag, encoding: str = "utf_8_sig"
    ):
        if (output_sub := Tr.translate(sub, target_lang_tag)) is None:
            log.error("Translate failed")
            return None

        output_sub.encoding = encoding
        output_sub.overwrite_file()

        log.info(
            f'Translate success: ({sub.lang} -> {target_lang_tag.value}) ("{sub.pathname}" -> "{output_sub.pathname}")'
        )
