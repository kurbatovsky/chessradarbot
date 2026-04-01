from app.db import engine
from app.models import AppCache


def main():
    AppCache.__table__.drop(bind=engine, checkfirst=True)
    AppCache.__table__.create(bind=engine, checkfirst=True)
    print("app_cache recreated")


if __name__ == "__main__":
    main()
