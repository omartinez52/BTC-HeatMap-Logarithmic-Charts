"""
    BTC_Longterm_Data:
        - Gathers BTC historical price data from BCHAIN API aquired through Quandl.com .
        - BTC historical price data will be used to plot the BTC 200WMA Heat Map.
        (200WMA Heat Map Solution: 200WMA = 4-Weekly % Difference in the 1400 Daily moving average)
            - The 200WMA Heat Map uses BTC daily closing price from 2009-Now.
            - First, the daily BTC price is plotted on a line plot.
            - Markers are placed from data equated from the 200WMA Heat Map solution.
    Reference: https://www.lookintobitcoin.com/charts/200-week-moving-average-heatmap/
        - Charts are plotted based on the equation provided on the url link above.
        (COPIED FROM URL WEBSITE PROVIDED)
        {-Indicator Overview
            - In each of its major market cycles, Bitcoin's price historically bottoms out around the 200 week moving average.
            - This indicator uses a colour heatmap based on the % increases of that 200 week moving average.
            - Depending on the month-by-month % increase of the 200 week moving average, a colour is assigned to the price chart.
        - How It Can Be Used
            - The long term Bitcoin investor can monitor the monthly colour changes.
            - Historically, when we see orange and red dots assigned to the price chart.
            - This has been a good time to sell Bitcoin as the market overheats.
            - Periods where the price dots are purple and close to the 200 week MA have historically been good times to buy.
            - Note: this is a slightly modified version of a concept created by @100trillionUSD.
            - Use the link below to learn more about the original."}
"""
import numpy as np
import pandas as pd
import requests
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
class Bitcoin:
    def __init__(self):
        """Instantiating empty instance variables."""
        # BTC daily price for golden ration chart.
        self.GR_daily_df = ''
        # monthly data frame used for creating heat map.
        self.HM_monthly_df = ''
        # complete BTC historical daily price data frame.
        self.complete_df = ''
        # daily btc chart used for the heat map.
        self.HM_daily_df = ''
        # distance used for color sequence of heatmap.
        self.HM_distance = ''
        # complete list of dates from complete BTC data frame
        self.complete_dates = ''
        # list of dates in the HM_monthly data frame
        self.HM_monthly_dates=''
        # list of dates in the GR_daily_df data frame
        self.GR_dates=''
        # heatmap dates
        self.HM_dates = ''
        self.API_url = 'https://www.quandl.com/api/v3/datasets/BCHAIN/MKPRU.json?api_key=vGBx1_TY6raUMRzDz4Df'
        self.CG_df=''
        self.updateDataFrames()
    """
        updateDataFrames():
            - Will make a request to quandl url to access BCHAIN API for BTC historical prices.
            - Uses data to fill all data frames with data in accordance to their use case.
            - Refer to Heat Map Solution and Logarithmic Solution.
    """
    def updateDataFrames(self):
        # Requesting data from API url. Using json to create a dictionary. Creating data frame from dict.
        self.complete_df = pd.DataFrame(json.loads(requests.get(self.API_url).text))
        # 3rd index of dataset column contains a nested list with data [[Date1,Val1],[Date2,Val2],...].
        self.complete_df = pd.DataFrame(self.complete_df.dataset[3],columns=['Date','Value'])
        # reverse order of complete data from to ascending datetime order.
        self.complete_df = self.complete_df.iloc[::-1]
        # creating 200WMA column to store data for heat map. Taking 1400 day moving average of data.
        self.complete_df['200WMA'] = self.complete_df['Value'].astype('float').rolling(window=1400).mean()

        # creating copies of daily data frame.
        self.HM_daily_df = self.complete_df.copy()
        self.GR_daily_df = self.complete_df.copy()
        # removing rows if price is 0.
        self.GR_daily_df = self.GR_daily_df[self.GR_daily_df['Value'] > 0]
        # creating 350 Daily Moving Average column.
        self.GR_daily_df['350DMA'] = self.GR_daily_df['Value'].astype('float').rolling(window=350).mean()
        #removing first 350 rows of data to line up with 350DMA line.
        self.GR_daily_df = self.GR_daily_df[350:]
        # creating a series of datetime objects for plotting 350DMA line.
        self.GR_dates = pd.to_datetime(self.GR_daily_df['Date'])

        # removing first 1400 rows of data to line up with 200WMA line.
        self.HM_daily_df = self.HM_daily_df[1400:]
        # Collects one day of data every 4th week (or 28 days).
        self.HM_monthly_df = self.HM_daily_df[::28]
        # creating a series of datetime objects for plotting monthly heat map markers.
        self.HM_monthly_dates = pd.to_datetime(self.HM_monthly_df['Date'])
        # creating a series of datetime objects for plotting heatmap chart.
        self.HM_dates = pd.to_datetime(self.HM_daily_df['Date'])
        # creating a series of datetime objects for plotting Logarithmic chart.
        self.complete_dates = pd.to_datetime(self.complete_df['Date'])
        # monthly percent change of the 200WMA used for color sequence of heat map.
        self.HM_distance = self.HM_monthly_df['200WMA'].pct_change() * 100

        # creating golden ration mutipliers
        self.GR_daily_df['1.6GRM'] = self.GR_daily_df['350DMA'].astype('float') * 1.6
        self.GR_daily_df['2GRM'] = self.GR_daily_df['350DMA'].astype('float') * 2.0
        self.GR_daily_df['3GRM'] = self.GR_daily_df['350DMA'].astype('float') * 3.0
        self.GR_daily_df['5GRM'] = self.GR_daily_df['350DMA'].astype('float') * 5.0
        self.GR_daily_df['8GRM'] = self.GR_daily_df['350DMA'].astype('float') * 8.0
        self.GR_daily_df['13GRM'] = self.GR_daily_df['350DMA'].astype('float') * 13.0
        self.GR_daily_df['21GRM'] = self.GR_daily_df['350DMA'].astype('float') * 21.0

        #creating coin gecko data frame
        self.CG_df = cg.get_coins_markets(vs_currency='usd')
        self.CG_df = pd.DataFrame(
            self.CG_df,
            columns=[
                'symbol',   # crypto symbol
                'current_price', # crypto current price
                'price_change_percentage_24h',  # crypto 24hr price change
            ]
        )
        # only taking info on top 10 crypto currencies
        self.CG_df = self.CG_df.iloc[0:10]
        # setting symbol names to upper case
        self.CG_df['symbol'] = self.CG_df['symbol'].str.upper()
# bitcoin object which will hold all data frames.
btc_obj = Bitcoin()
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,assets_external_path=mathjax)

app.layout = html.Div(
    children=[
        html.Div(
            id='header-img-div',
            children=[
                html.Div(
                    id='header-price',
                    children=[],
                    style={'border': '1px solid black',
                           'border-radius':'5px',
                           'width': '100wh',
                           'height':'5vh',
                           'overflow':'hidden',
                           'top':'-1%',
                           'left':'50%',
                           'background-color': '#ADADC9',
                           }
                ),
                # btc logo png
                html.Img(src='https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1024px-Bitcoin.svg.png',
                         style={'width':'4%',
                                'position':'absolute',
                                'top': '7%',
                                'left':'1%',
                                }
                         ),
                # Title image
                html.Img(src='https://fontmeme.com/permalink/210806/6cc02fc14ff0457056bbde9a6904e7de.png',
                         style={'width':'3%',
                                'position':'absolute',
                                'top': '7.5%',
                                'left':'5.5%',
                                }
                         ),
            ],style={'width':'auto',
                     'height':'15vh',
                     }
        ),
        html.Div(
            id='label-img',
            children=[
                html.Img(src='https://fontmeme.com/permalink/210807/4702eb95fe3a8737a0f29597dfecf6b9.png',
                         style={'width':'20%',
                                'position':'absolute',
                                'top': '19%',
                                'left':'5%',
                                }
                         ),
                html.Img(src='https://fontmeme.com/permalink/210806/908ef73077a3ef9c6a921cb08ee512bf.png',
                         style={'width': '20%',
                                'position': 'absolute',
                                'top': '82.5%',
                                'left': '5%',
                                }
                         ),
            ]
        ),
        html.Div(
            id='main-div',
            children=[
                dcc.Input(id='input-bar',
                          value='btc',
                          style={'visibility':'hidden',}
                          ),
                html.Div(
                    id='graphs-div',
                    children=[
                        dcc.Loading(
                            id='loading_hm',
                            type='default',
                            fullscreen=True,
                            children=[
                                html.Div(
                                    children=[
                                        html.Img(
                                            src='https://www.lookintobitcoin.com/static/img/formulas/02.png',
                                            style={'position':'absolute',
                                                   'width':'30%',
                                                   'top': '-8%',
                                                   'left': '37%',
                                                   },
                                            id='200WMA-Heat-Map-Equation-img'
                                        ),
                                        dcc.Graph(
                                            id='heatmap-chart',
                                            style={
                                                   "width": '100%',
                                                   'height': '50vh',
                                                   }
                                        ),
                                    ],style={'position':'absolute',
                                                 'width':'160vh',
                                                 'height':'55vh',
                                                 'top': '50%',
                                                 'left': '50%',
                                                 'border': '1px solid black',
                                                 'border-radius':'10px',
                                                 "transform": "translate(-50%, -50%)",
                                                 }
                                ),
                                html.Div(
                                    children=[
                                        html.Img(
                                            src='https://www.lookintobitcoin.com/static/img/formulas/04.png',
                                            style={'position':'absolute',
                                                   'width':'32%',
                                                   'top': '-10%',
                                                   'left': '35%',
                                                   },
                                            id='Golden-Ratio-Equation-img'
                                        ),
                                        dcc.Graph(
                                            id='golden-chart',
                                            style={
                                                   "width": '100%',
                                                   'height': '50vh',
                                                   }
                                        ),
                                    ],style={'position':'absolute',
                                                 'width':'160vh',
                                                 'height':'55vh',
                                                 'top': '142%',
                                                 'left': '50%',
                                                 'border': '1px solid black',
                                                 'border-radius':'10px',
                                                 "transform": "translate(-50%, -50%)",
                                                 }
                                ),
                            ]
                        ),
                    ],style={'position':'absolute',
                             'width':'169vh',
                             'height':'70vh',
                             'top':'0%'
                             }
                ),
            ],style={'position':'absolute',
                     'margin-left': 'auto',
                     'margin-right': 'auto',
                     'top':'84%',
                     'left':'50%',
                     'width':'169vh',
                     'height':'135vh',
                     'border': '4px solid black',
                     'border-radius':'10px',
                     "transform": "translate(-50%, -50%)",
                     }
        ),
    ],
)
@app.callback(
    Output(component_id='heatmap-chart',component_property='figure'),
    Output(component_id='golden-chart',component_property='figure'),
    Output(component_id='header-price',component_property='children'),
    Input(component_id='input-bar',component_property='value'),
)
def returnCharts(value):
    # Heat map figure which will hold all plots significant to the 200WMA Heat Map.
    HMfig = go.Figure()
    # Golden ration figure which will hold all plots significant to the Golden ration multiplier.
    GRfig = go.Figure()
    # Heat Map BTC 200WMA line.
    HMfig.add_trace(
        go.Scatter(
            x=btc_obj.HM_dates,
            y=btc_obj.HM_daily_df['200WMA'],
            mode='lines',
            legendrank=2,
            line={'color':'rgb(227, 9, 9)'},
            name='200WMA',
        )
    )
    # Heat Map BTC Daily price chart.
    HMfig.add_trace(
        go.Scatter(
            x=btc_obj.HM_dates,
            y=btc_obj.HM_daily_df['Value'],
            mode='lines',
            legendrank=1,
            line={'color':'rgb(0, 89, 255)'},
            showlegend=False,
        )
    )
    # heat map markers
    HMfig.add_trace(go.Scatter(x=btc_obj.HM_monthly_dates,
                               y=btc_obj.HM_monthly_df['Value'],
                               marker={'color':btc_obj.HM_distance,
                                       'colorscale':'rainbow',
                                       'cmin':0,
                                       'cmax':20,
                                       'size':8,
                                       },
                               mode='markers',
                               showlegend=False,
                               )
                    )
    HMfig.update_yaxes(type='log')

    # 350 day moving average
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['350DMA'],
            mode='lines',
            legendrank=2,
            line={'color': 'rgb(255, 204, 0)'},
            name='350DMA',
        ),
    )
    # Golden Ratio Multiplier(GRM): 1.6
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['1.6GRM'],
            mode='lines',
            legendrank=3,
            line={'color': 'rgb(0, 201, 54)'},
            name='1.6 GRM',
            opacity=0.4,
        )
    )
    # Golden Ratio Multiplier(GRM): 2.0
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['2GRM'],
            mode='lines',
            legendrank=3,
            line={'color': 'rgb(245, 0, 82)'},
            name='2 GRM',
            opacity=0.4,
        )
    )
    # Golden Ratio Multiplier(GRM): 3.0
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['3GRM'],
            mode='lines',
            legendrank=4,
            line={'color': 'rgb(219, 15, 206)'},
            name='3 GRM',
            opacity=0.4,
        )
    )
    # Golden Ratio Multiplier(GRM): 5.0
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['5GRM'],
            mode='lines',
            legendrank=4,
            line={'color': 'rgb(73, 0, 122)'},
            name='5 GRM',
            opacity=0.4,
        )
    )
    # Golden Ratio Multiplier(GRM): 8.0
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['8GRM'],
            mode='lines',
            legendrank=4,
            opacity=0.4,
            line={'color': 'rgb(11, 1, 97)',
                  'dash':'dash'
                  },
            name='8 GRM',
        )
    )
    # Golden Ratio Multiplier(GRM): 13.0
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['13GRM'],
            mode='lines',
            legendrank=4,
            opacity=0.4,
            line={'color': 'rgb(11, 1, 97)',
                  'dash': 'dash'
                  },
            name='13 GRM',
        )
    )
    # Golden Ratio Multiplier(GRM): 21.0
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['21GRM'],
            mode='lines',
            legendrank=4,
            opacity=0.4,
            line={'color': 'rgb(11, 1, 97)',
                  'dash': 'dash'
                  },
            name='21 GRM',
        )
    )
    # BTC Daily price chart.
    GRfig.add_trace(
        go.Scatter(
            x=btc_obj.GR_dates,
            y=btc_obj.GR_daily_df['Value'],
            mode='lines',
            legendrank=1,
            line={'color': 'rgb(0, 89, 255)'},
            name='BTC Price',
        )
    )
    GRfig.update_yaxes(type='log',
                       title='Price'
                       )
    GRfig.update_xaxes(title='Date')

    # empty list to be filled and returned
    myList = list()
    # creating table for crypto prices
    for index, row in btc_obj.CG_df.iterrows():
        # assigning red color if price change is less than 0, else green
        color = 'rgb(255,17,0)' if row['price_change_percentage_24h'] < 0 else 'rgb(3, 163, 30)'
        t = html.Div(
            children=[
                html.Th(
                    html.H6(row['symbol'],
                            style={'display': 'inline-block',
                                   'font-size': '14px',
                                   'margin-left':'25px',
                                   }
                            )
                ),
                html.Th(
                    html.H6("${:,.2f}".format(row['current_price']),
                            style={'display': 'inline-block',
                                   'font-size': '14px',
                                   'color':color,
                                   }
                            )
                ),
                html.Th(
                    html.H6("%{:,.1f}".format(row['price_change_percentage_24h']),
                            style={'display': 'inline-block',
                                   'font-size': '14px',
                                   'color': color,
                                   }
                            )
                )
            ],style={'display':'inline-block',
                     }
        )
        myList.append(t)
    return HMfig, GRfig, myList
if __name__ == '__main__':
    app.run_server(debug=True)