import pytest
from sqlalchemy.exc import IntegrityError
from types import SimpleNamespace
import ckan.model as model
from ckan.tests import factories
from ckan.plugins import toolkit
from ckanext.saml2auth.views.saml2auth import _get_user_by_email


@pytest.fixture
def tdv_data():
    """TestDatasetViews setup data"""
    obj = SimpleNamespace()
    obj.user1 = factories.User(
        email='user1@example.com',
        plugin_extras={'saml2auth': {'saml_id': 'saml_id1'}}
    )
    obj.user2 = factories.User(
        email='user2@example.com',
        plugin_extras={'saml2auth': {'saml_id': 'saml_id2'}}
    )
    return obj


@pytest.mark.usefixtures(u'clean_db', u'clean_index')
@pytest.mark.ckan_config(u'ckan.plugins', u'saml2auth')
class TestDatasetViews(object):
    def test_get_user_by_email_empty(self, tdv_data):
        """ The the function _get_user_by_email for empty response """
        ret = _get_user_by_email('user3@example.com')
        assert ret is None

    def test_get_user_by_email_ok(self, tdv_data):
        """ The the function _get_user_by_email for empty response """
        ret = _get_user_by_email(tdv_data.user1['email'])
        assert ret is not None
        assert ret['email'] == tdv_data.user1['email']

    @pytest.mark.skipif(
        toolkit.check_ckan_version(min_version='2.12'),
        reason='CKAN 2.12+ enforces a case-insensitive unique email index'
    )
    def test_get_user_by_email_multiple(self, tdv_data):
        """ The the function _get_user_by_email for duplicated emails
            CKAN < 2.12 allows the same email with a different case """
        # Generate a duplciate email
        user2 = model.User.get(tdv_data.user2['id'])
        user2.email = tdv_data.user1['email'].upper()
        model.Session.commit()

        with pytest.raises(toolkit.ValidationError):
            _get_user_by_email(tdv_data.user1['email'])

    @pytest.mark.skipif(
        not toolkit.check_ckan_version(min_version='2.12'),
        reason='Only CKAN 2.12+ enforces a case-insensitive unique email index'
    )
    def test_get_user_by_email_multiple_rejected_by_db(self, tdv_data):
        """ CKAN 2.12+ rejects duplicated emails (any case) for active
            users at the database level, so _get_user_by_email can never
            find multiple active users with the same email """
        user2 = model.User.get(tdv_data.user2['id'])
        user2.email = tdv_data.user1['email'].upper()
        with pytest.raises(IntegrityError):
            model.Session.commit()
        model.Session.rollback()

        ret = _get_user_by_email(tdv_data.user1['email'])
        assert ret is not None
        assert ret['id'] == tdv_data.user1['id']

    @pytest.mark.skipif(
        not toolkit.check_ckan_version(min_version='2.12'),
        reason='Only CKAN 2.12+ enforces a case-insensitive unique email index'
    )
    def test_get_user_by_email_multiple_deleted(self, tdv_data):
        """ The the function _get_user_by_email for duplicated emails
            The CKAN 2.12+ index only covers active users, so a deleted
            user can still share an email with an active one """
        user2 = model.User.get(tdv_data.user2['id'])
        user2.state = 'deleted'
        user2.email = tdv_data.user1['email'].upper()
        model.Session.commit()

        with pytest.raises(toolkit.ValidationError):
            _get_user_by_email(tdv_data.user1['email'])
