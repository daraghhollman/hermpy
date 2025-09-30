import datetime as dt
import typing

DateLike: typing.TypeAlias = dt.date | dt.datetime
DateOrDates: typing.TypeAlias = DateLike | typing.Sequence[DateLike]
