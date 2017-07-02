from __future__ import unicode_literals
from django.contrib.auth.models import User
<<<<<<< HEAD
=======
# from helper.models import Document,Order
from django.db import models
import datetime

# Create your models here.

ACTIVE = True
INACTIVE = False
# Trans_status

NOT_STARTED = 0  # assignment not started yet
ONGOING = 1  # assignment started not submitted to supervisor
APPROVING = 2  # assignment submitted to supervisor for approval
APPROVED = 3  # assignment approved, to status 5
DISAPPROVED = 4  # assignment disapproved, return to status 1
FINISHED = 5  # assignment approved and finished

TRANS_STATUS_CHOICE = (
    (NOT_STARTED, 'not_started'),
    (ONGOING, 'ongoing'),
    (APPROVING, 'approving'),
    (APPROVED, 'approved'),
    (DISAPPROVED, 'disapproved'),
    (FINISHED, 'finished')
)


class Translator(User):
>>>>>>> 30da62cc0b7892ecb223af46ba4595cb6a6bb074

class Translator(User):
    class Meta:
        proxy = True

    def get_name(self):
        name = self.first_name + ' ' + self.last_name
        if name is not ' ':
            return name
        return self.user.username




