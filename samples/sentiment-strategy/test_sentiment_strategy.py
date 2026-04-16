#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Test script for Sentiment-based trading strategy
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import os
import sys

import backtrader as bt


def runstrat(args=None):
    args = parse_args(args)
    
    cerebro = bt.Cerebro()
    
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    datapath = args.data
    if not os.path.isabs(datapath):
        datapath = os.path.join(os.path.dirname(__file__), '..', '..', 'datas', datapath)
    
    data = bt.feeds.SentimentCSVData(
        dataname=datapath,
        dtformat='%Y-%m-%d',
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=6,
        sentiment=7,
    )
    
    cerebro.adddata(data)
    
    cerebro.addstrategy(bt.strategies.SentimentStrategy,
                        buy_threshold=args.buy_threshold,
                        sell_threshold=args.sell_threshold,
                        prdata=args.prdata,
                        prtrade=args.prtrade)
    
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    
    print('=' * 60)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('=' * 60)
    
    results = cerebro.run()
    
    print('=' * 60)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('=' * 60)
    
    if args.plot:
        cerebro.plot()


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sentiment Strategy Test')
    
    parser.add_argument('--data', required=False,
                        default='sentiment-test-data.csv',
                        metavar='CSV_FILE',
                        help='CSV data file with sentiment column')
    
    parser.add_argument('--buy-threshold', required=False, type=float,
                        default=0.8,
                        help='Buy when sentiment > this threshold')
    
    parser.add_argument('--sell-threshold', required=False, type=float,
                        default=-0.5,
                        help='Sell when sentiment < this threshold')
    
    parser.add_argument('--prdata', required=False, action='store_true',
                        default=True,
                        help='Print data bars')
    
    parser.add_argument('--prtrade', required=False, action='store_true',
                        default=True,
                        help='Print trade information')
    
    parser.add_argument('--plot', required=False, action='store_true',
                        default=False,
                        help='Plot the results')
    
    return parser.parse_args(pargs)


if __name__ == '__main__':
    runstrat()
