from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    course_number = Column('course_number', String(100))
    course_name = Column('course_name', String(100))
    course_category = Column('course_category', String(100))
    assignqs = relationship('AssignQ', back_populates='course')

    # 添加与 PersonalExperiment 的关系
    personal_experiments = relationship('PersonalExperiment', back_populates='course')

    help_topics = relationship('HelpTopic', back_populates='course')  # 添加与HelpTopic的关系

    def __init__(self, course_number, course_name, course_category):
        self.course_number = course_number
        self.course_name = course_name
        self.course_category = course_category
