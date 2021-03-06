# -*- coding: utf-8 -*-
from binascii import b2a_qp
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.site.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode


class BaseTagsVocabulary(object):
    """Vocabulary factory listing all catalog keywords from specified tags"""
    implements(IVocabularyFactory)
    indexName = ''

    def __call__(self, context, query=None):
        site = getSite()
        self.catalog = getToolByName(site, "portal_catalog", None)
        if self.catalog is None:
            return SimpleVocabulary([])
        index = self.catalog._catalog.getIndex(self.indexName)

        def safe_encode(term):
            if isinstance(term, unicode):
                # no need to use portal encoding for transitional encoding from
                # unicode to ascii. utf-8 should be fine.
                term = term.encode('utf-8')
            return term

        # Vocabulary term tokens *must* be 7 bit values, titles *must* be
        # unicode
        items = [
            SimpleTerm(safe_unicode(i), b2a_qp(safe_encode(i)), safe_unicode(i))
            for i in index._index
            if query is None or safe_encode(query) in safe_encode(i)
        ]
        return SimpleVocabulary(items)


class IStandardTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from standard tags"""
    indexName = 'standardTags'


class IAmTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from I am tags"""
    indexName = 'iamTags'


class ISearchTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from I search tags"""
    indexName = 'isearchTags'


class HiddenTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from hidden tags"""
    indexName = 'hiddenTags'

    def __call__(self, context, query=None):
        voc = super(HiddenTagsVocabulary, self).__call__(context, query)
        # Add a-la-une term if it does not already exist, aka still not used for any document
        if u'a-la-une' not in voc.by_token:
            simpleTerms = [term for term in voc]
            simpleTerms.append(SimpleTerm(u'a-la-une', title=u'A la une'))
            voc = SimpleVocabulary(simpleTerms)
        return voc


IStandardTagsVocabularyFactory = IStandardTagsVocabulary()
IAmTagsVocabularyFactory = IAmTagsVocabulary()
ISearchTagsVocabularyFactory = ISearchTagsVocabulary()
HiddenTagsVocabularyFactory = HiddenTagsVocabulary()
