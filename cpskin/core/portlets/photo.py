# -*- coding: utf-8 -*-
from plone import api
from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IPhotoPortlet(IPortletDataProvider):
    """
    Photo portlet interface
    """


class Assignment(base.Assignment):
    implements(IPhotoPortlet)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('photo.pt')

    @property
    def available(self):
        """
        Portlet should be available from the 3 level of navigation
        """
        contextPhyPath = self.context.getPhysicalPath()
        portalPhyPath = api.portal.get().getPhysicalPath()
        path = [elem for elem in list(contextPhyPath) if elem not in list(portalPhyPath)]
        depth = len(path)
        if depth < 2:
            return False
        return True


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
