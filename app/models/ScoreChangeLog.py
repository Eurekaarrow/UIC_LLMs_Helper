# app/models/ScoreChangeLog.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ScoreChangeLog(Base):
    __tablename__ = 'score_change_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    llm_answer_id = Column(Integer, ForeignKey('LLM_Answer.LLM_id'))
    user_id = Column(Integer, ForeignKey('user.id'))  # 外键引用 User 表
    original_score = Column(Float)
    new_score = Column(Float)
    explanation = Column(String(255), nullable=True)

    llm_answer = relationship("LLM_Answer", back_populates="score_change_logs")
    user = relationship("User")  # 定义和 User 表的关系

    def __init__(self, llm_answer_id, original_score, new_score, explanation, user_id):
        self.llm_answer_id = llm_answer_id
        self.original_score = original_score
        self.new_score = new_score
        self.explanation = explanation
        self.user_id = user_id  # 初始化 user_id