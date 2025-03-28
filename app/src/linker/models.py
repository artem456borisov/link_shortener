from sqlalchemy import Table, Column, Integer, DateTime, MetaData, String
from random import randint
metadata = MetaData()

links_table = Table(
    "links_table",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("full_link", String),
    Column("short_link", String),
    Column("clicks", Integer, default=randint(0,100)),
    Column("expires_at", DateTime, default= None)
)