from sqlalchemy import Column, Integer, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from app.models.base import Base

class LLM_Answer(Base):
    __tablename__ = 'LLM_Answer'

    LLM_id = Column(Integer, primary_key=True, autoincrement=True)
    LLM_used = Column(Text)
    score = Column(Integer)
    comment = Column(Text)

    images = relationship('LLM_Answer_Image', back_populates='llm_answer')
    score_change_logs = relationship('ScoreChangeLog', back_populates='llm_answer', cascade="all, delete-orphan")

    help_topics = relationship('HelpTopic', back_populates='llm_answer', cascade="all, delete-orphan")  # 新增与HelpTopic的关系

    def __init__(self, LLM_used, score, comment):
        self.LLM_used = LLM_used
        self.score = score
        self.comment = comment
