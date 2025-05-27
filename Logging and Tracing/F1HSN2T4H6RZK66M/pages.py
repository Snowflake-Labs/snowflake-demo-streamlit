from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from streamlit.source_util import _on_pages_changed, get_pages
from streamlit.util import calc_md5


@dataclass
class Page:
    """
    Stremlit Page Object.
    """

    path: str
    name: str
    icon: str

    @property
    def page_hash(self) -> str:
        """
        Create a new page hash.
        """
        return calc_md5(str(Path(self.path).absolute()))

    def to_dict(self) -> Dict[str, str]:
        """
        Return the Page Object as a dictionary.
        """
        return {
            "page_script_hash": self.page_hash,
            "page_name": self.name,
            "icon": self.icon,
            "script_path": self.path,
        }


def show_pages(pages: List[Page]):
    """
    Given a list of Page objects, get pages that are currently being
    shown in the sidebar, and overwrite them with this new set of pages.
    """
    current_pages: Dict[str, Dict[str, str]] = get_pages("")

    current_pages.clear()
    for page in pages:
        current_pages[page.page_hash] = page.to_dict()

    _on_pages_changed.send()
