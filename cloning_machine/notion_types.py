from typing import Any, TypedDict, TypeGuard, NotRequired, Union


class BlockContent(TypedDict, total=False):
    text: list[dict[str, Any]]
    checked: bool
    color: str
    icon: dict[str, Any]
    children: list[Any]
    title: list[dict[str, Any]]
    properties: dict[str, Any]
    id: str  # For database ID


class NotionBlock(TypedDict):
    id: str
    type: str
    has_children: NotRequired[bool]
    paragraph: NotRequired[BlockContent]
    heading_1: NotRequired[BlockContent]
    heading_2: NotRequired[BlockContent]
    heading_3: NotRequired[BlockContent]
    bulleted_list_item: NotRequired[BlockContent]
    numbered_list_item: NotRequired[BlockContent]
    to_do: NotRequired[BlockContent]
    toggle: NotRequired[BlockContent]
    child_page: NotRequired[BlockContent]
    child_database: NotRequired[BlockContent]
    embed: NotRequired[BlockContent]
    image: NotRequired[BlockContent]
    video: NotRequired[BlockContent]
    file: NotRequired[BlockContent]
    pdf: NotRequired[BlockContent]
    bookmark: NotRequired[BlockContent]
    callout: NotRequired[BlockContent]
    quote: NotRequired[BlockContent]
    equation: NotRequired[BlockContent]
    divider: NotRequired[BlockContent]
    table_of_contents: NotRequired[BlockContent]
    column: NotRequired[BlockContent]
    column_list: NotRequired[BlockContent]
    link_preview: NotRequired[BlockContent]
    synced_block: NotRequired[BlockContent]
    template: NotRequired[BlockContent]
    link_to_page: NotRequired[BlockContent]
    table: NotRequired[BlockContent]
    table_row: NotRequired[BlockContent]
    code: NotRequired[BlockContent]


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
    return isinstance(obj, dict) and "id" in obj and "type" in obj
