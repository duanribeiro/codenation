from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotAcceptable


class BasicPagination(PageNumberPagination):
    def get_paginated_response(self, queryset, request, serializer,
                            serializer_kwargs={}):
        self.page_size = self.__get_page_size_from_request(request)

        serializer = serializer(
            self.paginate_queryset(queryset, request),
            many=True,
            **serializer_kwargs
        )
        return super().get_paginated_response(serializer.data)
    
    def __get_page_size_from_request(self, request):
        page_size = request.query_params.get('page_size')
        
        if page_size and not page_size.isnumeric():
            raise NotAcceptable(detail=f'"page_size" must be integer.')
        
        return page_size or api_settings.PAGE_SIZE
