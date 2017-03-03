from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Country(Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """return country data in serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


class Missile(Base):
    __tablename__ = 'missile'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(500))
    country_id = Column(String(80), ForeignKey('country.id'))
    country = relationship(Country)
    link = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return Missile data in serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'country': self.country_id,
            'link': self.link
        }

engine = create_engine('sqlite:///lots_of_missiles.db')

Base.metadata.create_all(engine)
