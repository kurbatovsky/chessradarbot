import asyncio

from app.services.notification_service import process_due_users


def main():
    asyncio.run(process_due_users())


if __name__ == "__main__":
    main()
