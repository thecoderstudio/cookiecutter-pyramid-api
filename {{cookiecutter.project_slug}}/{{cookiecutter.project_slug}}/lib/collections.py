from collections.abc import Mapping


def update(
    destination: Mapping,
    source: Mapping,
    recursion_excluded: list = []
):
    new_destination = destination
    for key, value in source.items():
        if isinstance(value, Mapping) and key not in recursion_excluded:
            new_destination[key] = update(new_destination.get(key, {}), value)
        else:
            new_destination[key] = value

    return new_destination
