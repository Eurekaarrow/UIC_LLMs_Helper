from sqlalchemy import Column, Integer, String, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from app.models.base import Base

class PersonalExperiment(Base):
    __tablename__ = 'personal_experiment'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    question_text = Column(Text)
    llm_used = Column(Text)
    llm_answer_image = Column(LargeBinary)
    score = Column(Integer)
    course_id = Column(Integer, ForeignKey('course.id'))  # 添加外键引用到Course表
    is_submitted = Column(Integer, default=0)  # 0 未提交, 1 提交待审核, 2 审核通过, 3 审核拒绝

    user = relationship('User', back_populates='personal_experiments')
    course = relationship('Course', back_populates='personal_experiments')

    def __init__(self, user_id, question_text, llm_used, llm_answer_image, score, course_id, is_submitted=0):
        self.user_id = user_id
        self.question_text = question_text
        self.llm_used = llm_used
        self.llm_answer_image = llm_answer_image
        self.score = score
        self.course_id = course_id
        self.is_submitted = is_submitted
