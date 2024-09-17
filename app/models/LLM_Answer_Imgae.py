import base64
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGBLOB  # 导入MySQL的LONGBLOB类型
from app.models.base import Base

class LLM_Answer_Image(Base):
    __tablename__ = 'LLM_Answer_Image'

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    llm_answer_id = Column(Integer, ForeignKey('LLM_Answer.LLM_id'))
    image_data = Column(LONGBLOB)  # 使用LONGBLOB替代LargeBinary

    llm_answer = relationship('LLM_Answer', back_populates='images')

    def get_image_data_base64(self):
        return base64.b64encode(self.image_data).decode('utf-8')

    def __init__(self, image_data=None, llm_answer_id=None):
        self.image_data = image_data
        self.llm_answer_id = llm_answer_id
