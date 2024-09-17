from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models import Request_image  # 确保导入 Request_image

class Request(Base):
    __tablename__ = 'Request'

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    qtext = Column(Text, nullable=True)
    course_id = Column(Integer, nullable=True)
    llm_used = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    llm_answer_id = Column(Integer, nullable=True)
    new_score = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=True)
    course_number = Column('course_number', String(100), nullable=True)
    course_name = Column('course_name', String(100), nullable=True)
    course_category = Column('course_category', String(100), nullable=True)
    request_type = Column(String(255), nullable=True)

    image_relationships = relationship('Request_image', back_populates='request')

    def __init__(self, qtext=None, course_id=None, llm_used=None, score=None, 
                 comment=None, llm_answer_id=None, new_score=None, 
                 explanation=None, user_id=None, course_number=None, 
                 course_name=None, course_category=None, request_type=None):
        self.qtext = qtext
        self.course_id = course_id
        self.llm_used = llm_used
        self.score = score
        self.comment = comment
        self.llm_answer_id = llm_answer_id
        self.new_score = new_score
        self.explanation = explanation
        self.user_id = user_id
        self.course_number = course_number
        self.course_name = course_name
        self.course_category = course_category
        self.request_type = request_type
