#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Test script for Sentiment-based trading strategy with SMA smoothing
# and dynamic position sizing
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
                        sma_period=args.sma_period,
                        use_smoothed=args.use_smoothed,
                        prdata=args.prdata,
                        prtrade=args.prtrade)
    
    if args.use_dynamic_sizer:
        print(f'Using SentimentSizer: extreme_threshold={args.extreme_threshold}, '
              f'medium_threshold={args.medium_threshold}, '
              f'large_stake={args.large_stake}, small_stake={args.small_stake}')
        cerebro.addsizer(bt.sizers.SentimentSizer,
                         extreme_threshold=args.extreme_threshold,
                         medium_threshold=args.medium_threshold,
                         large_stake=args.large_stake,
                         small_stake=args.small_stake)
    else:
        print(f'Using FixedSize sizer: stake={args.fixed_stake}')
        cerebro.addsizer(bt.sizers.FixedSize, stake=args.fixed_stake)
    
    print('=' * 60)
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    print(f'SMA Period: {args.sma_period}')
    print(f'Buy Threshold: {args.buy_threshold}')
    print(f'Sell Threshold: {args.sell_threshold}')
    print(f'Use Smoothed Sentiment: {args.use_smoothed}')
    print(f'Use Dynamic Sizer: {args.use_dynamic_sizer}')
    print('=' * 60)
    
    results = cerebro.run()
    
    print('=' * 60)
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
    print(f'Portfolio Return: {(cerebro.broker.getvalue() - 100000.0):.2f}')
    print('=' * 60)
    
    if args.plot:
        cerebro.plot()


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sentiment Strategy Test with SMA Smoothing and Dynamic Position Sizing')
    
    parser.add_argument('--data', required=False,
                        default='sentiment-test-data.csv',
                        metavar='CSV_FILE',
                        help='CSV data file with sentiment column')
    
    parser.add_argument('--buy-threshold', required=False, type=float,
                        default=0.5,
                        help='Buy when smoothed sentiment > this threshold')
    
    parser.add_argument('--sell-threshold', required=False, type=float,
                        default=-0.3,
                        help='Sell when smoothed sentiment < this threshold')
    
    parser.add_argument('--sma-period', required=False, type=int,
                        default=5,
                        help='Period for SMA smoothing of sentiment')
    
    parser.add_argument('--no-smooth', required=False, action='store_false',
                        default=True,
                        dest='use_smoothed',
                        help='Disable SMA smoothing (use raw sentiment)')
    
    parser.add_argument('--no-dynamic-sizer', required=False, action='store_false',
                        default=True,
                        dest='use_dynamic_sizer',
                        help='Disable dynamic position sizing (use fixed size)')
    
    parser.add_argument('--fixed-stake', required=False, type=int,
                        default=10,
                        help='Fixed stake size when using FixedSize sizer')
    
    parser.add_argument('--extreme-threshold', required=False, type=float,
                        default=0.6,
                        help='Threshold for extreme sentiment (large position)')
    
    parser.add_argument('--medium-threshold', required=False, type=float,
                        default=0.3,
                        help='Threshold for medium sentiment (small position)')
    
    parser.add_argument('--large-stake', required=False, type=int,
                        default=100,
                        help='Large stake size for extreme sentiment')
    
    parser.add_argument('--small-stake', required=False, type=int,
                        default=10,
                        help='Small stake size for medium sentiment')
    
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
