from sqlalchemy import Column, String, Integer
from app.models.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=True)
    password = Column('password', String(100))
    user_type = Column('type', String(50))

    personal_experiments = relationship('PersonalExperiment', back_populates='user')

    def __init__(self, email, password, user_type):
        self.email = email
        self.password = password
        self.user_type = user_type

    @property
    def getpassword(self):
        return self.password

    @property
    def setpassword(self, password):
        self.password = password

    def getemail(self):
        return self.email

    def gettype(self):
        return self.user_type