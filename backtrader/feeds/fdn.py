import datetime as dt
from dataclasses import dataclass

import backtrader as bt
from backtrader import TimeFrame, date2num

try:
    from fdnpy import FinancialDataClient
except ImportError as exc:
    FinancialDataClient = None
    _FDNPY_IMPORT_ERROR = exc
else:
    _FDNPY_IMPORT_ERROR = None


@dataclass(frozen=True)
class Bar:
    dt: dt.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    openinterest: float = 0.0


class FDNBacktraderAdapter:
    DAILY_METHODS = {
        'stock': 'get_stock_prices',
        'international_stock': 'get_international_stock_prices',
        'etf': 'get_etf_prices',
        'commodity': 'get_commodity_prices',
        'otc': 'get_otc_prices',
        'crypto': 'get_crypto_prices',
        'forex': 'get_forex_prices',
    }

    MINUTE_METHODS = {
        'stock': 'get_minute_prices',
        'etf': 'get_minute_prices',
        'crypto': 'get_crypto_minute_prices',
        'forex': 'get_forex_minute_prices',
    }

    def __init__(self, client):
        self.client = client

    def load_bars(self, identifier, asset_class, timeframe, fromdate=None, todate=None):
        asset_class = asset_class.lower().strip()
        fromdate = self._normalize_dt(fromdate)
        todate = self._normalize_dt(todate)

        if timeframe == TimeFrame.Days:
            method_name = self.DAILY_METHODS.get(asset_class)
            if method_name is None:
                raise ValueError('Unsupported daily asset_class: %r' % asset_class)
            rows = getattr(self.client, method_name)(identifier=identifier)
            bars = [self._parse_daily_row(row) for row in rows]

        elif timeframe == TimeFrame.Minutes:
            method_name = self.MINUTE_METHODS.get(asset_class)
            if method_name is None:
                raise ValueError('Unsupported minute asset_class: %r' % asset_class)
            if fromdate is None and todate is None:
                raise ValueError(
                    'Historical minute data requires fromdate and/or todate')
            start = fromdate or todate
            end = todate or fromdate
            start_date = min(start.date(), end.date())
            end_date = max(start.date(), end.date())
            bars = []
            current_date = start_date
            one_day = dt.timedelta(days=1)
            fetch = getattr(self.client, method_name)
            while current_date <= end_date:
                rows = fetch(identifier=identifier, date=current_date.isoformat())
                bars.extend(self._parse_minute_row(row) for row in rows)
                current_date += one_day
        else:
            raise ValueError(
                'Only TimeFrame.Days and TimeFrame.Minutes are supported directly. '
                'Use Backtrader resampling for other granularities.')

        return self._finalize_bars(bars, fromdate=fromdate, todate=todate)

    @staticmethod
    def _parse_daily_row(row):
        return Bar(
            dt=dt.datetime.strptime(row['date'], '%Y-%m-%d'),
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume'],
        )

    @staticmethod
    def _parse_minute_row(row):
        return Bar(
            dt=dt.datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S'),
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume'],
        )

    @staticmethod
    def _normalize_dt(value):
        if value is None or value.tzinfo is None:
            return value
        return value.astimezone(dt.timezone.utc).replace(tzinfo=None)

    @classmethod
    def _finalize_bars(cls, bars, fromdate=None, todate=None):
        unique_bars = {}
        for bar in bars:
            normalized_dt = cls._normalize_dt(bar.dt) or bar.dt
            unique_bars[normalized_dt] = Bar(
                dt=normalized_dt,
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
                openinterest=bar.openinterest,
            )

        ordered_bars = [unique_bars[key] for key in sorted(unique_bars)]

        if fromdate is not None:
            ordered_bars = [bar for bar in ordered_bars if bar.dt >= fromdate]
        if todate is not None:
            ordered_bars = [bar for bar in ordered_bars if bar.dt <= todate]

        return ordered_bars


class FinancialDataNetData(bt.feed.DataBase):
    params = (
        ('dataname', None),
        ('symbol', None),
        ('api_key', None),
        ('asset_class', 'stock'),
        ('timeframe', TimeFrame.Days),
        ('compression', 1),
        ('fromdate', None),
        ('todate', None),
    )

    def __init__(self):
        super(FinancialDataNetData, self).__init__()
        identifier = self.p.symbol or self.p.dataname
        if not identifier:
            raise ValueError('Provide a symbol or dataname identifier')
        if not self.p.api_key:
            raise ValueError('API key for FinancialData.Net is required, get one at https://financialdata.net/')
        if self.p.compression != 1:
            raise ValueError(
                'This feed returns native 1-day or 1-minute bars only. '
                'Use cerebro.resampledata(...) for other compression values.')

        self._identifier = str(identifier)
        self._bars = []
        self._bar_index = 0

    def start(self):
        super(FinancialDataNetData, self).start()

        if FinancialDataClient is None:
            raise ImportError(
                "fdnpy is required for FinancialDataNetData. Install it with 'pip install fdnpy'."
            )

        client = FinancialDataClient(api_key=self.p.api_key)
        adapter = FDNBacktraderAdapter(client)
        self._bars = adapter.load_bars(
            identifier=self._identifier,
            asset_class=self.p.asset_class,
            timeframe=self.p.timeframe,
            fromdate=self.p.fromdate,
            todate=self.p.todate,
        )
        self._bar_index = 0

    def stop(self):
        self._bars = []
        self._bar_index = 0
        super(FinancialDataNetData, self).stop()

    def _load(self):
        if self._bar_index >= len(self._bars):
            return False

        bar = self._bars[self._bar_index]
        self._bar_index += 1

        self.lines.datetime[0] = date2num(bar.dt)
        self.lines.open[0] = bar.open
        self.lines.high[0] = bar.high
        self.lines.low[0] = bar.low
        self.lines.close[0] = bar.close
        self.lines.volume[0] = bar.volume
        self.lines.openinterest[0] = bar.openinterest
        return True


__all__ = ['Bar', 'FDNBacktraderAdapter', 'FinancialDataNetData']
