from sqlalchemy import create_engine, Column, String, Integer, Float, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    cohort = Column(String, default="Spring 2026")
    interviews_completed = Column(Integer, default=0)
    overall_avg = Column(Float, nullable=True)
    communication_avg = Column(Float, nullable=True)
    status = Column(String, default="Not Started")
    needs_review = Column(Boolean, default=False)
    last_evaluated = Column(DateTime, default=datetime.utcnow)

class Evaluation(Base):
    __tablename__ = 'evaluations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String)
    interview_number = Column(Integer)
    simulation = Column(String)
    indicator_id = Column(Integer)
    indicator_name = Column(String)
    level = Column(Integer)
    confidence = Column(Float)
    evidence = Column(JSON)
    justification = Column(String)
    strengths = Column(String)
    improvements = Column(String)
    instructor_override = Column(Integer, nullable=True)
    instructor_notes = Column(String, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///rubricai.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    return SessionLocal()
