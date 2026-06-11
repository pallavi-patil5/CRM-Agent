from database.db import SessionLocal
from database.models import Action


class ActionService:

    def __init__(self):

        self.db = SessionLocal()

    # =====================================
    # CREATE ACTION
    # =====================================

    def create_action(
        self,
        email_id,
        action_type,
        reasoning_trace,
        proposed_content="",
        approved=False
    ):

        action = Action(

            email_id=email_id,

            action_type=action_type,

            agent_reasoning_log=reasoning_trace,

            proposed_content=proposed_content,

            is_approved=approved
        )

        self.db.add(action)

        self.db.commit()

        self.db.refresh(action)

        return action

    # =====================================
    # GET ACTION
    # =====================================

    def get_action(
        self,
        action_id
    ):

        return (
            self.db.query(Action)
            .filter(
                Action.id == action_id
            )
            .first()
        )

    # =====================================
    # GET ALL ACTIONS
    # =====================================

    def get_all_actions(self):

        return (
            self.db.query(Action)
            .all()
        )

    # =====================================
    # APPROVE ACTION
    # =====================================

    def approve_action(
        self,
        action_id,
        approver
    ):

        action = self.get_action(
            action_id
        )

        if not action:
            return None

        action.is_approved = True

        action.approved_by = approver

        self.db.commit()

        self.db.refresh(action)

        return action

    # =====================================
    # ACTION SUMMARY
    # =====================================

    def get_action_summary(
        self,
        action_id
    ):

        action = self.get_action(
            action_id
        )

        if not action:
            return None

        return {

            "action_id":
                action.id,

            "action_type":
                action.action_type,

            "approved":
                action.is_approved,

            "approved_by":
                action.approved_by
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

    service = ActionService()

    sample_reasoning = [

        {
            "step":
                "Heuristic Analysis",

            "result":
                {
                    "legal": True
                }
        },

        {
            "step":
                "Classification",

            "result":
                {
                    "category":
                        "Legal"
                }
        }
    ]

    action = service.create_action(

        email_id=1,

        action_type="Legal-Flag",

        reasoning_trace=sample_reasoning,

        proposed_content=
        "Case escalated to legal team."
    )

    print()

    print(
        service.get_action_summary(
            action.id
        )
    )

    service.close()