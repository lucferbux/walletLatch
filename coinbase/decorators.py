#from django.core.exceptions import PermissionDenied
# from django.shortcuts import redirect

# def checkAccess(function):
#     def wrap(request, *args, **kwargs):
#         if not latch_interface.checkAccountId() or not wallet.checkCoinbaseClient():
#             return redirect('login')
#         elif latch_interface.checkLatch():
#             return redirect('latchlocked')
#         else:
#             return function(request, *args, **kwargs)

#     return wrap
