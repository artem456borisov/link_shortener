import random
import string

from datetime import datetime
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class LinkCreate(BaseModel):
    full_link: str
    short_link: Optional[str] = Field(default=None, validate_default=True)
    expires_at: Optional[datetime] = Field(default=None)

    @field_validator("short_link", mode="before")
    @classmethod
    def random_string(cls, link):
        random_string = ''.join(random.choices(string.ascii_letters, k=8))
        if link != None:
            return link
        else:
            return random_string

    @field_validator("expires_at", mode="before")
    @classmethod
    def str_to_datetime(cls, date_str:str):
        """
        Convert string in format 'MM-DD-YYYY HH:MM' to datetime object
        Example: "12-31-2023 14:30" -> datetime(2023, 12, 31, 14, 30)
        """
        return datetime.strptime(date_str, '%m-%d-%Y %H:%M').date()