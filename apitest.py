from api.request_helpers import RequestHelpers
from api.request_url import RequestURL



if __name__ == '__main__':
    reqHelpers = RequestHelpers()
    reqHelpers.url = 'http://27.78.16.56:8020/v1/template_logs.json'
    res = reqHelpers.get_test()