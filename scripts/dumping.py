from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, VARCHAR, TEXT, ForeignKey, TIMESTAMP, BIGINT, Table
import json
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import DATE, NUMERIC, Integer, Text
import time


Base = declarative_base()

HOST = "localhost"
DB = "tweetsDB"
USER = "postgres"
PASSWD = "passwd"

posgres_conn_str = f"postgresql://{USER}:{PASSWD}@{HOST}/{DB}"
engine = create_engine(posgres_conn_str)

DBSession = sessionmaker()
DBSession.configure(bind=engine)
Base.metadata.create_all(engine)
session = DBSession()


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(BIGINT, primary_key=True)
    screen_name = Column(VARCHAR(200))
    name = Column(VARCHAR(200))
    description = Column(TEXT, nullable=True)
    followers_count = Column(INTEGER, nullable=True)
    friends_count = Column(INTEGER, nullable=True)
    statuses_count = Column(INTEGER, nullable=True)


class HashTag(Base):
    __tablename__ = 'hashtags'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    value = Column(TEXT, nullable=True, unique=True)


tweet_hashtags = Table('tweet_hashtags', 
                        Base.metadata, 
                        Column(('tweet_id'), VARCHAR(20), ForeignKey('tweets.id')),
                        Column(('hashtag_id'), INTEGER, ForeignKey('hashtags.id')))

tweet_mentions = Table('tweet_mentions',
                        Base.metadata,
                        Column(('account_id'), BIGINT, ForeignKey('accounts.id')),
                        Column(('tweet_id'), VARCHAR(20), ForeignKey('tweets.id')))

class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(VARCHAR(20), primary_key=True)
    content = Column(TEXT, nullable=True)
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    retweet_count = Column(INTEGER, nullable=True)
    favorite_count = Column(INTEGER, nullable=True)
    neg = Column(NUMERIC(6, 4), nullable=True)
    neu = Column(NUMERIC(6, 4), nullable=True)
    pos = Column(NUMERIC(6, 4), nullable=True)
    compound = Column(NUMERIC(6, 4), nullable=True)
    happened_at = Column(TIMESTAMP(timezone=True))
    author_id = Column(ForeignKey('accounts.id'), nullable=False)
    country_id = Column(ForeignKey('countries.id'), nullable=True)
    parent_id = Column(ForeignKey('tweets.id'), nullable=True)
    country = relationship("Country", lazy='joined')
    author = relationship("Account", lazy='joined')
    hashtags = relationship("HashTag", secondary=tweet_hashtags, lazy='joined')
    mentions = relationship("Account", secondary=tweet_mentions, lazy='joined')
    parent = relationship("Tweet", remote_side=[id])



class Country(Base):
    __tablename__ = 'countries'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    code = Column(VARCHAR(2), nullable=False, unique=True)
    name = Column(VARCHAR(200))


class AccountDocument:
    def __init__(self, account_obj):
        self.id = str(account_obj.id)
        self.screen_name = account_obj.screen_name
        self.name = account_obj.name
        self.description = account_obj.description
        self.followers_count = account_obj.followers_count
        self.friends_count = account_obj.friends_count
        self.statuses_count = account_obj.statuses_count


class LocationDocument:
    def __init__(self, location_point):
        loc_point = to_shape(location_point)
        self.lat, self.lon = loc_point.y, loc_point.x 


class CountryDocument:
    def __init__(self, country_obj):
        self.code, self.name = country_obj.code, country_obj.name
    


class TweetDocument:
    def __init__(self, tweet_obj):
        # self.id = str(tweet_obj.id)
        self.content = tweet_obj.content
        self.location = LocationDocument(tweet_obj.location) if tweet_obj.location is not None else None
        self.retweet_count = tweet_obj.retweet_count
        self.favorite_count = tweet_obj.favorite_count
        self.neg = float(tweet_obj.neg) if tweet_obj.neg is not None else None
        self.neu = float(tweet_obj.neu) if tweet_obj.neu is not None else None
        self.pos = float(tweet_obj.pos) if tweet_obj.pos is not None else None
        self.compound = float(tweet_obj.compound) if tweet_obj.compound is not None else None
        self.happened_at = str(tweet_obj.happened_at).replace(' ', 'T')
        self.author = AccountDocument(tweet_obj.author) if tweet_obj.author is not None else None
        self.country = CountryDocument(tweet_obj.country) if tweet_obj.country is not None else None
        self.parent_id = tweet_obj.parent_id if tweet_obj.parent_id is not None else None
        self.parent = TweetDocument(tweet_obj.parent) if  tweet_obj.parent else None
        self.hashtags = [hashtag.value for hashtag in tweet_obj.hashtags if tweet_obj.hashtags]
        self.mentions = [AccountDocument(mention) for mention in tweet_obj.mentions if tweet_obj.mentions]
        



def main():
    offset = "0"


    file_num = 0


    while True:    

        with open(f"dumps/psql_dump_with_parent{file_num}.txt", "w") as file:
            begin = time.time()

            results = session.query(Tweet).filter(Tweet.id > offset).order_by(Tweet.id).limit(25_000)
            
            if results.count() == 0:
                break
            for res in results:
                routing = res.id if res.parent_id is None else res.parent_id
                file.write('{"index":{"_id":"' + res.id + '", "routing":"' + routing + '"}}\n')
                to_dump = TweetDocument(res)
                file.write(json.dumps(to_dump, default= lambda x: x.__dict__)+"\n")
                offset = res.id

            end = time.time()
            print(end - begin)
            file_num += 1
        break


if __name__ == "__main__":
    print("running")
    main()