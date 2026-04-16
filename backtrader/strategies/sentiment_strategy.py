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
    Sentiment-based trading strategy.
    
    Buy Logic:
      - No position is open
      - Today's sentiment > 0.8
      
    Sell Logic:
      - A position exists
      - Today's sentiment < -0.5
    '''
    
    params = (
        ('buy_threshold', 0.8),
        ('sell_threshold', -0.5),
        ('prdata', True),
        ('prtrade', True),
    )
    
    def __init__(self):
        self.sentiment = self.data.sentiment
        
    def next(self):
        current_date = self.data.datetime.date(0)
        current_sentiment = self.data.sentiment[0]
        current_close = self.data.close[0]
        
        if self.p.prdata:
            print(f'DATE: {current_date}, CLOSE: {current_close:.2f}, SENTIMENT: {current_sentiment:.2f}')
        
        if not self.position:
            if current_sentiment > self.p.buy_threshold:
                if self.p.prdata:
                    print(f'  >>> BUY SIGNAL: sentiment ({current_sentiment:.2f}) > threshold ({self.p.buy_threshold})')
                self.buy()
        else:
            if current_sentiment < self.p.sell_threshold:
                if self.p.prdata:
                    print(f'  <<< SELL SIGNAL: sentiment ({current_sentiment:.2f}) < threshold ({self.p.sell_threshold})')
                self.sell()
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'  --- ORDER EXECUTED: BUY at {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            else:
                print(f'  --- ORDER EXECUTED: SELL at {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f'  --- ORDER FAILED: {order.getstatusname()}')
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        if self.p.prtrade:
            print(f'  === TRADE CLOSED: PnL Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')
