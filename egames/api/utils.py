def custom_payload_handler(token, user=None, request=None):
    if user:
        role_name = user.role.role_name if hasattr(user, 'role') else None
        token['user_id'] = role_name
    return token