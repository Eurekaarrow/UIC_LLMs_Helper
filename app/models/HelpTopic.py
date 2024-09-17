from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class HelpTopic(Base):
    __tablename__ = 'HelpTopic'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'))  # 添加外键
    topic = Column(String(100))
    subtopic = Column(String(100))
    llm_answer_id = Column(Integer, ForeignKey('LLM_Answer.LLM_id'))
    topic_helps_questions = Column(String(500))  # 新增的字段

    llm_answer = relationship('LLM_Answer', back_populates='help_topics')
    course = relationship('Course', back_populates='help_topics')

    def __init__(self, course_id, topic, subtopic, llm_answer_id=None, topic_helps_questions=None):
        self.course_id = course_id
        self.topic = topic
        self.subtopic = subtopic
        self.llm_answer_id = llm_answer_id
        self.topic_helps_questions = topic_helps_questions
