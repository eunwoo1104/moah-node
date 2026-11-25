from typing import Any, NotRequired, Optional, TypedDict

JSONType = dict[str, Any] | list | str | int


class MoahResponse(TypedDict):
    code: str
    msg: NotRequired[str]
    content: NotRequired[JSONType]


def create_response(
    code: str, msg: Optional[str] = None, content: Optional[JSONType] = None
) -> MoahResponse:
    resp: MoahResponse = {
        "code": code,
    }
    if msg is not None:
        resp["msg"] = msg
    if content is not None:
        resp["content"] = content
    return resp
