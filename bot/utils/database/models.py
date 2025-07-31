from asyncpg import DuplicateDatabaseError, connect
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, VARCHAR, Integer, func, text
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from bot.data.config import DB_USER, DB_PASS, DB_HOST, DB_NAME, toshkent_now

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, pool_size=200, max_overflow=2000)
Base = declarative_base()
async_session = async_sessionmaker(engine, expire_on_commit=False)
async def create_database(db_name=DB_NAME):
    conn_info = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/postgres'
    conn = await connect(conn_info)

    try:
        await conn.execute(f'CREATE DATABASE {db_name}')
        print(f'Database {db_name} created successfully.')
    except DuplicateDatabaseError:
        print(f'Database {db_name} already exists.')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        await conn.close()
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Jadvallar yaratildi.")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    fullname = Column(String, nullable=True)
    username = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    language = Column(String(5), nullable=True)
    is_blocked = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    referral_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=toshkent_now)
    updated_at = Column(DateTime, default=toshkent_now, onupdate=toshkent_now)
    deleted_at = Column(DateTime, nullable=True)

class Channel(Base):
    __tablename__ = "channels"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(String, nullable=False)

class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(500))
    link = Column(String)
    file_id = Column(String)
    caption = Column(String, nullable=True)
    bot_username = Column(String, nullable=True)
    bot_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    channel_message_id = Column(String, nullable=True)
    channel_id = Column(String, nullable=True)


class TelegramApp(Base):
    __tablename__ = "telegram_apps"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    api_id = Column(BigInteger, nullable=False)
    api_hash = Column(String, nullable=False)

    user_bots = relationship("UserBot", back_populates="app")


class UserBot(Base):
    __tablename__ = "user_bots"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False)
    session_string = Column(String, nullable=False)
    telegram_user_id = Column(BigInteger, nullable=False)
    app_id = Column(BigInteger, ForeignKey("telegram_apps.id"))
    app = relationship("TelegramApp", back_populates="user_bots")
    is_active = Column(Boolean, default=True)

class SocialNetworkStat(Base):
    __tablename__ = "social_network_stats"

    id = Column(Integer, primary_key=True)
    facebook = Column(BigInteger, default=0)
    instagram = Column(BigInteger, default=0)
    youtube = Column(BigInteger, default=0)
    tiktok = Column(BigInteger, default=0)
    telegram = Column(BigInteger, default=0)
    twitter = Column(BigInteger, default=0)
    vk = Column(BigInteger, default=0)
    ok = Column(BigInteger, default=0)
    linkedin = Column(BigInteger, default=0)
    reddit = Column(BigInteger, default=0)
    snapchat = Column(BigInteger, default=0)
    pinterest = Column(BigInteger, default=0)
    tumblr = Column(BigInteger, default=0)
    threads = Column(BigInteger, default=0)
    weibo = Column(BigInteger, default=0)
    wechat = Column(BigInteger, default=0)
    track = Column(BigInteger, nullable=False, server_default=text('0'), default=0 )

class Channel_userbots(Base):
    __tablename__ = "channel_userbots"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    channel_chat_id = Column(BigInteger, unique=True, nullable=False)
    channel_name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Channel_userbots(id={self.id}, channel_chat_id={self.channel_chat_id}, channel_name={self.channel_name})>"

class DB_bots(Base):
    __tablename__ = "db_bots"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)




class TelegramAppExtra(Base):
    __tablename__ = "telegram_apps_extra"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    api_id = Column(BigInteger, nullable=False)
    api_hash = Column(String, nullable=False)

    user_bots = relationship("UserBotExtra", back_populates="app")


class UserBotExtra(Base):
    __tablename__ = "user_bots_extra"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False)
    session_string = Column(String, nullable=False)
    telegram_user_id = Column(BigInteger, nullable=False)
    app_id = Column(BigInteger, ForeignKey("telegram_apps_extra.id"))
    app = relationship("TelegramAppExtra", back_populates="user_bots")
    is_active = Column(Boolean, default=True)