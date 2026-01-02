from src.backend.db.database import Base,engine
import src.backend.model.tables 

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()