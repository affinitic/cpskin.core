# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface

from cpskin.locales import CPSkinMessageFactory as _


class ICPSkinCoreLayer(Interface):
    """
    Marker interface that defines a ZTK browser layer.
    """


class ICPSkinCoreWithMembersLayer(Interface):
    """
    Marker interface that defines a ZTK browser layer.
    """


class IBannerActivated(Interface):
    """
    Marker interface to enable / disable banner viewlet
    """


class ILocalBannerActivated(Interface):
    """
    Marker interface to enable / disable banner viewlet
    """


class IMediaActivated(Interface):
    """
    Marker interface to enable / disable (multi)media viewlet
    """


class IFolderViewSelectedContent(Interface):
    """
    Marker interface to add / remove content to / from folder view
    """


class IFolderViewWithBigImages(Interface):
    """
    Marker interface to use big images on folder view
    """


class ICPSkinSettings(Interface):
    """
    Settings for CPSkin
    """
    load_page_menu = schema.Bool(
        title=_(u"Load page menu"),
        description=_(u"Is level 1 menu load page at click?"),
        required=False,
        default=False
    )


class IVideoCollection(Interface):
    """
    Marker interface for video collection used to viewlet multimedia
    """


class IAlbumCollection(Interface):
    """
    Marker interface for album collection used to viewlet multimedia
    """
