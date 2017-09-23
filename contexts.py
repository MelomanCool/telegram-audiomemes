from collections import defaultdict


_user_contexts = defaultdict(dict)


def get_user_context(user_id) -> dict:
    return _user_contexts[user_id]
