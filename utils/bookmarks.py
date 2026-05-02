"""论文收藏夹工具模块：管理 output/bookmarks.json 的读写操作。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

BOOKMARKS_PATH = _ROOT / "output" / "bookmarks.json"


def load_bookmarks() -> list[dict[str, Any]]:
    """加载收藏夹，返回论文列表。文件不存在时返回空列表。"""
    if not BOOKMARKS_PATH.exists():
        return []
    try:
        data = json.loads(BOOKMARKS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_bookmarks(bookmarks: list[dict[str, Any]]) -> None:
    """将收藏夹保存到 output/bookmarks.json。"""
    BOOKMARKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    BOOKMARKS_PATH.write_text(
        json.dumps(bookmarks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _paper_id(paper: dict[str, Any]) -> str:
    """生成论文唯一标识（优先使用 DOI，否则用标题）。"""
    return (paper.get("doi_url") or paper.get("title") or "").strip().lower()


def add_bookmark(paper: dict[str, Any]) -> bool:
    """添加论文到收藏夹。若已存在则跳过，返回是否实际添加。"""
    bookmarks = load_bookmarks()
    pid = _paper_id(paper)
    existing_ids = {_paper_id(b) for b in bookmarks}
    if pid in existing_ids:
        return False
    bookmarks.append(paper)
    save_bookmarks(bookmarks)
    return True


def remove_bookmark(paper_id: str) -> bool:
    """从收藏夹中移除指定论文（按 paper_id 匹配）。返回是否实际移除。"""
    bookmarks = load_bookmarks()
    original_len = len(bookmarks)
    bookmarks = [b for b in bookmarks if _paper_id(b) != paper_id.strip().lower()]
    if len(bookmarks) < original_len:
        save_bookmarks(bookmarks)
        return True
    return False


def is_bookmarked(paper: dict[str, Any]) -> bool:
    """检查论文是否已在收藏夹中。"""
    pid = _paper_id(paper)
    return any(_paper_id(b) == pid for b in load_bookmarks())


def _slugify(text: str) -> str:
    """将标题转换为 BibTeX key 友好的格式。"""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s-]+", "_", text.strip())
    return text[:40]


def _format_bibtex_authors(authors_str: str) -> str:
    """将逗号分隔的作者字符串转换为 BibTeX 格式（用 ' and ' 连接）。"""
    if not authors_str:
        return "Unknown"
    authors = [a.strip() for a in authors_str.split(",") if a.strip()]
    return " and ".join(authors)


def export_bibtex(bookmarks: list[dict[str, Any]]) -> str:
    """将收藏夹论文列表导出为 BibTeX 格式字符串。"""
    entries = []
    for i, paper in enumerate(bookmarks, 1):
        title = paper.get("title", "Untitled")
        authors_str = paper.get("authors", "")
        venue = paper.get("venue", "")
        pub_date = paper.get("published_date", "")
        doi_url = paper.get("doi_url", "")
        abstract = paper.get("abstract", "")

        # 提取年份
        year = pub_date[:4] if pub_date and len(pub_date) >= 4 else "0000"

        # 生成 BibTeX key：第一作者姓氏 + 年份 + 标题首词
        first_author = authors_str.split(",")[0].strip() if authors_str else "Unknown"
        last_name = first_author.split()[-1] if first_author.split() else "Unknown"
        title_word = _slugify(title.split()[0]) if title.split() else "paper"
        bib_key = f"{_slugify(last_name)}{year}_{title_word}_{i}"

        # 判断文献类型
        bib_type = "article"
        venue_lower = venue.lower()
        if any(x in venue_lower for x in ["working paper", "nber", "ssrn", "arxiv", "preprint"]):
            bib_type = "misc"

        lines = [f"@{bib_type}{{{bib_key},"]
        lines.append(f"  title     = {{{{{title}}}}},")
        lines.append(f"  author    = {{{_format_bibtex_authors(authors_str)}}},")
        if venue:
            field = "journal" if bib_type == "article" else "howpublished"
            lines.append(f"  {field:<9} = {{{venue}}},")
        if year != "0000":
            lines.append(f"  year      = {{{year}}},")
        if doi_url:
            lines.append(f"  doi       = {{{doi_url}}},")
            lines.append(f"  url       = {{{doi_url}}},")
        if abstract:
            # 截断过长的摘要，避免 BibTeX 文件过大
            short_abstract = abstract[:500] + ("..." if len(abstract) > 500 else "")
            lines.append(f"  abstract  = {{{short_abstract}}},")
        lines.append("}")
        entries.append("\n".join(lines))

    return "\n\n".join(entries)
