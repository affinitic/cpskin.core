from plone import api

from Products.CMFCore.utils import getToolByName

from cpskin.core.interfaces import ICPSkinCoreWithMembersLayer


def user_logged_in(event):
    """
    When a user is logged in : define came_from
    Applies only if members-config profile has been installed
    """
    portal = api.portal.get()

    request = getattr(portal, "REQUEST", None)
    if not ICPSkinCoreWithMembersLayer.providedBy(request):
        return

    pm = getToolByName(portal, 'portal_membership')

    # needed because happens after notifying the event we are subscribed to :
    pm.createMemberArea()

    if 'citizens' in pm.getAuthenticatedMember().getGroups():
        home = pm.getHomeFolder()
        request.set('came_from', home.absolute_url())
        request.form['came_from'] = home.absolute_url()


def user_initial_logged_in(event):
    """
    When a user is logged in for the first time :
      - define came_from
      - restrict content
    Applies only if members-config profile has been installed
    """
    portal = api.portal.get()

    request = getattr(portal, "REQUEST", None)
    if not ICPSkinCoreWithMembersLayer.providedBy(request):
        return

    pm = getToolByName(portal, 'portal_membership')

    # needed because happens after notifying the event we are subscribed to :
    pm.createMemberArea()

    members = pm.getMembersFolder()
    if 'citizens' in pm.getAuthenticatedMember().getGroups():
        request = getattr(portal, "REQUEST", None)
        request.set('came_from', members.absolute_url())
        request.form['came_from'] = members.absolute_url()

    home = pm.getHomeFolder()
    if home is None:
        return

    # Restrict content
    local_roles = members.getLocallyAllowedTypes()
    home.setConstrainTypesMode(1)
    home.setLocallyAllowedTypes(local_roles)
    home.setImmediatelyAddableTypes(local_roles)
