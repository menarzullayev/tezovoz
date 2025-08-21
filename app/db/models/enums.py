# UPD-105
import enum

class UserStatusEnum(enum.Enum):
    """
    Foydalanuvchining botdagi holati.
    """
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"

class PaymentStatusEnum(enum.Enum):
    """
    To'lov holati.
    """
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"
    REJECTED = "rejected"

class NotificationStatusEnum(enum.Enum):
    """
    Bildirishnoma holati.
    """
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class FeedbackStatusEnum(enum.Enum):
    """
    Fikr-mulohaza holati.
    """
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class ReferralStatusEnum(enum.Enum):
    """
    Referal holati.
    """
    ACTIVE = "active"
    PAID = "paid"

class LogTypeEnum(enum.Enum):
    """
    Log turi.
    """
    ADMIN_ACTION = "admin_action"
    VOTING = "voting"
    PAYMENT = "payment"
    ERROR = "error"