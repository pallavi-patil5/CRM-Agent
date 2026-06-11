from database.db import SessionLocal
from database.models import Ticket


class TicketService:

    def __init__(self):

        self.db = SessionLocal()

    # =====================================
    # CREATE TICKET
    # =====================================

    def create_ticket(
        self,
        email_id,
        title,
        description,
        priority="Medium",
        assignee="Support Team"
    ):

        ticket = Ticket(

            email_id=email_id,

            title=title,

            description=description,

            priority=priority,

            assignee=assignee,

            status="Open"
        )

        self.db.add(ticket)

        self.db.commit()

        self.db.refresh(ticket)

        return ticket

    # =====================================
    # GET TICKET
    # =====================================

    def get_ticket(
        self,
        ticket_id
    ):

        return (
            self.db.query(Ticket)
            .filter(
                Ticket.id == ticket_id
            )
            .first()
        )

    # =====================================
    # GET ALL TICKETS
    # =====================================

    def get_all_tickets(self):

        return (
            self.db.query(Ticket)
            .all()
        )

    # =====================================
    # UPDATE STATUS
    # =====================================

    def update_status(
        self,
        ticket_id,
        new_status
    ):

        ticket = (
            self.get_ticket(
                ticket_id
            )
        )

        if not ticket:

            return None

        ticket.status = new_status

        self.db.commit()

        self.db.refresh(ticket)

        return ticket

    # =====================================
    # GET OPEN TICKETS
    # =====================================

    def get_open_tickets(self):

        return (
            self.db.query(Ticket)
            .filter(
                Ticket.status == "Open"
            )
            .all()
        )

    # =====================================
    # PRIORITY ASSIGNMENT
    # =====================================

    def determine_priority(
        self,
        classification
    ):

        category = classification.get(
            "category",
            ""
        )

        urgency = classification.get(
            "urgency",
            "Medium"
        )

        if category in [
            "Security",
            "Legal"
        ]:
            return "Critical"

        if urgency == "Critical":
            return "Critical"

        if urgency == "High":
            return "High"

        return "Medium"

    # =====================================
    # AUTO CREATE FROM AGENT
    # =====================================

    def create_from_classification(
        self,
        email_id,
        classification
    ):

        priority = (
            self.determine_priority(
                classification
            )
        )

        ticket = self.create_ticket(

            email_id=email_id,

            title=
            f"{classification['category']} Case",

            description=
            classification["reasoning"],

            priority=priority
        )

        return ticket

    # =====================================
    # CLOSE SESSION
    # =====================================

    def close(self):

        self.db.close()


# =====================================
# TEST
# =====================================

if __name__ == "__main__":

    service = TicketService()

    classification = {

        "category":
            "Refund",

        "urgency":
            "High",

        "reasoning":
            "Customer was charged twice."
    }

    ticket = (
        service.create_from_classification(
            email_id=1,
            classification=classification
        )
    )

    print()

    print("Ticket Created")

    print("ID:", ticket.id)

    print("Priority:", ticket.priority)

    service.close()