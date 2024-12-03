from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Finding(Base):
    __tablename__ = 'findings'
    
    id = Column(Integer, primary_key=True)
    finding_name = Column(String, nullable=False)
    report_date = Column(Date, nullable=False)
    occurrences = Column(Integer, default=0)

    class Config:
        orm_mode = True

# Create database engine
engine = create_engine('sqlite:///findings.db')
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine) 