from flaskbb.auth.controllers import RegisterUser
from flaskbb.exceptions import ValidationError

try:
    from unittest import mock
except ImportError:
    import mock


class FakeForm(object):
    def __init__(self, username, email, password, valid=True):
        self.data = {'username': username, 'email': email,
                     'password': password}
        self.valid = valid
        self.errors = {}

    def validate_on_submit(self):
        return self.valid

    def __call__(self):
        return self


def stingy_registrar(username, email, password):
    raise ValidationError('Fails validation', 'username')


class TestRegisterUser(object):
    def setup(self):
        self.form = FakeForm('fred', 'fred', 'fred')
        self.generous_registrar = lambda *a, **k: None
        self.stingy_registrar = stingy_registrar

    def test_submit_invalid_form_data(self):
        self.form.valid = False
        controller = RegisterUser(self.form, self.generous_registrar, None, None)

        with mock.patch.object(RegisterUser, '_render') as render:
            controller.post()

        assert render.call_count == 1

    def test_submit_valid_form_data(self):
        controller = RegisterUser(self.form, self.generous_registrar, None, None)

        with mock.patch.object(RegisterUser, '_register_user') as register:
            controller.post()

        assert register.call_count == 1

    def test_fail_registration_validation(self):
        controller = RegisterUser(self.form, self.stingy_registrar, None, None)

        with mock.patch.object(RegisterUser, '_render') as render:
            controller.post()

        assert self.form.errors == {'username': ['Fails validation']}
        assert render.call_count == 1

    def test_pass_registration_validation(self):
        controller = RegisterUser(self.form, self.generous_registrar, None, None)

        with mock.patch.object(RegisterUser, '_redirect') as redirect:
            controller.post()

        assert redirect.call_count == 1