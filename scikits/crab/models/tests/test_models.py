import numpy as np
from numpy.testing import assert_array_equal

from nose.tools import assert_raises, assert_equals

from ..basic_models import DictPreferenceDataModel
from ..utils import UserNotFoundError, ItemNotFoundError

#Simple Movies DataSet

movies = {'Marcel Caraciolo': {'Lady in the Water': 2.5,
                               'Snakes on a Plane': 3.5,
                               'Just My Luck': 3.0,
                               'Superman Returns': 3.5,
                               'You, Me and Dupree': 2.5,
                               'The Night Listener': 3.0},
          'Luciana Nunes': {'Lady in the Water': 3.0,
                            'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5,
                            'Superman Returns': 5.0,
                            'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
          'Leopoldo Pires': {'Lady in the Water': 2.5,
                             'Snakes on a Plane': 3.0,
                             'Superman Returns': 3.5,
                             'The Night Listener': 4.0},
          'Lorena Abreu': {'Snakes on a Plane': 3.5,
                           'Just My Luck': 3.0,
                           'The Night Listener': 4.5,
                           'Superman Returns': 4.0,
                           'You, Me and Dupree': 2.5},
          'Steve Gates': {'Lady in the Water': 3.0,
                          'Snakes on a Plane': 4.0,
                          'Just My Luck': 2.0,
                          'Superman Returns': 3.0,
                          'The Night Listener': 3.0,
                          'You, Me and Dupree': 2.0},
          'Sheldom': {'Lady in the Water': 3.0,
                      'Snakes on a Plane': 4.0,
                      'The Night Listener': 3.0,
                      'Superman Returns': 5.0,
                      'You, Me and Dupree': 3.5},
          'Penny Frewman': {'Snakes on a Plane': 4.5,
                            'You, Me and Dupree': 1.0,
                            'Superman Returns': 4.0},
          'Maria Gabriela': {}}


def test_basic_methods_DictPreferenceDataModel():
    #Empty Dataset
    model = DictPreferenceDataModel({})
    assert_equals(model.dataset, {})

    assert_array_equal(np.array([]), model.user_ids())
    assert_array_equal(np.array([]), model.item_ids())
    assert_equals(True, model.has_preference_values())
    assert_equals(0, model.users_count())
    assert_equals(0, model.items_count())
    assert_equals(-np.inf, model.maximum_preference_value())
    assert_equals(np.inf, model.minimum_preference_value())

    #DataSet
    model = DictPreferenceDataModel(movies)
    assert_equals(model.dataset, movies)
    assert_array_equal(np.array(['Leopoldo Pires', 'Lorena Abreu',
                                 'Luciana Nunes', 'Marcel Caraciolo',
                                 'Maria Gabriela', 'Penny Frewman', 'Sheldom',
                                 'Steve Gates'],
                                dtype='|S16'),
                                model.user_ids())

    assert_array_equal(np.array(['Just My Luck', 'Lady in the Water',
                                 'Snakes on a Plane', 'Superman Returns',
                                 'The Night Listener', 'You, Me and Dupree']),
                                model.item_ids())

    assert_equals(True, model.has_preference_values())
    assert_equals(8, model.users_count())
    assert_equals(6, model.items_count())
    assert_equals(5.0, model.maximum_preference_value())
    assert_equals(1.0, model.minimum_preference_value())

    assert_array_equal(np.array([('Just My Luck', 3.0),
                                 ('Lady in the Water', 2.5),
                                 ('Snakes on a Plane', 3.5),
                                 ('Superman Returns', 3.5),
                                 ('The Night Listener', 3.0),
                                 ('You, Me and Dupree', 2.5)],
                                dtype=[('item_ids', '|S35'),
                                       ('preferences', '<f8')]),
                                model['Marcel Caraciolo'])

    elements = [pref for pref in model]
    assert_equals('Leopoldo Pires', elements[0][0])

    assert_array_equal(np.array([('Lady in the Water', 2.5),
                                 ('Snakes on a Plane', 3.0),
                                 ('Superman Returns', 3.5),
                                 ('The Night Listener', 4.0)],
                                dtype=[('item_ids', '|S35'),
                                       ('preferences', '<f8')]),
                                elements[0][1])


def test_preferences_from_user_exists_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    #ordered by item_id
    assert_array_equal(np.array([('Just My Luck', 3.0),
                                 ('Snakes on a Plane', 3.5),
                                 ('Superman Returns', 4.0),
                                 ('The Night Listener', 4.5),
                                 ('You, Me and Dupree', 2.5)],
                                dtype=[('item_ids', '|S35'),
                                       ('preferences', '<f8')]),
                                model.preferences_from_user('Lorena Abreu'))

    #ordered by rating (reverse)
    assert_array_equal(np.array([('The Night Listener', 4.5),
                                 ('Superman Returns', 4.0),
                                 ('Snakes on a Plane', 3.5),
                                 ('Just My Luck', 3.0),
                                 ('You, Me and Dupree', 2.5)],
                                dtype=[('item_ids', '|S35'),
                                       ('preferences', '<f8')]),
                                model.preferences_from_user('Lorena Abreu',
                                order_by_id=False))


def test_preferences_from_user_exists_no_preferences_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    assert_array_equal(np.array([], dtype=[('item_ids', '|S35'),
                                           ('preferences', '<f8')]),
                       model.preferences_from_user('Maria Gabriela'))


def test_preferences_from_user_non_existing_user_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    assert_raises(UserNotFoundError, model.preferences_from_user, 'Flavia')


def test_item_ids_from_user_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    assert_array_equal(np.array(['Just My Luck', 'Lady in the Water',
                                 'Snakes on a Plane', 'Superman Returns',
                                 'The Night Listener', 'You, Me and Dupree'],
                                dtype='|S18'),
                                model.items_from_user('Marcel Caraciolo'))


def test_preferences_for_item_existing_item_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    #ordered by item_id
    assert_array_equal(np.array([('Leopoldo Pires', 3.5),
                                 ('Lorena Abreu', 4.0), ('Luciana Nunes', 5.0),
                                 ('Marcel Caraciolo', 3.5),
                                 ('Penny Frewman', 4.0), ('Sheldom', 5.0),
                                 ('Steve Gates', 3.0)],
                                dtype=[('user_ids', '|S35'),
                                       ('preferences', '<f8')]),
                                model.preferences_for_item('Superman Returns'))

    #ordered by rating (reverse)
    assert_array_equal(np.array([('Luciana Nunes', 5.0), ('Sheldom', 5.0),
                                 ('Penny Frewman', 4.0), ('Lorena Abreu', 4.0),
                                 ('Leopoldo Pires', 3.5),
                                 ('Marcel Caraciolo', 3.5),
                                 ('Steve Gates', 3.0)],
                                dtype=[('user_ids', '|S35'),
                                       ('preferences', '<f8')]),
                                model.preferences_for_item('Superman Returns',
                                                           order_by_id=False))


def test_preferences_for_item_existing_item_no_preferences_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    assert_array_equal(np.array([],
                                dtype=[('item_ids', '|S35'),
                                       ('preferences', '<f8')]),
                       model.preferences_for_item, 'The Night Listener')


def test_preferences_for_item_non_existing_item_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    assert_raises(ItemNotFoundError, model.preferences_for_item,
                  'Back to the future')


def test_preference_value_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    assert_equals(3.5, model.preference_value('Marcel Caraciolo',
                                              'Superman Returns'))


def test_preference_value__invalid_DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    assert_raises(UserNotFoundError, model.preference_value,
                  'Flavia', 'Superman Returns')
    assert_raises(ItemNotFoundError, model.preference_value,
                  'Marcel Caraciolo', 'Back to the future')
    assert_equals(np.inf, model.preference_value('Maria Gabriela',
                                                 'The Night Listener'))


def test_set_preference_value_DictPreferenceDataModel():
    #Add
    model = DictPreferenceDataModel(movies)
    model.set_preference('Maria Gabriela', 'Superman Returns', 2.0)
    assert_equals(2.0,
                  model.preference_value('Maria Gabriela', 'Superman Returns'))

    #Edit
    model = DictPreferenceDataModel(movies)
    model.set_preference('Marcel Caraciolo', 'Superman Returns', 1.0)
    assert_equals(1.0, model.preference_value('Marcel Caraciolo',
                                              'Superman Returns'))

    #invalid
    assert_raises(UserNotFoundError,model.set_preference,'Carlos','Superman Returns', 2.0)
    #assert_raises(ItemNotFoundError,model.set_preference,'Marcel Caraciolo','Indiana Jones', 1.0)

def test_remove_preference_value__DictPreferenceDataModel():
    model = DictPreferenceDataModel(movies)
    model.remove_preference('Maria Gabriela', 'Superman Returns')
    assert_equals(np.inf,
                  model.preference_value('Maria Gabriela', 'Superman Returns'))
    assert_raises(ItemNotFoundError, model.remove_preference,
                  'Marcel Caraciolo',
                  'Indiana Jones')
