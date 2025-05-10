from pydantic import BaseModel
from typing import Optional

class Link(BaseModel):
    url: str
    slug: Optional[str] = None