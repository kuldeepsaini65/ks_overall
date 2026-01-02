
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

def _add_validation_messages(request, error):
    """
    Handle model-level ValidationError
    """
    if hasattr(error, 'message_dict'):
        for errors in error.message_dict.values():
            for msg in errors:
                messages.error(request, msg)
    else:
        messages.error(request, error.messages[0])


def _add_form_error_messages(request, form):
    """
    Handle form validation errors
    """
    for field, errors in form.errors.items():
        for error in errors:
            if field == '__all__':
                messages.error(request, error)
            else:
                messages.error(
                    request,
                    f"{field.replace('_', ' ').title()}: {error}"
                )
