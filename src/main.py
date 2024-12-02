import os

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
    episode_number: str = input("请输入你要的集数: ")
    for file_name in get_all_zh_hans_ass_files_in_current_path():
        # 判断是否是当前集数
        if file_name.endswith(f"{episode_number}.zh-Hans.ass"):
            log.info(f"正在处理文件: {file_name}")
            # 读取ass文件内容
            with open(f"{file_name}", "r", encoding="utf-8") as f:
                text_data = f.read()
            response = Zhconvert.convert("/convert", text_data)
            if response.status_code == 200:
                Response_json_data = response.json()
                with open(f"{episode_number:02}.zh-Hant.ass", "w", encoding="utf-8") as f:
                    f.write(Response_json_data["data"]["text"])
            else:
                log.error(f"请求失败: {response.text}")
