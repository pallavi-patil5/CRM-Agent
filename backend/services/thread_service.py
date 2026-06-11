from database.db import SessionLocal
from database.models import Thread
from database.models import Email


class ThreadService:

    def __init__(self):

        self.db = SessionLocal()

    # =====================================
    # GET THREAD
    # =====================================

    def get_thread_by_thread_id(
        self,
        thread_identifier
    ):

        thread = (
            self.db.query(Thread)
            .filter(
                Thread.thread_id ==
                thread_identifier
            )
            .first()
        )

        return thread

    # =====================================
    # GET ALL EMAILS
    # =====================================

    def get_thread_emails(
        self,
        thread_identifier
    ):

        thread = (
            self.get_thread_by_thread_id(
                thread_identifier
            )
        )

        if not thread:

            return []

        emails = (
            self.db.query(Email)
            .filter(
                Email.thread_id ==
                thread.id
            )
            .order_by(
                Email.email_timestamp.asc()
            )
            .all()
        )

        return emails

    # =====================================
    # BUILD HISTORY
    # =====================================

    def build_thread_history(
        self,
        thread_identifier
    ):

        emails = (
            self.get_thread_emails(
                thread_identifier
            )
        )

        if not emails:

            return ""

        history = []

        for email in emails:

            history.append(
                f"""
Sender: {email.sender}

Subject: {email.subject}

Message:
{email.body}
"""
            )

        return "\n\n".join(history)

    # =====================================
    # THREAD SUMMARY
    # =====================================

    def get_thread_summary(
        self,
        thread_identifier
    ):

        emails = (
            self.get_thread_emails(
                thread_identifier
            )
        )

        return {

            "thread_id":
                thread_identifier,

            "email_count":
                len(emails),

            "participants":
                list(
                    set(
                        [
                            e.sender
                            for e in emails
                        ]
                    )
                )
        }

    # =====================================
    # CLOSE SESSION
    # =====================================

    def close(self):

        self.db.close()


# =====================================
# TEST
# =====================================

if __name__ == "__main__":

    service = ThreadService()

    history = (
        service.build_thread_history(
            "thread_alice_pricing"
        )
    )

    print(history)

    print()

    summary = (
        service.get_thread_summary(
            "thread_alice_pricing"
        )
    )

    print(summary)

    service.close()