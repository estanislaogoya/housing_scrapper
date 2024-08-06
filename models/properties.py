from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models import Base
from models.clients import Client
import datetime

class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    internal_id = Column(Text, nullable=False)
    provider = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    captured_date = Column(TIMESTAMP, server_default=func.now())
    client_id = Column(Integer, ForeignKey('clients.client_id'))
    
    client = relationship("Client", backref="properties")
    
    def __repr__(self):
        return f"<Property(id={self.id}, internal_id={self.internal_id}, provider={self.provider})>"
