# app/db/queries/init_db.py
from app.db.base import Base

from app.db.models.user import User
from app.db.models.image import Image
from app.db.models.story import Story
from app.db.models.poem import Poem
from app.db.session import engine

def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()
