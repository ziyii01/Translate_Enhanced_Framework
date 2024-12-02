import os

import chardet
import httpx
from loguru import logger as log

URL_ROOT = "https://api.zhconvert.org"


def current_running_path() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_all_zh_hans_ass_files_in_current_path() -> list[str]:
    return [
        os.path.join(current_running_path(), f)
        for f in os.listdir(current_running_path())
        if f.endswith(".zh-Hans.ass")
    ]


class Zhconvert:
    @staticmethod
    def convert(
        api,
        text,
        converter="Traditional",
        apiKey="",
        outputFormat="json",
        prettify="false",
    ) -> httpx.Response:
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


if __name__ == "__main__":
    while True:
        episode_number: str = input("请输入你要的集数: ")
        for file_name in get_all_zh_hans_ass_files_in_current_path():
            # 判断是否是当前集数
            if file_name.endswith(f"{episode_number}.zh-Hans.ass"):
                log.info(f"正在处理文件: {file_name}")
                # 读取ass二进制，用于判断文字编码
                with open(f"{file_name}", "rb") as f:
                    text_data = f.read()
                    encoding = chardet.detect(text_data)["encoding"]
                # 判断文字编码是否正确
                while True:
                    if (
                        encoding_input := input(
                            f"当前的文字编码识别为{encoding}，正确请回车，不正确请输入文字编码: "
                        )
                    ) != "":
                        encoding = encoding_input
                    else:
                        break
                # 读取ass文件内容
                with open(f"{file_name}", "r", encoding="utf-8") as f:
                    text_data = f.read()
                # 调用繁化姬接口
                response = Zhconvert.convert("/convert", text_data)
                if response.status_code != 200:
                    log.error(f"网址请求失败: {response.text}")
                    continue
                Response_json_data = response.json()
                if Response_json_data["code"] != 0:
                    log.error(f"繁化姬接口失败: {Response_json_data['msg']}")
                else:
                    # 写入文件
                    with open(
                        f"{episode_number.zfill(2)}.zh-Hant.ass",
                        "w",
                        encoding=encoding,
                    ) as f:
                        f.write(Response_json_data["data"]["text"])
                    log.info(f"文件: {file_name} 处理完成")
