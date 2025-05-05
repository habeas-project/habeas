"""Custom exceptions for the Habeas backend application."""


class HabeasBaseError(Exception):
    """Base class for all custom application exceptions."""

    pass


# --- Admission Service Exceptions ---


class AdmissionServiceError(HabeasBaseError):
    """Base class for errors related to the Admission Service."""

    pass


class AttorneyNotFoundError(AdmissionServiceError):
    """Raised when an Attorney record is not found for a given ID."""

    def __init__(self, attorney_id: int, message: str | None = None):
        self.attorney_id = attorney_id
        self.message = message or f"Attorney with id {attorney_id} not found."
        super().__init__(self.message)


class CourtNotFoundError(AdmissionServiceError):
    """Raised when a Court record is not found for a given ID."""

    def __init__(self, court_id: int, message: str | None = None):
        self.court_id = court_id
        self.message = message or f"Court with id {court_id} not found."
        super().__init__(self.message)


class AdmissionNotFoundError(AdmissionServiceError):
    """Raised when an AttorneyCourtAdmission link is not found."""

    def __init__(self, attorney_id: int, court_id: int, message: str | None = None):
        self.attorney_id = attorney_id
        self.court_id = court_id
        self.message = message or f"Admission link between Attorney {attorney_id} and Court {court_id} not found."
        super().__init__(self.message)


# --- Other Service Exceptions (Add as needed) ---
# e.g., AuthenticationError, AuthorizationError, etc.
