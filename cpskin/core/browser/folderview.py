# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from plone import api
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from cpskin.core.interfaces import IFolderViewSelectedContent, \
                                   IFolderViewWithBigImages

from cpskin.locales import CPSkinMessageFactory as _
import httpagentparser

ADDABLE_TYPES = ['Collection', 'Document', 'Folder']


class FolderView(BrowserView):

    def _redirect(self, msg=''):
        if self.request:
            if msg:
                api.portal.show_message(message=msg,
                                        request=self.request,
                                        type='info')
            self.request.response.redirect(self.context.absolute_url())
        return msg

    def _get_real_context(self):
        context = self.context
        plone_view = getMultiAdapter((context, self.request), name="plone")
        if plone_view.isDefaultPageInFolder():
            context = aq_parent(context)
        context = aq_inner(context)
        return context

    def hasEffectiveDate(self, obj):
        """
        Check if object has a correct effective date
        If None, you get 01/01/1000 and strftime cannot convert it
        """
        effective = obj.effective
        if effective.year() < 1900:
            return False
        return True

    def isFolderViewActivated(self, context=None):
        """
        Check if folderview is activated on context
        """
        if context is None:
            context = self.context
        layout = context.getLayout()
        if layout == 'folderview':
            return True
        return False

    def can_configure(self):
        """
        Check if folderview can be configured on context
        """
        context = self.context
        if not IFolderish.providedBy(context):
            return False
        alreadyActivated = self.isFolderViewActivated()
        return (not alreadyActivated)

    def configure(self):
        """
        Configure folders and collections for folderview
        """
        context = self.context
        configure_folderviews(context)
        api.portal.show_message(message=_(u"Vue index avec collections configurée."),
                                request=self.request,
                                type='info')
        self.request.response.redirect(context.absolute_url())
        return ''

    def getResults(self, content):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        brains = content.results()
        results = {'sticky-results': [],
                   'standard-results': []}
        for brain in brains:
            if portal_catalog.getIndexDataForRID(brain.getRID())['is_sticky']:
                results['sticky-results'].append(brain)
            else:
                results['standard-results'].append(brain)
        if not results['sticky-results'] and not results['standard-results']:
            return None
        return results

    def getContents(self):
        brains = self.searchSelectedContent()
        objects = [brain.getObject() for brain in brains]
        realObjects = []
        for obj in objects:
            if obj.portal_type == 'Folder':
                if obj.getDefaultPage() is not None:
                    realObject = getattr(obj, obj.getDefaultPage())
                    realObjects.append(realObject)
                else:
                    continue
            else:
                realObjects.append(obj)
        return realObjects

    def isBigImage(self, number, results, resultType):
        """
        Check if image should be big depending on position and result type
        (sticky / non-sticky)
        """
        if not self.bigImagesAreUsed():
            return False
        if resultType == 'sticky-results' and number < 5:
            return True
        elif resultType == 'standard-results' and \
             number < 5 - len(results['sticky-results']):
            return True
        return False

    def getThumbSize(self, obj, isBigImage=False):
        prefix = 'image'
        thumbSize = 'thumb'
        if getattr(obj, 'hasContentLeadImage', None):
            prefix = 'leadImage'
        if isBigImage:
            thumbSize = 'mini'
        return '%s_%s' % (prefix, thumbSize)

    def searchSelectedContent(self):
        path = '/'.join(self.context.getPhysicalPath())
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        queryDict = {}
        queryDict['path'] = {'query': path, 'depth': 1}
        queryDict['portal_type'] = ADDABLE_TYPES
        queryDict['object_provides'] = IFolderViewSelectedContent.__identifier__
        queryDict['sort_on'] = 'getObjPositionInParent'
        results = portal_catalog.searchResults(queryDict)
        return results

    def hasFlexSlider(self):
        """
        Check if flexslider is available and installed
        """
        try:
            from cpskin.slider.interfaces import ICPSkinSliderLayer
        except ImportError:
            return False
        else:
            request = getattr(self.context, "REQUEST", None)
            if ICPSkinSliderLayer.providedBy(request):
                return True
            return False

    def is_browser_compatible(self):
        results = True
        request = getattr(self.context, "REQUEST", None)
        http_user_agent = request.getHeader('HTTP_USER_AGENT')
        browser_user_agent = httpagentparser.detect(http_user_agent)
        if browser_user_agent:
            browser = browser_user_agent.get('browser')
            if browser:
                if 'Internet Explorer' in browser.get('name'):
                    results = int(browser['version'].split('.')[0]) >= 9
        return results

    def addContent(self):
        """
        Mark content to add it to folder view
        """
        context = self._get_real_context()
        alsoProvides(context, IFolderViewSelectedContent)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Contenu ajouté à la vue index.'))

    def removeContent(self):
        """
        Unmark content to remove it from folder view
        """
        context = self._get_real_context()
        noLongerProvides(context, IFolderViewSelectedContent)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Contenu retiré de la vue index.'))

    def isEligibleContent(self):
        context = self._get_real_context()
        if context.portal_type not in ADDABLE_TYPES:
            return False
        parent = aq_parent(context)
        if not self.isFolderViewActivated(parent):
            return False
        return True

    def canAddContent(self):
        if not self.isEligibleContent():
            return False
        context = self._get_real_context()
        if IFolderViewSelectedContent.providedBy(context):
            return False
        return True

    def canRemoveContent(self):
        if not self.isEligibleContent():
            return False
        context = self._get_real_context()
        if not IFolderViewSelectedContent.providedBy(context):
            return False
        return True

    def canUseBigImages(self):
        """
        Check if big images can be used on folder view
        """
        if not self.isFolderViewActivated():
            return False
        context = self._get_real_context()
        return (not IFolderViewWithBigImages.providedBy(context))

    def bigImagesAreUsed(self):
        context = self._get_real_context()
        return IFolderViewWithBigImages.providedBy(context)

    def canStopBigImagesUse(self):
        """
        Check if big images are used on folder view
        """
        if not self.isFolderViewActivated():
            return False
        return (self.bigImagesAreUsed())

    def useBigImages(self):
        """
        Use big images for first elements on folder view
        """
        context = self._get_real_context()
        alsoProvides(context, IFolderViewWithBigImages)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Big images are now used on this folder view.'))

    def stopBigImagesUse(self):
        """
        Use using big images for first elements on folder view
        """
        context = self._get_real_context()
        noLongerProvides(context, IFolderViewWithBigImages)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Big images are not used anymore on this folder view.'))

    def slider_config(self):
        portal_registry = getToolByName(self.context, 'portal_registry')
        slider_timer = portal_registry['cpskin.core.interfaces.ICPSkinSettings.slider_timer']
        auto_play_slider = portal_registry['cpskin.core.interfaces.ICPSkinSettings.auto_play_slider']
        config = """
        (function($) {
             "use strict";
             var animation = "slide";
             // IE 9 does not support 'slide' animation
             if (navigator.sayswho === 'MSIE 9' || navigator.sayswho === 'IE 9')
             {
                animation = "fade";
             }
             $('#carousel').flexslider({
               animation: animation,
               controlNav: false,
               animationLoop: false,
               slideshow: false,
               itemWidth: 210,
               itemMargin: 5,
               asNavFor: '#slider'
             });
             $('#slider').flexslider({
               animation: animation,
               controlNav: false,
               animationLoop: true,
               slideshow: %(auto_play_slider)s,
               slideshowSpeed: %(slider_timer)s,
               sync: "#carousel"
             });
         })(jQuery);
        """ % {'auto_play_slider': auto_play_slider and 'true' or 'false',
               'slider_timer': slider_timer}
        return config


def configure_folderviews(context):
    """
    """
    existingIds = context.objectIds()
    portalPath = api.portal.get().getPhysicalPath()
    contextPath = '/'.join(context.getPhysicalPath()[len(portalPath):])
    if 'a-la-une' not in existingIds:
        folder = api.content.create(container=context,
                                    type='Folder',
                                    id='a-la-une',
                                    title="À la une")
        alsoProvides(folder, IFolderViewSelectedContent)
        collection = api.content.create(container=folder,
                                        type='Collection',
                                        id='a-la-une',
                                        title="À la une")
        query = [{'i': 'hiddenTags',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': 'a-la-une'},
                  {'i': 'path',
                  'o': 'plone.app.querystring.operation.string.path',
                  'v': '/%s' % contextPath}]
        collection.setQuery(query)
        collection.setSort_on('effective')
        collection.setSort_reversed(True)
        collection.setLayout('folder_summary_view')
        folder.setDefaultPage('a-la-une')
    if 'actualites' not in existingIds:
        folder = api.content.create(container=context,
                                    type='Folder',
                                    id='actualites',
                                    title="Actualités")
        alsoProvides(folder, IFolderViewSelectedContent)
        collection = api.content.create(container=folder,
                                        type='Collection',
                                        id='actualites',
                                        title="Actualités")
        query = [{'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['News Item']},
                  {'i': 'path',
                  'o': 'plone.app.querystring.operation.string.path',
                  'v': '/%s' % contextPath}]
        collection.setQuery(query)
        collection.setSort_on('effective')
        collection.setSort_reversed(True)
        collection.setLayout('folder_summary_view')
        folder.setDefaultPage('actualites')
    if 'evenements' not in existingIds:
        folder = api.content.create(container=context,
                                    type='Folder',
                                    id='evenements',
                                    title="Événements")
        alsoProvides(folder, IFolderViewSelectedContent)
        collection = api.content.create(container=folder,
                                        type='Collection',
                                        id='evenements',
                                        title="Événements")
        query = [{'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['Event']},
                  {'i': 'path',
                  'o': 'plone.app.querystring.operation.string.path',
                  'v': '/%s' % contextPath}]
        collection.setQuery(query)
        collection.setSort_on('effective')
        collection.setSort_reversed(True)
        collection.setLayout('folder_summary_view')
        folder.setDefaultPage('evenements')

    context.setLayout('folderview')
