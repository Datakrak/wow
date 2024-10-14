from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Item(Base):
    __tablename__ = "ITEMS"

    ID = Column(String(20), primary_key=True, index=True)
    NAME = Column(String(100), index=True)

    auction = relationship('Auction', back_populates='item')


class Auction(Base):
    __tablename__ = "AUCTIONS"

    ID = Column(String(100), primary_key=True, index=True)
    ID_AUCTION = Column(String(100), index=True)
    ID_ITEM = Column(String(100), ForeignKey('ITEMS.ID'))
    PRICE = Column(Integer)
    QUANTITY = Column(Integer)
    TIME_LEFT = Column(String(20))
    DATETIME = Column(DateTime)

    item = relationship("Item", back_populates='auction')