import logging

from django.contrib.admin.options import get_content_type_for_model

from core.constants import SYSTEM_PROGRAM_USER_ID
from users.models import ProgramUser

logger = logging.getLogger("django")


def get_system_user():
    try:
        return ProgramUser.objects.get(pk=SYSTEM_PROGRAM_USER_ID)
    except ProgramUser.DoesNotExist:
        logger.warning("System ProgramUser does not exists.")
        raise ProgramUser.DoesNotExist("System ProgramUser does not exists.")


def log_creation(obj, message='[{"added": {}}]'):
    """
    Log that an object has been successfully added.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import ADDITION, LogEntry

    user = get_system_user()

    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=ADDITION,
        change_message=message,
    )


def log_change(obj, message):
    """
    Log that an object has been successfully changed.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import CHANGE, LogEntry

    user = get_system_user()

    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=CHANGE,
        change_message=message,
    )


def log_deletion(obj):
    """
    Log that an object will be deleted. Note that this method must be
    called before the deletion.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import DELETION, LogEntry

    user = get_system_user()

    return LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=DELETION,
    )
