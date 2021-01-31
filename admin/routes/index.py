from starlette.responses import RedirectResponse

from admin.route import Route

class Index(Route):
    """
    Route for the index page, all it does is redirects.
    """
    name = "index"
    path = "/"

    async def get(self, request):
        """
        Permanently redirect requests to modcast.network.
        """
        return RedirectResponse("https://modcast.network", 301)
