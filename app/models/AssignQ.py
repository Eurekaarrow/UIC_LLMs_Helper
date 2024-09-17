from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class AssignQ(Base):
    __tablename__ = 'AssignQ'

    q_Id = Column(Integer, primary_key=True, autoincrement=True)
    Qtext = Column(Text)
    course_id = Column(Integer, ForeignKey('course.id'))  # 添加外键引用到Course表
    course = relationship("Course", back_populates="assignqs")  # 添加关系到Course模型

    llm_answer_id = Column(Integer, ForeignKey('LLM_Answer.LLM_id'))
    llm_answer = relationship("LLM_Answer", backref="assignq", uselist=False)

    def __init__(self, Qtext, llm_answer, course_id):
        self.Qtext = Qtext
        self.llm_answer = llm_answer
        self.course_id = course_id  # 初始化时添加course_id