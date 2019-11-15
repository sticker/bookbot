import pytest
import os
from datetime import datetime
from lib.reminder.reminder import Reminder

target = Reminder()

def test_remind_impression():
    assert target.remind_impression(elapsed_days=60) is not None

