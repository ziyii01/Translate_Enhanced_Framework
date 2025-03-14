import os
import locale
import codecs

import chardet

from TEF_log import log


class Sub:
    # must exist
    path: str
    prefix: str
    lang: str | None
    suffix: str

    # generate
    pathname: str

    encoding: str | None
    text: str

    def splice_pathname(self):
        if self.lang is None:
            _tuple = (os.path.join(self.path, self.prefix), self.suffix)
        else:
            _tuple = (os.path.join(self.path, self.prefix), self.lang, self.suffix)
        self.pathname = ".".join(_tuple)

    def split_pathname(self):
        self.path, filename = os.path.split(self.pathname)

        last_dot_index = filename.rfind(".")
        self.suffix = filename[last_dot_index + 1 :]

        try:
            second_last_dot_index = filename.rindex(".", 0, last_dot_index)
        except:  # noqa: E722
            second_last_dot_index = None

        if second_last_dot_index:
            self.prefix = filename[:second_last_dot_index]
            self.lang = filename[second_last_dot_index + 1 : last_dot_index]
        else:
            self.prefix = filename[:last_dot_index]
            self.lang = None

    def get_encoding(self):
        with open(self.pathname, "rb") as file:
            text_data = file.read()
            encoding = chardet.detect(text_data)["encoding"]

        if encoding is None:
            log.warning(
                f'Can not find the encoding from "{self.pathname}", auto use UTF-8'
            )
            return "utf8"

        if encoding == "GB2312" or encoding == "cp936":
            encoding = "gb18030-2000"

        elif not (encoding.startswith("UTF") or encoding.startswith("utf")):
            locale_encoding = locale.getencoding()
            log.warning(
                f"Auto find the encoding is {encoding}, it may be {locale_encoding} ({codecs.lookup(locale_encoding).name}), has been auto changed it"
            )
            encoding = locale_encoding

        log.info(
            f"Auto find the encoding is {encoding} ({codecs.lookup(encoding).name})"
        )

        self.encoding = encoding

    def get_text(self):
        if not self.encoding:
            raise Exception(
                "A Sub obj is missing the member var 'encoding': Sub.get_text"
            )

        if os.path.exists(self.pathname):
            try:
                with open(self.pathname, "rt", encoding=self.encoding) as file:
                    self.text = file.read()
            except UnicodeDecodeError:
                log.error(
                    f'The encoding "{self.encoding}" is not correct, try UTF-8 instead'
                )
                with open(self.pathname, "rt", encoding="utf-8") as file:
                    self.text = file.read()
        else:
            log.error(f'The input file "{self.pathname}" is not exist')
            self.text = ""

    def __init__(self, **vars):
        if "pathname" in vars:
            self.pathname = vars["pathname"]
            self.split_pathname()

        elif (
            "path" in vars and "prefix" in vars and "lang" in vars and "suffix" in vars
        ):
            self.path = vars["path"]
            self.prefix = vars["prefix"]
            self.lang = vars["lang"]
            self.suffix = vars["suffix"]
            self.splice_pathname()

        else:
            raise Exception("This Sub obj init error, obj has been corrupted")

        log.info(f"Creating new Sub obj: pathname: {self.pathname}")

        if "encoding" in vars:
            self.encoding = vars["encoding"]
        else:
            self.get_encoding()

        if "text" in vars:
            self.text = vars["text"]
        else:
            self.get_text()

    # ==
    def __eq__(self, other):
        if isinstance(other, Sub):
            return self.pathname == other.pathname
        return NotImplemented

    # <
    def __lt__(self, other):
        if isinstance(other, Sub):
            return self.pathname < other.pathname
        return NotImplemented

    # <=
    def __le__(self, other):
        return self < other or self == other

    # >
    def __gt__(self, other):
        return not self <= other

    # >=
    def __ge__(self, other):
        return not self < other

    # !=
    def __ne__(self, other):
        return not self == other

    def overwrite_file(self) -> None:
        if os.path.exists(self.pathname):
            log.warning(
                f'The output file "{self.pathname}" already exists, auto overwrite it'
            )

        with open(self.pathname, "wt", encoding=self.encoding) as file:
            file.write(self.text)
