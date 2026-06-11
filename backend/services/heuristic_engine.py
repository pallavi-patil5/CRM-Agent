import re


class HeuristicEngine:

    # =====================================
    # SPAM KEYWORDS
    # =====================================

    SPAM_KEYWORDS = [
        "seo",
        "guest post",
        "backlinks",
        "inheritance",
        "claim your share",
        "processing fee",
        "lottery",
        "crypto investment",
        "bitcoin opportunity",
        "prince"
    ]

    # =====================================
    # SECURITY KEYWORDS
    # =====================================

    SECURITY_KEYWORDS = [
        "ransomware",
        "btc",
        "bitcoin payment",
        "data breach",
        "unauthorized access",
        "suspicious login",
        "hacked",
        "security incident",
        "publish data"
    ]

    # =====================================
    # LEGAL KEYWORDS
    # =====================================

    LEGAL_KEYWORDS = [
        "legal action",
        "lawsuit",
        "cease and desist",
        "attorney",
        "legal notice",
        "formal complaint",
        "court",
        "litigation"
    ]

    # =====================================
    # COMPLIANCE KEYWORDS
    # =====================================

    COMPLIANCE_KEYWORDS = [
        "gdpr",
        "hipaa",
        "data deletion",
        "right to be forgotten",
        "privacy request",
        "data export",
        "compliance"
    ]

    # =====================================
    # URGENT KEYWORDS
    # =====================================

    URGENT_KEYWORDS = [
        "urgent",
        "asap",
        "immediately",
        "critical",
        "p0",
        "production down",
        "outage",
        "cannot access",
        "system unavailable"
    ]

    # =====================================
    # TEXT NORMALIZATION
    # =====================================

    @staticmethod
    def normalize(text):

        if not text:
            return ""

        return text.lower()

    # =====================================
    # KEYWORD MATCHER
    # =====================================

    @staticmethod
    def contains_keywords(text, keywords):

        text = HeuristicEngine.normalize(text)

        for keyword in keywords:

            if keyword in text:
                return True

        return False

    # =====================================
    # SPAM
    # =====================================

    def detect_spam(self, text):

        return self.contains_keywords(
            text,
            self.SPAM_KEYWORDS
        )

    # =====================================
    # SECURITY
    # =====================================

    def detect_security(self, text):

        return self.contains_keywords(
            text,
            self.SECURITY_KEYWORDS
        )

    # =====================================
    # LEGAL
    # =====================================

    def detect_legal(self, text):

        return self.contains_keywords(
            text,
            self.LEGAL_KEYWORDS
        )

    # =====================================
    # COMPLIANCE
    # =====================================

    def detect_compliance(self, text):

        return self.contains_keywords(
            text,
            self.COMPLIANCE_KEYWORDS
        )

    # =====================================
    # URGENCY
    # =====================================

    def detect_urgency(self, text):

        text = self.normalize(text)

        score = 0

        for keyword in self.URGENT_KEYWORDS:

            if keyword in text:
                score += 1

        if score >= 3:
            return "Critical"

        if score >= 1:
            return "High"

        return "Normal"

    # =====================================
    # MAIN ANALYSIS
    # =====================================

    def analyze_email(
        self,
        subject,
        body
    ):

        full_text = f"{subject}\n{body}"

        spam = self.detect_spam(
            full_text
        )

        security = self.detect_security(
            full_text
        )

        legal = self.detect_legal(
            full_text
        )

        compliance = self.detect_compliance(
            full_text
        )

        urgency = self.detect_urgency(
            full_text
        )

        requires_human = (
            security
            or legal
            or compliance
        )

        return {

            "spam": spam,

            "security": security,

            "legal": legal,

            "compliance": compliance,

            "urgency": urgency,

            "requires_human": requires_human
        }


# =====================================
# TEST
# =====================================

if __name__ == "__main__":

    engine = HeuristicEngine()

    sample_subject = (
        "URGENT: Ransomware Attack"
    )

    sample_body = """
    Our systems have been hacked.

    We demand 2 BTC.

    Immediate action required.
    """

    result = engine.analyze_email(
        sample_subject,
        sample_body
    )

    print(result)