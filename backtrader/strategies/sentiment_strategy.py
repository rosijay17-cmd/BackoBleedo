#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2023 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt


class SentimentStrategy(bt.Strategy):
    '''
    Sentiment-based trading strategy with SMA smoothing.
    
    Features:
      - 5-day SMA smoothing on sentiment data to reduce noise
      - Uses smoothed sentiment for trading decisions
      - Exposes smoothed sentiment for dynamic position sizing (SentimentSizer)
    
    Buy Logic:
      - No position is open
      - Smoothed sentiment > buy_threshold
      
    Sell Logic:
      - A position exists
      - Smoothed sentiment < sell_threshold
    '''
    
    params = (
        ('buy_threshold', 0.5),
        ('sell_threshold', -0.3),
        ('sma_period', 5),
        ('use_smoothed', True),
        ('prdata', True),
        ('prtrade', True),
    )
    
    def __init__(self):
        self.raw_sentiment = self.data.sentiment
        
        if self.p.use_smoothed:
            self.sentiment_sma = bt.indicators.SMA(
                self.data.sentiment,
                period=self.p.sma_period
            )
            self.smoothed_sentiment = self.sentiment_sma
        else:
            self.smoothed_sentiment = self.raw_sentiment
        
        self.sentiment = self.smoothed_sentiment
        
    def next(self):
        current_date = self.data.datetime.date(0)
        current_raw_sentiment = self.raw_sentiment[0]
        current_close = self.data.close[0]
        
        try:
            current_smoothed = self.smoothed_sentiment[0]
        except (TypeError, IndexError):
            current_smoothed = None
        
        if self.p.prdata:
            if current_smoothed is not None:
                print(f'DATE: {current_date}, CLOSE: {current_close:.2f}, '
                      f'RAW_SENT: {current_raw_sentiment:.2f}, '
                      f'SMOOTHED: {current_smoothed:.2f}')
            else:
                print(f'DATE: {current_date}, CLOSE: {current_close:.2f}, '
                      f'RAW_SENT: {current_raw_sentiment:.2f}')
        
        if current_smoothed is None:
            return
        
        if not self.position:
            if current_smoothed > self.p.buy_threshold:
                if self.p.prdata:
                    print(f'  >>> BUY SIGNAL: smoothed sentiment ({current_smoothed:.2f}) > threshold ({self.p.buy_threshold})')
                self.buy()
        else:
            if current_smoothed < self.p.sell_threshold:
                if self.p.prdata:
                    print(f'  <<< SELL SIGNAL: smoothed sentiment ({current_smoothed:.2f}) < threshold ({self.p.sell_threshold})')
                self.sell()
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'  --- ORDER EXECUTED: BUY {order.executed.size} shares at {order.executed.price:.2f}, '
                      f'Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            else:
                print(f'  --- ORDER EXECUTED: SELL {abs(order.executed.size)} shares at {order.executed.price:.2f}, '
                      f'Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f'  --- ORDER FAILED: {order.getstatusname()}')
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        if self.p.prtrade:
            print(f'  === TRADE CLOSED: PnL Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')
