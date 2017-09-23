from functools import wraps


def restricted(admins):

    def decorator(func):

        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id not in admins:
                print("Unauthorized access denied for {}.".format(user_id))
                return

            return func(bot, update, *args, **kwargs)

        return wrapped

    return decorator
