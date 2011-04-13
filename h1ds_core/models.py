"""
Do not delete this file.

Although h1ds_core  doesn't have any models,  for now anyway,  this file
needs to be present for django to emit a 'post_syncdb' signal,  which is
required  by  h1ds_core/management.py to  link static files to  the main 
project media directory (MEDIA_ROOT in settings.py).
"""
