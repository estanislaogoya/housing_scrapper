from sqlalchemy import Column, Integer, Text
from models import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Client(Base):
    __tablename__ = 'clients'
    
    client_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    phone = Column(Text)
    address = Column(Text)
    
    def __repr__(self):
        return f"<Client(id={self.client_id}, name={self.name}, email={self.email})>"
