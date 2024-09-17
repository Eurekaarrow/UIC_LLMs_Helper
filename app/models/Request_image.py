from sqlalchemy import Column, Integer, ForeignKey, LargeBinary
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Request_image(Base):
    __tablename__ = 'Request_Image'

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    llm_answer_id = Column(Integer, ForeignKey('Request.request_id'))
    image_data = Column(LONGBLOB)  # 使用LONGBLOB替代LargeBinary

    request = relationship('Request', back_populates='image_relationships')

    def __init__(self, image_data, llm_answer_id):
        self.image_data = image_data
        self.llm_answer_id = llm_answer_id
