import datetime
import uuid

from sqlalchemy import and_, Boolean, Column, DateTime, func, not_, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import case

from {{cookiecutter.project_slug}}.models.functions import utcnow

NUMBER_OF_HOURS_VALID = 1


class SecureTokenMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_hash = Column(String(119), nullable=False)
    token_salt = Column(String(29), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    invalidated = Column(Boolean, default=False, nullable=False)
    expires_on = Column(
        DateTime,
        default=utcnow() + datetime.timedelta(
            hours=NUMBER_OF_HOURS_VALID
        ),
        nullable=False
    )

    @hybrid_property
    def active(self):
        return self.seconds_until_expiry > 0 and not self.invalidated

    @active.expression
    def active(cls):
        return case([(and_(
            cls.seconds_until_expiry > 0,
            not_(cls.invalidated)), True)],
            else_=False)

    @hybrid_property
    def seconds_until_expiry(self):
        seconds_left = (
            self.expires_on - datetime.datetime.utcnow()
        ).total_seconds()
        return seconds_left if seconds_left > 0 else 0

    @seconds_until_expiry.expression
    def seconds_until_expiry(cls):
        current_time = func.current_timestamp()
        seconds_left = (
            func.date_part('day', cls.expires_on - current_time) * 24 +
            func.date_part('hour', cls.expires_on - current_time) * 60 +
            func.date_part('minute', cls.expires_on - current_time) * 60 +
            func.date_part('second', cls.expires_on - current_time))

        return case([(seconds_left > 0, seconds_left)], else_=0)

    def invalidate(self):
        self.invalidated = True
