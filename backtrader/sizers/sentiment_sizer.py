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


class SentimentSizer(bt.Sizer):
    '''
    Dynamic position sizing based on smoothed sentiment value.
    
    The size is determined by the absolute value of the smoothed sentiment:
      - If abs(sentiment) >= extreme_threshold: use large_stake
      - If medium_threshold <= abs(sentiment) < extreme_threshold: use small_stake
      - If abs(sentiment) < medium_threshold: use 0 (no trade)
    
    This sizer expects the strategy to have an attribute `smoothed_sentiment`
    that provides the smoothed sentiment value (e.g., 5-day SMA).
    '''
    
    params = (
        ('extreme_threshold', 0.6),
        ('medium_threshold', 0.3),
        ('large_stake', 100),
        ('small_stake', 10),
    )
    
    def __init__(self):
        pass
    
    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.strategy.getposition(data)
        
        if not position:
            smoothed_sentiment = self._get_smoothed_sentiment()
            if smoothed_sentiment is None:
                return self.p.small_stake
            
            abs_sentiment = abs(smoothed_sentiment)
            
            if abs_sentiment >= self.p.extreme_threshold:
                size = self.p.large_stake
            elif abs_sentiment >= self.p.medium_threshold:
                size = self.p.small_stake
            else:
                size = 0
            
            max_possible = int(cash / data.close[0])
            size = min(size, max_possible)
            
            return size
        else:
            return position.size
    
    def _get_smoothed_sentiment(self):
        if hasattr(self.strategy, 'smoothed_sentiment'):
            try:
                return self.strategy.smoothed_sentiment[0]
            except (TypeError, IndexError):
                return None
        
        if hasattr(self.strategy, 'sentiment_sma'):
            try:
                return self.strategy.sentiment_sma[0]
            except (TypeError, IndexError):
                return None
        
        if hasattr(self.data, 'sentiment'):
            try:
                return self.data.sentiment[0]
            except (TypeError, IndexError):
                return None
        
        return None
