from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///users.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    active = Column(Boolean, default=True)

Base.metadata.create_all(engine)

def add_or_update_user(u):
    session = Session()
    user = session.get(User, u.id)

    if user:
        user.active = True
    else:
        user = User(
            id=u.id,
            username=u.username,
            first_name=u.first_name,
            last_name=u.last_name,
            active=True
        )
        session.add(user)

    session.commit()
    session.close()

def deactivate_user(u):
    session = Session()
    user = session.get(User, u.id)
    if user:
        user.active = False
        session.commit()
    session.close()

def get_active_users():
    session = Session()
    users = session.query(User).filter_by(active=True).all()
    session.close()
    return users
