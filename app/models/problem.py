from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., "Supervised Learning", "Unsupervised Learning"
    initial_code = Column(Text, nullable=False)  # Starter code template
    solution_code = Column(Text, nullable=False)  # Reference solution
    test_cases = Column(Text, nullable=False)  # JSON string of test cases
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    solutions = relationship("Solution", back_populates="problem")
    submissions = relationship("Submission", back_populates="problem") 