from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models import Base
from models.clients import Client
import datetime

class SearchQuery(Base):
    __tablename__ = 'search_queries'
    
    query_id = Column(Integer, primary_key=True, autoincrement=True)
    search_text = Column(Text, nullable=False)
    provider_name = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    client_id = Column(Integer, ForeignKey('clients.client_id'))
    enabled = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<SearchQuery(query_id={self.query_id}, search_text={self.search_text}, provider_name={self.provider_name})>"
