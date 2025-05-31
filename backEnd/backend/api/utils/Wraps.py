from ..models.file import file


def get_first_existing_key(sources, keys):
    for key in keys:
        for source in sources:
            if source and key in source:
                return source[key]
    return None

def before_and_after_view(number: int):
    def actual_decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                keys = ["idlaw", "idLaw", "id"]
                sources = [request.data, kwargs]
                idlaw = get_first_existing_key(sources, keys)
                curfile = file.objects.get(id=idlaw)
                curfile.status = 0
                curfile.save()
            except:
                return None
            response = func(request, *args, **kwargs)
            curfile.status = number
            curfile.save()
            return response
        return wrapper
    return actual_decorator