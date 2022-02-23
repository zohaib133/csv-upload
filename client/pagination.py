from rest_framework.pagination import PageNumberPagination


class Paginate:
    def __init__(self, query, extract, start_index, limit):
        self.query = query
        self.extract = extract
        self.start_index = start_index
        self.limit = limit

    def paginate(self):
        try:
            total = self.query.count()
        except:
            total = len(self.query)

        upper_limit = min(total, self.start_index + self.limit)
        iteration = 0

        items = []
        key_finder = self.start_index + 1
        for item in self.query[self.start_index:upper_limit]:
            iteration = iteration + 1
            ext = self.extract(item)
            if ext is not None:
                items.append(ext)
                key_finder += 1

        return {
            'recordsTotal': total,
            'recordsFiltered': total,
            'data': items
        }


class CustomPagination(PageNumberPagination):

    def get_page_number(self, request, paginator):
        page_number = request.query_params.get(self.page_query_param, 0)
        page_number = int(page_number)
        page_number = page_number + 1
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        return page_number


class PaginationClass:
    def __init__(self, query_set, extract, request):
        self.paginator = CustomPagination()
        self.paginator.page_size = 100
        self.page = 1
        self.query_set = query_set
        self.extract = extract
        self.request = request

    def paginate(self):
        self.paginator.page_query_param = 'start'
        result_page = self.paginator.paginate_queryset(self.query_set, self.request)
        serializer = self.extract(result_page, many=True, context=self.request)
        data = self.paginator.get_paginated_response(serializer.data)

        return {
            'recordsTotal': data.data['count'],
            'recordsFiltered': data.data['count'],
            'data': data.data['results']
        }


class PaginateWithExtractedParameters:
    def __init__(self, query, extract, start_index, limit, **kwargs):
        self.query = query
        self.extract = extract
        self.start_index = start_index
        self.limit = limit
        self.kwargs = kwargs

    def paginate(self):
        try:
            total = self.query.count()
        except:
            total = len(self.query)

        upper_limit = min(total, self.start_index + self.limit)
        iteration = 0

        items = []
        key_finder = self.start_index + 1
        for item in self.query[self.start_index:upper_limit]:
            iteration = iteration + 1
            ext = self.extract(item, **self.kwargs)
            if ext is not None:
                items.append(ext)
                key_finder += 1

        return {
            'recordsTotal': total,
            'recordsFiltered': total,
            'data': items
        }
