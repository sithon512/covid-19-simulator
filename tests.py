from mixer.backend.sqlalchemy import Mixer

import unittest

mixer = Mixer(session=session, commit=True)
