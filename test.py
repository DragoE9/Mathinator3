import datetime
from tzlocal import get_localzone

EST = datetime.timezone(datetime.timedelta(hours=-5))
UTC = datetime.timezone.utc

one = datetime.datetime(year=2024,month=10,day=5,hour=1,tzinfo=EST)
two = datetime.datetime(year=2024,month=10,day=5,hour=6,tzinfo=UTC)

print(one.astimezone(UTC))

