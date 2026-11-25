from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import MoAhNodeDB
    from .session import MediaUploadSessionManager


class MoAhNodeCTX(SimpleNamespace):
    database: "MoAhNodeDB"
    session: "MediaUploadSessionManager"
