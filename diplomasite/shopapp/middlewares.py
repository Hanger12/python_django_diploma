from urllib.parse import urlencode

from django.shortcuts import redirect
from rest_framework.request import Request


class ModifyQueryParamsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        print("юда мы зашли")
        request_method = request.META['REQUEST_METHOD']
        path_info = request.META['PATH_INFO']
        print(request_method)
        print(path_info)
        if path_info == '/api/catalog/':
            query_params = request.GET.copy()
            print(query_params)
            new_params = {}
            for key, value in query_params.items():
                if key.startswith('filter[') and key.endswith(']'):
                    new_key = key[7:-1]  # Удаляем 'filter[' и ']'
                    if value == 'false':
                        value = ''
                    new_params[new_key] = value
                else:
                    new_params[key] = value
            # Генерация нового URL с измененными параметрами
            if query_params != request.GET:
                new_query_string = urlencode(query_params, doseq=True)
                new_url = f"{request.path}?{new_query_string}"
                return redirect(new_url)
        # Продолжаем выполнение запроса, если изменений не было
        response = self.get_response(request)
        return response
