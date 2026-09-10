"""Local-process coordination for the single-host SQLite installation."""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import tempfile
from django.conf import settings
from django.core.files import locks


@contextmanager
def email_delivery_lock(booking_id, field):
    # OS file locks do not hold a SQLite transaction during SMTP.
    # Shared DB across different machines requires distributed coordination.
    database = str(settings.DATABASES['default']['NAME'])
    scope = hashlib.sha256((str(getattr(settings, 'BASE_DIR', '')) + database).encode()).hexdigest()[:24]
    folder = Path(tempfile.gettempdir()) / ('najafdo-mail-' + scope)
    folder.mkdir(exist_ok=True)
    filename = hashlib.sha256(f'{booking_id}:{field}'.encode()).hexdigest() + '.lock'
    with (folder / filename).open('a+b') as handle:
        acquired = locks.lock(handle, locks.LOCK_EX | locks.LOCK_NB)
        try:
            yield bool(acquired)
        finally:
            if acquired:
                locks.unlock(handle)
