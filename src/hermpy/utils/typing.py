import datetime as dt
from collections.abc import Sequence

DateLike: type = dt.date | dt.datetime
DateSequence = Sequence[DateLike]
