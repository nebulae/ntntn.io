from config import *

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import users
from decimal import *

import logging


class DynamicPropertyMixin(object):
    """ Facilitates creating dynamic properties on ndb.Expando entities.
        Also works on ndb.Model derived classes! 
        Note: keyword args are passed on to the underlying ndb.XxxProperty() class
    """

    def is_prop(self, name):
        return name in self._properties

    def set_dynamic_prop(self, cls, name, value, **kwds):
        """ Creates a typed dynamic property.  This can be particularly useful for
            ndb.PickleProperty and ndb.JsonProperty types in order to take advantage
            of the datastore in/out conversions.

            Note: keyword args are passed on to the underlying ndb.XxxProperty() class
        """
        prop = cls(name, **kwds)
        prop._code_name = name
        self._properties[name] = prop
        prop._set_value(self, value)

    def set_unindexed_prop(self, name, value, **kwds):
        """ Creates a generic unindexed property which is required for Expando to store
            any ndb.BlobProperty() or derived class such as:
                ndb.TextProperty()
                ndb.PickleProperty()
                ndb.JsonProperty()
        """
        self.set_dynamic_prop(ndb.GenericProperty, name, value, indexed=False, **kwds)

    # --- The blob properties ---

    def set_blob_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.BlobProperty, name, value, **kwds)

    def set_text_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.TextProperty, name, value, **kwds)

    def set_pickle_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.PickleProperty, name, value, **kwds)

    def set_json_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.JsonProperty, name, value, **kwds)

    # --- Useful non-blob properties ---

    def set_string_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.StringProperty, name, value, **kwds)

    def set_integer_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.IntegerProperty, name, value, **kwds)

    def set_float_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.FloatProperty, name, value, **kwds)

    def set_datetime_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.DateTimeProperty, name, value, **kwds)

    def set_key_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.KeyProperty, name, value, **kwds)

    # --- Less useful non-blob properties ---

    def set_generic_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.GenericProperty, name, value, **kwds)

    def set_boolean_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.BooleanProperty, name, value, **kwds)

    def set_date_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.DateProperty, name, value, **kwds)

    def set_time_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.TimeProperty, name, value, **kwds)

    def set_user_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.UserProperty, name, value, **kwds)

    def set_geopt_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.GeoPtProperty, name, value, **kwds)

    def set_blobkey_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.BlobKeyProperty, name, value, **kwds)


def tokenize_autocomplete(phrase):
    a = []
    for word in phrase.split():
        j = 1
        while True:
            for i in range(len(word) - j + 1):
                a.append(word[i:i + j])
            if j == len(word):
                break
            j += 1
    return a


class CurrencyModel(ndb.IntegerProperty):
    def _validate(self, value):
        if not isinstance(value, (Decimal, float, str, unicode, int, long)):
            raise TypeError("value can't be converted to a Decimal.")

    def _to_base_type(self, value):
        return int(round(Decimal(value) * 100))

    def _from_base_type(self, value):
        return Decimal(value) / 100


class Meta(ndb.Expando, DynamicPropertyMixin):
    pass


class Log(ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    user_id = ndb.StringProperty(required=True)
    object_reference = ndb.KeyProperty()
    obj_old_value = ndb.JsonProperty()
    obj_new_value = ndb.JsonProperty()
    description = ndb.StringProperty()

class BaseModel(ndb.Model):
    active = ndb.BooleanProperty(default=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_modified = ndb.DateTimeProperty(auto_now=True)
    created_by_id = ndb.StringProperty(required=True)
    modified_by_id = ndb.StringProperty(required=True)
    computed_id = ndb.ComputedProperty(lambda self: self.key)
    classname = ndb.ComputedProperty(lambda self: self.__class__.__name__)
    data = ndb.StructuredProperty(Meta)
    image = ndb.BlobProperty()
    image_mimetype = ndb.StringProperty()

    def to_dict(self):
        orig_dict = super(BaseModel, self).to_dict()
        orig_dict['image'] = False if self.image is None else True
        return orig_dict

    def _pre_put_hook(self):     
        logging.info(self)
        self.modified_by_id = users.get_current_user().email()

    def _post_put_hook(self, future):
        logging.info(self)
        logging.info(future.get_result())

class Note(BaseModel):
    objid = ndb.KeyProperty()
    text = ndb.StringProperty()
