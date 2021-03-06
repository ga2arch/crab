#-*- coding:utf-8 -*-

"""
Several Basic Data models.

"""
# Authors: Marcel Caraciolo <marcel@muricoca.com>
# License: BSD Style


import numpy as np
from .base import BaseDataModel
from .utils import UserNotFoundError, ItemNotFoundError

###############################################################################
# DictDataModel


class DictPreferenceDataModel(BaseDataModel):
    '''Dictionary with preferences based Data model

    A DataModel backed by a python dict structured data. This class expects a
    simple dictionary where each element contains a userID, followed by itemID,
    followed by preference value and optional timestamp.

    {
        userID:{itemID:preference, itemID2:preference2},
        userID2:{itemID:preference3, itemID4:preference5},
    }

    Preference value is the parameter that the user simply expresses the degree
    of preference for an item.


    Parameters
    ----------

    dataset dict,shape = {
        userID:{itemID:preference, itemID2:preference2},
        userID2:{itemID:preference3, itemID4:preference5},
    }

    Methods
    ---------

    build_model() : self
        Build the model

    user_ids(): user_ids
         Return all user ids in the model, in order

    item_ids(): item_ids
        Return all item ids in the model, in order

    has_preference_values: bool
        Return True if this implementation actually it is not a 'boolean' data
        model, otherwise returns False.

    maximum_preference_value(): float
        Return the maximum preference value that is possible in the current
        problem domain being evaluated.

    minimum_preference_value(): float
        Return the minimum preference value that is possible in the current
        problem domain being evaluated

    preferences_from_user(user_id, order_by_id=True): numpy array of shape [(user_id,preference)]
        Return user's preferences, ordered by user ID (if order_by_id is True) 

    items_from_user(user_id): items_from_user : numpy array of shape [item_id,..]
         Return IDs of items user expresses a preference for

    preferences_for_item(item_id, order_by_id=True): preferences: numpy array of shape [(item_id,preference)]
         Return all existing Preferences expressed for that item,

    users_count():  n_users:  int
        Return total number of users known to the model.

    items_count(): n_items: int
        Return total number of items known to the model.

    set_preference( user_id, item_id, value): self
        Sets a particular preference (item plus rating) for a user.

    remove_preference(user_id,item_id): self
        Removes a particular preference for a user.

    Examples
    ---------
    >>> from scikits.crab.models.basic_models import DictPreferenceDataModel
    >>> model = DictPreferenceDataModel({})
    >>> #empty dataset
    >>> model.user_ids()
    array([], dtype=float64)
    >>> model.item_ids()
    array([], dtype=float64)
    >>> movies = {'Marcel Caraciolo': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, \
     'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, \
     'The Night Listener': 3.0}, \
     'Paola Pow': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, \
     'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, \
     'You, Me and Dupree': 3.5}, \
    'Leopoldo Pires': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, \
     'Superman Returns': 3.5, 'The Night Listener': 4.0}, \
    'Lorena Abreu': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, \
     'The Night Listener': 4.5, 'Superman Returns': 4.0, \
     'You, Me and Dupree': 2.5}, \
    'Steve Gates': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, \
     'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, \
     'You, Me and Dupree': 2.0}, \
    'Sheldom': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, \
     'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5}, \
    'Penny Frewman': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}, \
    'Maria Gabriela': {}}
    >>> model = DictPreferenceDataModel(movies)
    >>> #non-empty dataset
    >>> model.user_ids()
    array(['Leopoldo Pires', 'Lorena Abreu', 'Marcel Caraciolo',
               'Maria Gabriela', 'Paola Pow', 'Penny Frewman', 'Sheldom',
               'Steve Gates'],
              dtype='|S16')
    >>> model.item_ids()
    array(['Just My Luck', 'Lady in the Water', 'Snakes on a Plane',
               'Superman Returns', 'The Night Listener', 'You, Me and Dupree'],
              dtype='|S18')
    '''

    def __init__(self, dataset):
        BaseDataModel.__init__(self)
        self.dataset = dataset
        self.build_model()

    def __getitem__(self, user_id):
        return self.preferences_from_user(user_id)

    def __iter__(self):
        for index, user in enumerate(self.user_ids()):
            yield user, self[user]

    def build_model(self):
        '''
        Returns
        -------
        self:
             Build the data model
        '''

        self._user_ids = np.asanyarray(self.dataset.keys())
        self._user_ids.sort()

        self._item_ids = np.array([])
        for items in self.dataset.itervalues():
            self._item_ids = np.append(self._item_ids, items.keys())

        self._item_ids = np.unique(self._item_ids)
        self._item_ids.sort()

        self.max_pref = -np.inf
        self.min_pref = np.inf

        self.dataset_T = {}
        for user in self._user_ids:
            for item in self.dataset[user]:
                self.dataset_T.setdefault(item, {})
                self.dataset_T[item][user] = self.dataset[user][item]
                if self.dataset[user][item] > self.max_pref:
                    self.max_pref = self.dataset[user][item]
                if self.dataset[user][item] < self.min_pref:
                    self.min_pref = self.dataset[user][item]

    def user_ids(self):
        '''
        Returns
        -------
        self.user_ids:  numpy array of shape [n_user_ids]
                        Return all user ids in the model, in order
        '''
        return self._user_ids

    def item_ids(self):
        '''
        Returns
        -------
        self.item_ids:  numpy array of shape [n_item_ids]
                        Return all item ids in the model, in order
        '''
        return self._item_ids

    def preferences_from_user(self, user_id, order_by_id=True):
        '''
        Returns
        -------
        self.user_preferences : numpy array [(item_id,preference)]
                                Return user's preferences, ordered by user ID
                                (if order_by_id is True) or by the preference
                                values (if order_by_id is False), as an array.
        '''
        user_preferences = self.dataset.get(user_id, None)

        if user_preferences is None:
            raise UserNotFoundError

        user_preferences = user_preferences.items()

        if not order_by_id:
            user_preferences.sort(key=lambda user_pref: user_pref[1],
                                  reverse=True)
        else:
            user_preferences.sort(key=lambda user_pref: user_pref[0])

        return np.asanyarray(user_preferences,
                             dtype=[('item_ids', (str, 35)),
                                    ('preferences', float)])

    def items_from_user(self, user_id):
        '''
        Returns
        -------
        items_from_user : numpy array of shape [item_id,..]
                 Return IDs of items user expresses a preference for
        '''
        preferences = self.preferences_from_user(user_id)
        return [key for key, value in preferences]

    def preferences_for_item(self, item_id, order_by_id=True):
        '''
        Returns
        -------
        preferences: numpy array of shape [(item_id,preference)]
                     Return all existing Preferences expressed for that item,
        '''
        item_preferences = self.dataset_T.get(item_id, None)

        if item_preferences is None:
            raise ItemNotFoundError('Item not found.')

        item_preferences = item_preferences.items()

        if not order_by_id:
            item_preferences.sort(key=lambda item_pref: item_pref[1],
                                  reverse=True)
        else:
            item_preferences.sort(key=lambda item_pref: item_pref[0])

        return np.asanyarray(item_preferences,
                             dtype=[('user_ids', (str, 35)),
                                    ('preferences', float)])

    def preference_value(self, user_id, item_id):
        '''
        Returns
        -------
        preference:  float
                     Retrieves the preference value for a single user and item.
        '''
        preferences = self.dataset.get(user_id, None)
        if preferences is None:
            raise UserNotFoundError('user_id in the model not found')

        if item_id not in self.dataset_T:
            raise ItemNotFoundError

        return preferences.get(item_id, np.inf)

    def users_count(self):
        '''
        Returns
        --------
        n_users:  int
                  Return total number of users known to the model.
        '''
        return self._user_ids.size

    def items_count(self):
        '''
        Returns
        --------
        n_items:  int
                  Return total number of items known to the model.
        '''
        return self._item_ids.size

    def set_preference(self, user_id, item_id, value):
        '''
        Returns
        --------
        self
            Sets a particular preference (item plus rating) for a user.
        '''
        user_preferences = self.dataset.get(user_id, None)
        if user_preferences is None:
            raise UserNotFoundError('user_id in the model not found')
        
        #ALLOW NEW ITEMS
        #if item_id not in self.dataset_T:
        #    raise ItemNotFoundError
            
        self.dataset[user_id][item_id] = value
        self.build_model()

    def remove_preference(self, user_id, item_id):
        '''
        Returns
        --------
        self
            Removes a particular preference for a user.
        '''
        user_preferences = self.dataset.get(user_id, None)
        if user_preferences is None:
            raise UserNotFoundError('user_id in the model not found')

        if item_id not in self.dataset_T:
            raise ItemNotFoundError

        del self.dataset[user_id][item_id]
        self.build_model()

    def has_preference_values(self):
        '''
        Returns
        -------
        True/False:  bool
                     Return True if this implementation actually it is not a
                     'boolean' data model, otherwise returns False.
        '''
        return True

    def maximum_preference_value(self):
        '''
        Returns
        ---------
        self.max_preference:  float
                              Return the maximum preference value that is
                              possible in the current problem domain being
                              evaluated.
        '''
        return self.max_pref

    def minimum_preference_value(self):
        '''
        Returns
        ---------
        self.min_preference:  float
                              Returns the minimum preference value that is
                              possible in the current problem domain being
                              evaluated
        '''
        return self.min_pref
