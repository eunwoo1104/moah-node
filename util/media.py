import uuid
from os import getenv, path, remove


class MediaSaveHandler:
    save_dir: str = getenv("MEDIA_DIR") or "media"

    def __init__(self, content: bytes, extension: str):
        self.__safe: bool = False
        self.__saved: bool = False
        self.__content: bytes = content
        self.__extension: str = extension
        self.__dir: str = ""

    def __enter__(self):
        tries = 0
        while not self.__dir or path.exists(f"{self.save_dir}/{self.__dir}"):
            self.__dir = uuid.uuid4().hex + "." + self.__extension
            tries += 1
            if tries > 10:
                break

        if tries > 10:
            # TODO: better exception
            raise Exception("Retry later")

        with open(f"{self.save_dir}/{self.__dir}", "wb") as f:
            f.write(self.__content)

        self.__saved = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.unmark_safe()

        if not self.__safe:
            remove(f"{self.save_dir}/{self.__dir}")

    def mark_safe(self) -> None:
        self.__safe = True

    def unmark_safe(self) -> None:
        self.__safe = False

    @property
    def safe(self) -> bool:
        return self.__safe

    @property
    def saved(self) -> bool:
        return self.__saved

    @property
    def dir(self) -> str:
        return self.__dir
