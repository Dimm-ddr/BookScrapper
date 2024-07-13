from typing import Any, TypedDict, TypeGuard, NotRequired
from .notion_constants import NotionBlockType


class BlockContent(TypedDict, total=False):
    text: list[dict[str, Any]]
    checked: bool
    color: str
    icon: dict[str, Any]
    children: list[Any]
    title: list[dict[str, Any]]
    properties: dict[str, Any]
    id: str


class NotionBlock(TypedDict):
    id: str
    type: NotionBlockType
    has_children: NotRequired[bool]
    content: dict[NotionBlockType, BlockContent]


class NotionPage(TypedDict):
    id: str
    properties: dict[str, Any]


class NotionDatabasePage(TypedDict):
    id: str
    properties: dict[str, Any]


class NotionDatabase(TypedDict):
    id: str
    title: list[dict[str, Any]]
    properties: dict[str, Any]


class NotionListResponse(TypedDict):
    results: list[NotionBlock | NotionDatabasePage]
    has_more: bool
    next_cursor: NotRequired[str | None]


def is_notion_page(obj: Any) -> TypeGuard[NotionPage]:
    return isinstance(obj, dict) and "id" in obj and "properties" in obj


def is_notion_database(obj: Any) -> TypeGuard[NotionDatabase]:
    return isinstance(obj, dict) and "id" in obj and "properties" in obj


def is_notion_list_response(obj: Any) -> TypeGuard[NotionListResponse]:
    return isinstance(obj, dict) and "results" in obj and "has_more" in obj


def is_notion_database_page(obj: Any) -> TypeGuard[NotionDatabasePage]:
    return isinstance(obj, dict) and "id" in obj and "properties" in obj


def is_notion_block(obj: Any) -> TypeGuard[NotionBlock]:
    return (
        isinstance(obj, dict)
        and "id" in obj
        and "type" in obj
        and isinstance(obj["type"], NotionBlockType)
        and "content" in obj
        and isinstance(obj["content"], dict)
        and all(isinstance(k, NotionBlockType) for k in obj["content"])
    )
