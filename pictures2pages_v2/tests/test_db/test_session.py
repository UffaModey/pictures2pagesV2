import pytest
import unittest.mock as mock
from sqlalchemy.orm.session import Session
from pictures2pages_v2.app.db.session import session_scope


def test_session_scope():
    with session_scope() as session:
        assert isinstance(session, Session)


@mock.patch("pictures2pages_v2.app.db.session.SessionLocal")
def test_session_scope_fail(mocked_session_local_cls):
    mocked_session_local_cls.return_value.commit.side_effect = Exception("dummy")
    with pytest.raises(Exception) as e:
        with session_scope():
            pass
    mocked_session_local_cls.return_value.commit.assert_called_once()
    mocked_session_local_cls.return_value.rollback.assert_called_once()
    mocked_session_local_cls.return_value.close.assert_called_once()
    assert str(e.value) == "dummy"
