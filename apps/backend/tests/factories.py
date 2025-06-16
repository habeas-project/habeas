"""Test data factories using factory-boy."""

import factory

from faker import Faker

from app.models.admin import Admin
from app.models.attorney import Attorney
from app.models.court import Court
from app.models.user import User

# Initialize Faker
fake = Faker()


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory for SQLAlchemy models."""

    class Meta:
        abstract = True
        sqlalchemy_session = None  # Session will be injected via fixture
        sqlalchemy_session_persistence = "flush"  # Use flush for speed with SQLite, commit might be needed for PG


class AttorneyFactory(BaseFactory):
    """Factory for the Attorney model."""

    class Meta:
        model = Attorney

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    phone_number = factory.LazyFunction(lambda: f"+1{fake.numerify('##########')}")
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '.')}@{fake.domain_name()}")
    zip_code = factory.Faker("zipcode")
    state = factory.Faker("state_abbr")
    # user_id = factory.SubFactory("tests.factories.UserFactory", attorney=None) # Example if user relationship exists


class CourtFactory(BaseFactory):
    """Factory for the Court model."""

    class Meta:
        model = Court

    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(
        lambda: f"{fake.city()} {fake.random_element(['District', 'Circuit', 'Supreme'])} Court"
    )
    abbreviation = factory.LazyFunction(
        lambda: f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}"
    )
    url = factory.Faker("url")


class UserFactory(BaseFactory):
    """Factory for the User model."""

    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    cognito_id = factory.Sequence(lambda n: f"mock_user_{n}@example.com")
    user_type = factory.Faker("random_element", elements=["attorney", "client", "admin"])
    is_active = True


# Example of a factory creating relationships (if Attorney <-> Court exists)
# class AttorneyWithCourtsFactory(AttorneyFactory):
#     """Factory that creates an attorney with pre-assigned courts."""
#     @factory.post_generation
#     def admitted_courts(self, create, extracted, **kwargs):
#         if not create:
#             return
#
#         if extracted:
#             # Use provided courts
#             for court in extracted:
#                 self.admitted_courts.append(court)
#         else:
#             # Create 2 random courts if none provided
#             courts = CourtFactory.create_batch(2)
#             for court in courts:
#                 self.admitted_courts.append(court)


class AdminFactory(BaseFactory):
    """Factory for the Admin model."""

    class Meta:
        model = Admin

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '.')}@{fake.domain_name()}")
    department = factory.Faker("random_element", elements=["IT", "Security", "HR", "Legal", "Operations"])
    role = factory.Faker("random_element", elements=["admin", "super_admin", "moderator"])


# TODO: Add factories for other core models as needed.
# TODO: Configure factory session injection in conftest.py
