



class PreventAuthForLoggedInMiddleware:
    '''
    Docstring for PreventAuthForLoggedInMiddleware
      :     if User is Already logged in and manualy tries to hit /accounts/google/login/ Url then
            they will be redirected to home
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path.startswith("/accounts/google/login"):
            from django.shortcuts import redirect
            return redirect("homecontrol:dashboard")

        return self.get_response(request)
