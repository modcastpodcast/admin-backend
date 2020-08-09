from starlette.responses import RedirectResponse, PlainTextResponse

from crawlerdetect import CrawlerDetect

from admin.route import Route
from admin.models import ShortURL

class ShortURLRedirect(Route):
    """
    Route for handling the redirection of short URLs.
    """
    name = "short_url"
    path = "/{short_code:str}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.crawler_detector = CrawlerDetect()

    async def get(self, request):
        """
        Redirect a short URL to the intended destination.
        """
        short_code = request.path_params["short_code"]

        short_link = await ShortURL.get(short_code)

        if short_link:
            if not self.crawler_detector.isCrawler(request.headers["User-Agent"]):
                await short_link.update(clicks=short_link.clicks + 1).apply()
            return RedirectResponse(short_link.long_url)
        else:
            return PlainTextResponse("Short code not found", status_code=404)
