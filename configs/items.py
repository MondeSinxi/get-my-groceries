"""Grocery store item types."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Item:
    """Store Item"""

    item_name: str
    original_price: float
    date: datetime
    store_name: str
    discounted_price: Optional[float] = None
