from django.contrib.auth import get_user_model


class CustomerUserTests:
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="dave", email="dave@email.com", password="testpass123"
        )
        assert user.username == "dave2"
