from app.db import Base, engine
from app import models  # noqa: F401


def main():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables recreated successfully.")


if __name__ == "__main__":
    main()