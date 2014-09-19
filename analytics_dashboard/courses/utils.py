from waffle import switch_is_active


def is_feature_enabled(item):
    switch_name = item.get('switch', None)

    if switch_name:
        return switch_is_active(switch_name)

    return True
