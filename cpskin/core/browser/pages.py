from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FrontPage(BrowserView):

    index = ViewPageTemplateFile('templates/frontpage.pt')


class HelpPage(BrowserView):

    index = ViewPageTemplateFile('templates/helppage.pt')
