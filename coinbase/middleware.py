from django import shortcuts

class Redirect(Exception):
    def __init__(self, url):
        self.url = url

def redirect(url):
    red = Redirect(url)

class RedirectMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, Redirect):
            return shortcuts.redirect(exception.url)