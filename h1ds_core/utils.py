from django.conf import settings

class BaseURLProcessor(object):
    def __init__(self, url=None, tree=None, shot=None, path=None):
        """takes url or components.

        maps to /tree/shot/path.
        Use a subclass of this to change mapping.

        """
        if url != None:
            url = self.remove_prefix(url)
            print url
            self.tree, self.shot, self.path = self.get_components_from_url(url)
            if tree != None and tree != self.tree:
                raise AttributeError
            if shot != None and shot != self.shot:
                raise AttributeError
            if path != None and path != self.path:
                raise AttributeError
        else:
            self.tree, self.shot, self.path = tree, shot, path

    def remove_prefix(self, url):
        if url.startswith("/"):
            url = url[1:]
        if hasattr(settings, "H1DS_DATA_PREFIX"):
            pref = settings.H1DS_DATA_PREFIX + "/"
            if url.startswith(pref):
                url = url[len(pref):]        
        return url

    def apply_prefix(self, url):
        if not url.startswith("/"):
            url = "/"+url
        if hasattr(settings, "H1DS_DATA_PREFIX"):
            if not url.startswith("/"+settings.H1DS_DATA_PREFIX+"/"):
                url = "/"+settings.H1DS_DATA_PREFIX+ url
        return url
    
    def get_components_from_url(self, url):
        t, s, p = url.split("/", 2)
        tree = self.deurlize_tree(t)
        shot = self.deurlize_shot(s)
        path = self.deurlize_path(p)
        return tree, shot, path
        
    def get_url(self):
        return self.apply_prefix("/".join([self.urlized_tree(),
                                           self.urlized_shot(),
                                           self.urlized_path()]))
        
    def urlized_tree(self):
        return self.tree

    def urlized_shot(self):
        return str(self.shot)

    def urlized_path(self):
        return self.path

    def deurlize_tree(self, url_tree):
        return url_tree

    def deurlize_shot(self, url_shot):
        return int(url_shot)

    def deurlize_path(self, url_path):
        return url_path
