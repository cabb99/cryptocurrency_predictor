import os

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv

# from scipy.stats import norm
from scipy.stats import t
from scipy.stats import linregress
import numpy as np
import pandas as pd
import datetime
import dash_table
import dash_table.FormatTemplate

try:
    import exceptions
except ImportError:
    from . import exceptions

pages = []

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(DOTENV_PATH)

if "DYNO" in os.environ:
    # the app is on Heroku
    debug = False
# google analytics with the tracking ID for this app
# external_js.append('https://codepen.io/jackdbd/pen/rYmdLN.js')
else:
    debug = True
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)

try:
    # py.sign_in(os.environ["PLOTLY_USERNAME"], os.environ["PLOTLY_API_KEY"])
    pass
except KeyError:
    raise exceptions.ImproperlyConfigured("Plotly credentials not set in .env")

app_name = "Cryptocurrency Price Predictor"
server = Flask(app_name)

try:
    # server.secret_key = os.environ["SECRET_KEY"]
    pass
except KeyError:
    raise exceptions.ImproperlyConfigured("SECRET KEY not set in .env:")

external_js = [
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML",  # Latex
    "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js",  # Animations
]

external_css = [

    "https://codepen.io/chriddyp/pen/bWLwgP.css",  # Dash stylesheet
    "https://fonts.googleapis.com/css?family=Lobster|Raleway",  # Fonts
    # "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.3/css/fontawesome.min.css",  # Fonts
    {
        'href': 'https://use.fontawesome.com/releases/v5.15.3/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-SZXxX4whJ79/gErwcOYf+zWLeJdY/qpuqC4cAa9rOGUstPomtqpuNWT9wdPEn2fk',
        'crossorigin': 'anonymous'
    },
]

external_stylesheets = [

]

theme = {"font-family": "Arial", }

app = Dash(name=app_name, server=server,
           external_stylesheets=external_css,
           external_scripts=external_js,
           meta_tags=[{"name": "viewport", "content": "width=device-width"}])


def create_null(n):
    """ Creates empty data containers.
    Empty data containers can be used for headless callbacks.
    They can also be used to store information on the client side"""
    return html.Div(children=[dcc.Store(id=f'null{i}', data=[]) for i in range(n)])


def create_toggle():
    """Creates the menu toggle button to open and close the menu"""
    button = html.A(className="toggle", id="toggleB",
                    children=[html.I(),
                              html.I(),
                              html.I()])
    return button


def create_sidebar():
    """Creates the navigation sidebar. It can open and close."""
    sidebar = html.Div(
        [
            html.H2("Navigation", className="menu-tittle", id='menuTittle'),
            dbc.Nav(
                [
                    dbc.NavLink([html.I(className="fas fa-home"), " Home"],
                                href="/home", id="page-home-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-chart-line"), " Forecast"],
                                href="/forecast", id="page-1-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-chart-bar"), " Historical"],
                                href="/historical", id="page-2-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-microscope"), " Indicators"],
                                href="/indicators", id="page-3-link", className="page-link"),
                    # dbc.NavLink([html.I(className="fas fa-coins"), " Coins"],
                    #            href="/coins", id="page-4-link", className="page-link"),
                    # dbc.NavLink([html.I(className="fas fa-chart-pie"), " Market Cap"],
                    #            href="/marketcap", id="page-5-link", className="page-link"),
                    # dbc.NavLink([html.I(className="fas fa-heart"), " Sentiment"],
                    #            href="/sentiment", id="page-6-link", className="page-link"),
                    # dbc.NavLink([html.I(className="fas fa-virus"), " COVID"],
                    #            href="/covid", id="page-7-link", className="page-link"),
                    # dbc.NavLink([html.I(className="fas fa-code"), " Code"],
                    #            href="/code", id="page-8-link", className="page-link"),
                    dbc.NavLink([html.I(className="fab fa-github"), " Github"],
                                href="https://github.com/cabb99/cryptocurrency_predictor",
                                target='_blank', id="page-9-link", className="page-link"),
                    # dbc.NavLink([html.I(className="fas fa-users"), " Group"],
                    #            href="/group", id="page-10-link", className="page-link"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        id="sideNav",
        className="side-navigation"
    )
    return sidebar


def create_header():
    """Creates the header of the webpage.
    It remains constant across different pages."""
    header = html.Header(
        children=[html.H1(children=html.A(app_name, href="/home"), id='headTittle')],
        id="head", className="header")
    return header


def create_footer():
    """Creates the footer of the webpage.
    It remains constant across different pages."""
    p0 = html.P(
        children=[
            html.Span("Built with "),
            html.A(
                "Plotly Dash", href="https://github.com/plotly/dash", target="_blank"
            ),
        ]
    )
    p1 = html.P(
        children=[
            html.Span("Data from "),
            html.A("some website", href="https://some-website.com/", target="_blank"),
        ]
    )
    a_fa = html.A(
        children=[
            html.I([], className="fa fa-font-awesome fa-2x"), html.Span("Font Awesome")
        ],
        style={"textDecoration": "none"},
        href="http://fontawesome.io/",
        target="_blank",
    )

    div = html.Div([p0],
                   id="foot",
                   className="footer", )
    footer = html.Footer(children=div)
    return footer


def home():
    content = html.Div([
        html.Div(className="parallax-demo"),
        html.H2('Overview'),
        html.P("""Cryptocurrency is a burgeoning asset class with investors flocking to invest in all types of cryptos. 
Bitcoin by itself has been the best performing asset in the past 10 years with an annualized return of 230%.
1 bitcoin was valued at $1 in 2011 and now (as of May 2021) hovers in the $50,000 range, a whopping 5,000,000% increase."""),
        html.Br(),
        html.P("""As more and more people look to diversify their portfolio and have exposure to this new asset class,
having a tool to give investors and speculators alike an idea of how crypto prices will move will be a tremendous 
advantage."""),
        html.Br(),
        html.P("""Because cryptocurrency is still relatively new, it is difficult to determine what drives price 
movement and volatility. Technical analysis alone would not be sufficient to predict price movement and it may not even 
be the strongest determinant of price due to the lack of empirical evidence and history. In the example of Dogecoin, 
price movement has been driven by tweets from Elon Musk and momentum investing with very little to-no fundamental 
support. We want to provide a tool for people to think about various different factors to make the best informed
investment decisions when it comes to cryptocurrencies.
"""),
        html.Br(),
        html.Div(className="parallax-demo2"),
        html.H2('Research & Methodology'),
        html.P("""Our team attempted create a tool to predict and forecast cryptocurrency prices based on various factors such
as tweets, reddit threads, financial indicators, index benchmarks, bond prices, etc. using zero order, linear regression,
logistic regression, LSTM and ARIMA models, etc to determine correlation. Other methods included fitting a T-distribution
to determine profitablity and volatility."""),
        html.Br(),
        html.H2('Conclusion'),
        html.P("""The various factors chosen did not quantifiably indicate a correlation or predict an accurate price
change to the 5 cryptocurrencies analyzed."""),
    ])
    return content


def forecast():
    df = pd.read_csv('s3://ds4a-team151/Modelled_coins.csv', index_col=0)
    df2 = pd.read_csv('s3://ds4a-team151/Modelled_coins_prices.csv', index_col='date')
    df2.columns = df2.columns.astype(int)
    df['label'] = [f'{c["name"]} ({c["symbol"]})' for ii, c in df.iterrows()]
    df['value'] = df.index
    crypto_options = list(df[['label', 'value']].T.to_dict().values())
    money = dash_table.FormatTemplate.money(2)
    percentage = dash_table.FormatTemplate.percentage(2)
    content = html.Div([
        html.H2('Price forecast'),
        html.P("We calculate the estimated price in the future by fitting the past price changes using a Student's T "
               "distribution, allowing us to predict the distribution of the price change in the future. "
               "Use the slider to select the prediction for two quantiles of the distribution. The table "
               "will be sorted by calculating the geometric mean of the two quantiles. Use the buttons to select the "
               "number of price changes taken into account to make the distribution. "
               "Feel free to sort and filter by name, marketcap or price change."
               ),
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th([
                        'Confidence interval'
                    ], style={'width': '70%'}),
                    html.Th([
                        'Time back'
                    ], style={'width': '30%'}),
                ]),
            ]),
            html.Tbody([
                html.Tr([
                    html.Th([
                        dcc.RangeSlider(id='forecast-risk',
                                        className='forecast-slider',
                                        value=[0.4, 0.75],
                                        min=0.01, max=0.99, step=0.01,
                                        pushable=0.05,
                                        marks={
                                            0.01: {'label': '1%', 'style': {'color': '#000000'}},
                                            0.25: {'label': '25%', 'style': {'color': '#444444'}},
                                            0.50: {'label': '50%', 'style': {'color': '#000044'}},
                                            0.75: {'label': '75%', 'style': {'color': '#444444'}},
                                            0.99: {'label': '99%', 'style': {'color': '#000000'}},
                                        }
                                        ),
                    ]),
                    html.Th([
                        *[html.Button(i, id=f'button-{i}', n_clicks=0, className='forecast-button') for i in
                          ['1Y', '3M', '1M']]
                    ]),
                ]),
            ])
        ], style={'width': '90%'}),
        html.Div(id='forecast-table-parameters', children=[

        ]),
        dash_table.DataTable(id='forecast-table',
                             columns=[
                                 # dict(id='id', name='id'),
                                 dict(id='name', name='Name', type='numeric',
                                      selectable=False),
                                 dict(id='symbol', name='Symbol', type='numeric', ),
                                 dict(id='market_cap', name='Market cap (millions USD)', type='numeric',
                                      format=money, ),
                                 dict(id='price', name='Price (USD)', type='numeric', format=money, ),
                                 dict(id='max_change', name='Predicted change max', type='numeric',
                                      format=percentage, ),
                                 dict(id='min_change', name='Predicted change min', type='numeric',
                                      format=percentage, ),
                                 dict(id='estimated', name='Estimated change', type='numeric', format=percentage, ),
                             ],
                             sort_action="native",
                             sort_mode="single",
                             filter_action='native',
                             row_selectable='single',
                             data=[],  # small_table.to_dict('records'),
                             fixed_rows={'headers': True},
                             style_table={'height': 400},
                             style_data_conditional=[
                                 {
                                     'if': {
                                         'filter_query': '{estimated} > 0',
                                         'column_id': 'estimated'
                                     },
                                     'color': 'green'
                                 },
                                 {
                                     'if': {
                                         'filter_query': '{estimated} < 0',
                                         'column_id': 'estimated'
                                     },
                                     'color': 'red'
                                 },
                                 {
                                     'if': {
                                         'filter_query': '{max_change} > 0',
                                         'column_id': 'max_change'
                                     },
                                     'color': 'green'
                                 },
                                 {
                                     'if': {
                                         'filter_query': '{max_change} < 0',
                                         'column_id': 'max_change'
                                     },
                                     'color': 'red'
                                 },
                                 {
                                     'if': {
                                         'filter_query': '{min_change} > 0',
                                         'column_id': 'min_change'
                                     },
                                     'color': 'green'
                                 },
                                 {
                                     'if': {
                                         'filter_query': '{min_change} < 0',
                                         'column_id': 'min_change'
                                     },
                                     'color': 'red'
                                 }, ]
                             ),

        html.Div(id='forecast-coin-selections', style=dict(display='inline-block', width='100%'), children=[
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th([
                            'Cryptocurrency'
                        ]),
                        html.Th([
                            'Y axis'
                        ]),
                    ]),
                ]),
                html.Tbody([
                    html.Tr([
                        html.Th([
                            dcc.Dropdown(id='forecast-coin', className='forecast-selection',
                                         options=crypto_options, clearable=False,
                                         value=1, placeholder='Cryptocurrencies sorted by future gains'),
                        ]),
                        html.Th([
                            dcc.RadioItems(id='forecast-yaxis-type', className='forecast-radio', options=[
                                {'label': 'Linear', 'value': 'linear'},
                                {'label': 'Logarithmic', 'value': 'log'}],
                                           value='linear', labelStyle={'display': 'inline-block'})]),
                    ])
                ]),
            ], style={'width': '90%'}),
            dcc.Loading([
                html.H2([html.Img(id='forecast-coin-logo', className='forecast-coin-logo'),
                         html.P('Loading, please wait a few seconds', id='forecast-coin-name',
                                className='forecast-coin-name')]),
                dcc.Graph(id='forecast-graph', ),
                html.P('The plot will appear here', id='forecast-coin-description'),
            ]),
            dcc.Store(id='forecast-data', data=df.T.to_json(date_format='iso', orient='split')),
            dcc.Store(id='forecast-data-prices', data=df2.to_json(date_format='iso', orient='split')),
        ]),
        html.Div(
            [html.H3('Distribution of change in price'),
             html.P('''To forecast the price in the future we fitted the natural logarithm of the ratio of the change in
              price "log(ROCR)" to a Student's T distribution. The following plots shows the distribution of price over the
              period used for the forecast and how the quantiles observed compare to the quantiles predicted by the 
              Student's T distrubution'''),
             dcc.Loading(
                 dcc.Graph(id='forecast-kde', className='forecast-kde')),
             dcc.Loading(
                 dcc.Graph(id='forecast-QQ', className='forecast-QQ'))
             ]
        )
    ])
    return content


# def historical():
#     content = html.Div([
#         html.H2('Historical prices'),
#         html.Hr(),
#         html.Div([
#             dcc.DatePickerRange(),
#             dcc.Dropdown(id='historical-coin', options=[
#                 {'label': 'Bitcoin', 'value': 'BTC'},
#                 {'label': 'Ethereum', 'value': 'ETH'},
#                 {'label': 'Dogecoin', 'value': 'DOGE'}
#             ], value='BTC', placeholder='Select coin to compare history'),
#             html.Div('Historical Crypto Price Line Chart for Specific Dates', className='placeholder'),
#             html.Div('Historical Events aligned with above chart timeline (Hover to know event)',
#                      className='placeholder'),
#         ])
#     ])
#     return content

def historical():
    content = html.Div([
        html.H2('Historical prices'),
        html.P("""The price history of coins reveals a lot about the challenges in accurately predicing price trends. 
        Crypto as an investment class first hit the mainstream in 2018 and there was a general uptick in the price 
        of most coins; however, the magnitude of changes in price were unpredictable. Coins like Ripple (XRP) experienced a 
        meteoric rise in price and an equally precipitous fall in value with a few months, while other cryptos like Bitcoin (BTC) 
        exhibited a bit more resilience. Similarly, in the most recent bull market there's a general uptrend, but only certain coins
        likey BTC and ETH surpass all time highs while others like XRP don't come close. Dogecoin was a significant outlier with an 
        absurd increase in price in the past year. The level of volatility and spculation in the crypto markets makes it possible to 
        identify a price trend, particularly over longer time periods, but it is nearly impossible to quantify the magnitude of the 
        trend in shorter time periods."""
               ),
        html.Hr(),
        html.Div([
            html.Button(id='activate_tableau_viz1628020240288', className='hidden-button'),
            html.Div(
                children=[
                    html.Div(
                        className="tableauPlaceholder",
                        id="viz1628020240288",
                        style={"position": "relative"},
                        children=[
                            html.Noscript(
                                children=[
                                    html.A(
                                        href="#",
                                        children=[
                                            html.Img(
                                                alt=" ",
                                                src="https://public.tableau.com/static/images/Cr/CryptoAnalysis_16280131226670/Prices/1_rss.png",
                                                style={"border": "none"},
                                                children=[],
                                            )
                                        ],
                                    )
                                ]
                            ),
                            html.ObjectEl(
                                className="tableauViz",
                                style={"display": "none"},
                                children=[
                                    html.Param(
                                        name="host_url",
                                        value="https%3A%2F%2Fpublic.tableau.com%2F",
                                        children=[],
                                    ),
                                    html.Param(name="embed_code_version", value="3", children=[]),
                                    html.Param(name="site_root", value="", children=[]),
                                    html.Param(
                                        name="name",
                                        value="CryptoAnalysis_16280131226670/Prices",
                                        children=[],
                                    ),
                                    html.Param(name="tabs", value="yes", children=[]),
                                    html.Param(name="toolbar", value="yes", children=[]),
                                    html.Param(
                                        name="static_image",
                                        value="https://public.tableau.com/static/images/Cr/CryptoAnalysis_16280131226670/Prices/1.png",
                                        children=[],
                                    ),
                                    html.Param(name="animate_transition", value="yes", children=[]),
                                    html.Param(
                                        name="display_static_image", value="yes", children=[]
                                    ),
                                    html.Param(name="display_spinner", value="yes", children=[]),
                                    html.Param(name="display_overlay", value="yes", children=[]),
                                    html.Param(name="display_count", value="yes", children=[]),
                                    html.Param(name="language", value="en-US", children=[]),
                                ],
                            ),
                        ],
                    ),
                    html.Script(
                        type="text/javascript",
                        children=[
                            "var divElement = document.getElementById('viz1628020240288');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);"
                        ],
                    ),
                ]
            )
        ])
    ])
    return content


def indicators():
    indicator_options = [{'label': 'Bitcoin (BTC)', 'value': 'BTC'},
                         {'label': 'Ethereum (ETH)', 'value': 'ETH'},
                         {'label': 'Dogecoin (DOGE)', 'value': 'DOGE'},
                         {'label': 'Litecoin (LTC)', 'value': 'LTC'},
                         {'label': 'Ripple (XRP)', 'value': 'XRP'}]
    groups = [
        'Future ROCR',
        'Future NATR',
        'Future ROCR distribution',
        'Difference between future and past ROCR distribution',
        'Present ROCR distribution',
        'Past ROCR distribution',
        'Historical ROCR',
        'Historical NATR',
        'OHLC',
        'Price Transform indicators',
        'Momentum Indicators',
        'Overlap Studies',
        'Volatility Indicators',
        'Volume Indicators',
        'Statistic Indicators',
        'Cycle Indicators',
        'Pattern Recognition',
        'Pattern Recognition States',
        'Market Indicators',
        'Twitter tweet volume',
        'Google trends',
        'Federal Reserve bonds',
        'Covid infections',
    ]
    indicator_groups = [{'label': g, 'value': g} for g in groups]
    content = html.Div([
        html.H2('Indicators'),
        html.Hr(),
        html.Table(id='indicator_selections', children=[
            html.Thead(children=[
                html.Tr([
                    html.Th([
                        'Cryptocurrency'
                    ], style={'width': '40%'}),
                    html.Th(colSpan=2, children=[
                        'Indicator Groups'
                    ], style={'width': '60%'}),
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Th([
                        dcc.Dropdown(id='indicator-coin', className='indicator-dropdown', options=indicator_options,
                                     value='BTC', clearable=False), dcc.Loading(html.P(id='indicator-loading-data'))

                    ]),
                    html.Th([
                        dcc.Dropdown(id='indicator-group1', className='indicator-dropdown', options=indicator_groups,
                                     value='Future ROCR distribution', clearable=False),
                    ]),
                    html.Th([
                        dcc.Dropdown(id='indicator-group2', className='indicator-dropdown', options=indicator_groups,
                                     value='Past ROCR distribution', clearable=False),
                    ]),
                ]),

            ])
        ], style={'width': '90%'}),
        html.P(id='indicator-description'),
        dcc.Loading(dcc.Graph(id='indicator-correlation')),
        html.H3('Relationship between indicators'),
        html.H4(id='indicator-comparison-tittle', children='Click a heatmap cell above to update plots'),
        dcc.Loading(dcc.Graph(id='indicator-regplot'), ),
        dcc.Loading(dcc.Graph(id='indicator-timeplot'), ),
        dcc.Store(id='indicator-data', )
    ])
    return content


def coins():
    content = html.Div([
        html.H2('Similarity of cryptocurrencies'),
        html.Hr(),
        html.Div([
            html.Div('Correlation Matrix for cryptos vs other cryptos', className='placeholder')
        ])
    ])
    return content


def marketcap():
    content = html.Div([
        html.H2('Market Cap history'),
        html.Hr(),
        html.Div([
            html.Div('Plot showing the percentage of the marketcap by coin', className='placeholder'),
            dcc.Dropdown(id='marketcap-coin', options=[
                {'label': 'Bitcoin', 'value': 'BTC'},
                {'label': 'Ethereum', 'value': 'ETH'},
                {'label': 'Dogecoin', 'value': 'DOGE'}
            ], value='BTC', placeholder='Select coin to compare marketcaps'),
            html.Div('Plot showing the beta risk of each coin by coin', className='placeholder'),
        ])
    ])
    return content


def sentiment():
    content = html.Div([
        html.H2('Sentiment analysis'),
        html.Hr(),
        html.Div([
            dcc.Dropdown(id='sentiment-coin', options=[
                {'label': 'Bitcoin', 'value': 'BTC'},
                {'label': 'Ethereum', 'value': 'ETH'},
                {'label': 'Dogecoin', 'value': 'DOGE'}
            ], value='BTC', placeholder='Select coin to compare sentiment'),
            html.Div('Google, Twitter, reddit trends', className='placeholder'),
            html.Div('Tabular view of Twitter user ranking compared to each coin', className='placeholder'),
            html.Div('Twitter live stream', className='placeholder'),
            html.Div('Twitter word cloud for positive and negative sentiments', className='placeholder'),

        ])
    ])
    return content


def covid():
    content = html.Div([
        html.H2('Did COVID-19 influence the price of cryptocurrencies?'),
        html.Hr(),
        html.P("""One of the most historic events has been the COVID-19 pandemic. 
        It disrupted the life of people around the world, forcing them to rethink their jobs, rethink working from home, 
        practice social distancing, and to change their life priorities. During the same period, cryptocurrencies 
        such as Bitcoin continued to increase in price. We observed that this correlation is stronger when we focus on particular 
        countries such as the UK, US or Russia."""),
        html.Div([
            dcc.Dropdown(id='covid-coin', options=[
                {'label': 'Top500', 'value': 'top500'},
                {'label': 'Bitcoin', 'value': 'BTC'},
                {'label': 'Ethereum', 'value': 'ETH'},
                {'label': 'Dogecoin', 'value': 'DOGE'}
            ], value='BTC', placeholder='Select coin to compare to covid'),
            dcc.RadioItems(id='covid-cumulative', options=[
                {'label': 'Total cases', 'value': 'True'},
                {'label': 'New cases', 'value': 'False'},
            ]),
            html.Div('Line Plot of selected Country Cases relative to selected crypto price ', className='placeholder'),
            html.Div('Reg Plot of selected Country Cases relative to selected crypto price', className='placeholder'),
            html.Button('All the world', id='World'),
            html.Div('GeoMap of correlation between COVID Rates vs Coin Prices', className='placeholder'),
            html.Div('US GeoMap of correlation between COVID Rates vs Coin Prices', className='placeholder'),
        ]),

    ])
    return content


def github():
    content = html.Div("Link to Github page for this code")
    return content


def group():
    content = html.Div([
        html.H2('DS4A Empowerment Cohort 2: Team 151'),
        html.Hr(),
        html.Div([

        ])
    ])
    return content


def create_scratch_content():
    """ Creates scratch page content.
    Treat this like a sandbox"""
    content = html.Div(
        children=[
            # range slider with start date and end date
            html.Div(
                children=[
                    dcc.RangeSlider(
                        id="year-slider",
                        min=1990,
                        max=2018,
                        value=[2010, 2015],
                        marks={(i): f"{i}" for i in range(1990, 2018, 2)},
                    )
                ],
                style={"marginBottom": 20},
            ),
            html.Hr(),
            html.Img(src='https://s2.coinmarketcap.com/static/img/coins/64x64/1.png'),
            dcc.Dropdown(id='forecast-coin', options=[
                {'label': html.Img(src='https://s2.coinmarketcap.com/static/img/coins/64x64/1.png'),
                 'value': 1}],
                         value='BTC', placeholder='Cryptocurrencies sorted by future gains'),
            html.Button(id='activate_tableau'),
            html.Div(className='tableauPlaceholder',
                     id='viz1625607118381',
                     style={'position': 'relative'},
                     children=[html.Noscript(
                         html.A(href='#', id='viz1625607118381_tab',
                                children=html.Img(alt='Sheet 1',
                                                  src='https://public.tableau.com/static/images/DX/DX4J5S42B&/1_rss.png',
                                                  style={'border': 'none'})
                                )
                     ),
                         html.ObjectEl(className='tableauViz',
                                       id='viz1625607118381_object',
                                       style={'display': 'none'},
                                       children=[html.Param(name='host_url',
                                                            value='https://public.tableau.com/'),
                                                 html.Param(name='embed_code_version',
                                                            value='3'),
                                                 html.Param(name='path',
                                                            value='shared/DX4J5S42B'),
                                                 html.Param(name='toolbar',
                                                            value='yes'),
                                                 html.Param(name='static_image',
                                                            value='https://public.tableau.com/static/images/Tw/Tweeter_test/Sheet1/1.png'),
                                                 html.Param(name='animate_transition',
                                                            value='yes'),
                                                 html.Param(name='display_static_image',
                                                            value='yes'),
                                                 html.Param(name='display_spinner',
                                                            value='yes'),
                                                 html.Param(name='display_overlay',
                                                            value='yes'),
                                                 html.Param(name='display_count',
                                                            value='yes'),
                                                 html.Param(name='language',
                                                            value='en-US'),
                                                 ]
                                       )]),
            html.Script(type='text/javascript', children="""
                var divElement = document.getElementById('viz1625607118381');
                var vizElement = divElement.getElementsByTagName('object')[0];
                vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';
                var scriptElement = document.createElement('script');
                scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
                vizElement.parentNode.insertBefore(scriptElement, vizElement);
                """),
            html.Hr(),
            html.Div(
                children=[
                    dcc.Graph(
                        id="graph-0",
                        figure={
                            "data": [
                                {
                                    "x": [1, 2, 3],
                                    "y": [4, 1, 2],
                                    "type": "bar",
                                    "name": "SF",
                                },
                                {
                                    "x": [1, 2, 3],
                                    "y": [2, 4, 5],
                                    "type": "bar",
                                    "name": u"Montréal",
                                },
                            ],
                            "layout": {"title": "Dash Data Visualization"},
                        },
                    )
                ],
                className="row",
            ),
            html.Div(
                children=[
                    html.Div(dcc.Graph(id="graph-1"), className="six columns"),
                    html.Div(
                        dcc.Markdown(
                            """
                        This is a markdown description created with a Dash Core Component.
                        
                        > A {number} days of training to develop.
                        > Ten {number} days of training to polish.
                        >
                        > — Miyamoto Musashi

                        ***
                        """.format(
                                number="thousand"
                            ).replace(
                                "  ", ""
                            )
                        ),
                        className="six columns",
                    ),
                ],
                className="row",
                style={"marginBottom": 20},
            ),
            html.Hr(),
        ],
    )

    return content


def serve_layout():
    content_box = html.Div(id="body",
                           className="content",
                           style={"marginLeft": "0rem",
                                  "marginRight": "rem",
                                  "padding": "2rem 1rem", }
                           )

    layout = html.Div([dcc.Location(id="url"),
                       create_null(10),
                       create_toggle(),

                       create_header(),
                       html.Div(className="main-container", children=[
                           create_sidebar(),
                           html.Div(
                               children=[content_box, create_footer()],
                               id='cont1',
                               className="container",
                               style={"fontFamily": theme["font-family"]},
                           ),
                       ])
                       ])
    return layout


app.layout = serve_layout


# TODO: callbacks

@app.callback(Output("body", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/home"]:
        return home()
    elif pathname == "/forecast":
        return forecast()
    elif pathname == "/historical":
        return historical()
    elif pathname == "/indicators":
        return indicators()
    elif pathname == "/coins":
        return coins()
    elif pathname == "/marketcap":
        return marketcap()
    elif pathname == "/sentiment":
        return sentiment()
    elif pathname == "/covid":
        return covid()
    elif pathname == "/code":
        return create_scratch_content()
    elif pathname == "/github":
        return github()
    elif pathname == "/group":
        return group()
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# Show memory table


# @app.callback(Output('forecast-table', 'data'),
#               Input('forecast-data', 'data'))
# def on_data_set_table(data):
#     if data is None:
#         raise PreventUpdate
#
#     return data

@app.callback(Output('indicator-comparison-tittle', 'children'),
              Output('indicator-regplot', 'figure'),
              Output('indicator-timeplot', 'figure'),
              Input('indicator-data', 'data'),
              Input('indicator-correlation', 'clickData'),
              Input('indicator-group1', 'value'),
              Input('indicator-group2', 'value'), )
def update_indicator_regression(data, clickData, group1, group2):
    if clickData is None:
        raise PreventUpdate
    df = pd.read_json(data, orient='split')
    df.columns = pd.MultiIndex.from_tuples([a.split("<>") for a in df.columns])
    print(clickData)
    sel1 = clickData['points'][0]['x']
    sel2 = clickData['points'][0]['y']
    tname = f'{group1}: {sel1} vs {group2}: {sel2}'
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df[(group1, sel1)],
                              y=df[(group2, sel2)],
                              mode='markers',
                              text=df.index,
                              hovertemplate=f"<b>Date</b> : %{{text}}<br><i>{group1} ({sel1})</i>: %{{x}}<br><i>{group2} ({sel2})</i>: %{{y}}",
                              marker=dict(
                                  color=pd.to_datetime(df.index).view(int),  # set color equal to a variable
                                  colorscale='Viridis',  # one of plotly colorscales
                                  showscale=False,
                              ),showlegend=False
                              ))

    s=df[[(group1, sel1),(group2, sel2)]].dropna()
    x=s[(group1, sel1)]
    y=s[(group2, sel2)]

    slope,intercept,r_value,p_value, stderr=linregress(x,y)
    slope,intercept,r_value,p_value, stderr
    x_lin=np.linspace(x.min(),x.max(),20)
    y_lin=x_lin*slope+intercept
    fig2.add_trace(go.Scatter(x=x_lin,
                              y=y_lin,
                              mode='lines',
                              text=df.index,
                              hovertemplate=f"<b>R2</b> : {r_value**2}<br><b>R</b> : {r_value}<br><b>Slope</b> : {slope}<br><b>Intercept</b> : {intercept}<br><b>p-value</b> : {p_value}<br>",
                              showlegend=False
                              ))

    fig2.update_layout(title=tname,
                       xaxis_title=f'{group1}: {sel1}',
                       yaxis_title=f'{group2}: {sel2}',
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       )
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])

    fig3.add_trace(go.Scatter(x=df.index,
                              y=df[(group1, sel1)],
                              name=f'{group1}: {sel1}',
                              ), secondary_y=False, )
    fig3.add_trace(go.Scatter(x=df.index,
                              y=df[(group2, sel2)],
                              name=f'{group2}: {sel2}'
                              ), secondary_y=True, )
    fig3.update_layout(title=tname,
                       xaxis_title=f'Date',
                       yaxis_title=f'{group1}: {sel1}',
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       )
    fig3.update_yaxes(title_text=f'{group2}: {sel2}', secondary_y=True)
    return tname, fig2, fig3


@app.callback(Output('indicator-data', 'data'),
              Output('indicator-loading-data', 'children'),
              Input('indicator-coin', 'value'))
def update_indicator_data(coin):
    df = pd.read_csv(f's3://ds4a-team151/Alldata_{coin}.csv',
                     header=[0, 1], index_col=0)
    df.columns = [f"{a}<>{b}" for a, b in df.columns]
    return df.to_json(date_format='iso', orient='split'), ''


@app.callback(Output('indicator-correlation', 'figure'),
              Output('indicator-correlation', 'style'),
              Input('indicator-data', 'data'),
              Input('indicator-group1', 'value'),
              Input('indicator-group2', 'value'),
              )
def update_indicator_correlation(data, group1, group2):
    df = pd.read_json(data, orient='split')
    df.columns = pd.MultiIndex.from_tuples([a.split("<>") for a in df.columns])
    group1_cols = [(group1, a) for a in df[group1].columns]
    group2_cols = [(group2, a) for a in df[group2].columns]
    sel = df.loc[:, group1_cols + group2_cols]
    corr = sel.corr().loc[group2, group1]
    corr = corr.dropna(how='all', axis=0).dropna(how='all', axis=1)
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        y=corr.index,
        x=corr.columns,
        z=corr,
        hoverongaps=False,
        hovertemplate=f"<b>Correlation</b> :  %{{z:.2f}}<br><i>{group1}</i>: %{{x}}<br><i>{group2}</i>: %{{y}}",
        colorscale='RdBu_r',
        zmin=-1, zmax=1, ))

    heigth = max(len(group2_cols) * 20, 450)
    return fig, {'height': f'{heigth}px'}


@app.callback(Output('forecast-table', 'data'),
              Input('forecast-data', 'data'),
              Input('forecast-data-prices', 'data'),
              Input('button-1Y', 'n_clicks'),
              Input('button-3M', 'n_clicks'),
              Input('button-1M', 'n_clicks'),
              Input('forecast-risk', 'value'))
def update_forecast_table(coin_data, price_data, n1, n2, n3, slider_values):
    if n1 == 0:
        time_back = 365
    elif n2 == 0:
        time_back = 30 * 3
    elif n3 == 0:
        time_back = 30
    elif n1 > 0:
        time_back = 365
    elif n2 > 0:
        time_back = 30 * 3
    else:
        time_back = 30

    q1, q2 = slider_values

    df = pd.read_json(coin_data, orient='split').T

    # df = pd.read_csv('s3://ds4a-team151/Modelled_coins.csv', index_col=0)
    # df2 = pd.read_csv('s3://ds4a-team151/Modelled_coins_prices.csv', index_col='date')

    # time_back = 30
    # q1 = 0.75
    # q2 = 0.4
    max_date = pd.DatetimeIndex([c.split('_')[3] for c in df.columns if 'model_' in c])[8].date().isoformat()
    df_list = df.loc[:, f'model_StudentT_{time_back}_{max_date}_df']
    loc_list = df.loc[:, f'model_StudentT_{time_back}_{max_date}_loc']
    scale_list = df.loc[:, f'model_StudentT_{time_back}_{max_date}_scale']
    predicted_change_max = np.array(
        [np.exp(t.ppf(q=q1, df=df, loc=loc, scale=scale)) for (df, loc, scale) in zip(df_list, loc_list, scale_list)])
    predicted_change_min = np.array(
        [np.exp(t.ppf(q=q2, df=df, loc=loc, scale=scale)) for (df, loc, scale) in zip(df_list, loc_list, scale_list)])
    small_table = df[['name', 'symbol', 'quote.USD.market_cap', 'quote.USD.price']]
    small_table['predicted_change_min'] = predicted_change_min
    small_table['predicted_change_max'] = predicted_change_max

    small_table['predicted_change'] = (predicted_change_max * predicted_change_min) ** .5
    # small_table.sort_values('predicted_change',ascending=False)
    # small_table[small_table['quote.USD.market_cap'] > 1E9].sort_values('predicted_change', ascending=False)
    small_table = small_table.sort_values('predicted_change', ascending=False)
    small_table.columns = ["Name", "symbol", "Market cap (millions USD)", "Price (USD)", "Minimum predicted change",
                           "Maximum Predicted change", "Predicted change"]
    # print(len(small_table))
    # print([round(a,2) for a in small_table["Market cap (millions USD)"].sort_values()])
    small_table["Market cap (millions USD)"] = (small_table["Market cap (millions USD)"] / 1E6).astype(float).round(2)
    small_table["Price (USD)"] = small_table["Price (USD)"].astype(float).round(2)
    small_table['id'] = small_table.index

    small_table["Minimum predicted change"] = small_table[f"Minimum predicted change"] - 1
    small_table["Maximum Predicted change"] = small_table[f"Maximum Predicted change"] - 1
    small_table["Predicted change"] = small_table["Predicted change"] - 1
    small_table.columns = ["name", "symbol", "market_cap", "price",
                           "max_change", "min_change", "estimated", "id"]
    # print(small_table)
    return small_table.to_dict('records')
    # return {}


@app.callback(
    Output('forecast-table', 'selected_row_ids'),
    Input('forecast-table', 'active_cell'))
def select_row(active_cell):
    if active_cell is None:
        raise PreventUpdate
    return [active_cell['row_id']]


@app.callback(
    Output('forecast-coin', 'value'),
    Input('forecast-table', 'selected_row_ids'),
)
def test(selected):
    if selected is None:
        raise PreventUpdate
    print(selected)
    return selected[0]


@app.callback([
    Output('forecast-graph', 'figure'),
    Output('forecast-kde', 'figure'),
    Output('forecast-QQ', 'figure'),
    Output('forecast-coin-name', 'children'),
    Output('forecast-coin-logo', 'src'),
    Output('forecast-coin-description', 'children'),
    Output('button-1Y', 'n_clicks'),
    Output('button-3M', 'n_clicks'),
    Output('button-1M', 'n_clicks'),
], [
    Input('forecast-data', 'data'),
    Input('forecast-data-prices', 'data'),
    Input('forecast-coin', 'value'),
    Input('button-1Y', 'n_clicks'),
    Input('button-3M', 'n_clicks'),
    Input('button-1M', 'n_clicks'),
    Input('forecast-yaxis-type', 'value')
])
def update_forecast_figure(coin_data, price_data, coin_id, n1, n2, n3, yaxis_type):
    print(coin_id, n1, n2, n3, yaxis_type)
    forecast_coins = pd.read_json(coin_data, orient='split')
    yearly_historical = pd.read_json(price_data, orient='split')
    yearly_historical.columns = yearly_historical.columns.astype(int)

    # parameters
    # col = 1
    # yaxis_type = 'linear'
    if n1 == 0:
        time_back = 365
        n1, n2, n3 = 1, -1, -1
    elif n2 == 0:
        time_back = 30 * 3
        n1, n2, n3 = -1, 1, -1
    elif n3 == 0:
        time_back = 30
        n1, n2, n3 = -1, -1, 1
    elif n1 > 0:
        time_back = 365
        n1, n2, n3 = 1, -1, -1
    elif n2 > 0:
        time_back = 30 * 3
        n1, n2, n3 = -1, 1, -1
    else:
        time_back = 30
        n1, n2, n3 = -1, -1, 1

    prediction_time_back = time_back

    # Check that the column is in the table
    if coin_id not in (yearly_historical.columns):
        print(f'{coin_id} is not a valid id')

    info = forecast_coins[coin_id]
    historical = yearly_historical[coin_id]

    # Get model variables
    mcols = [c for c in info.index if 'model_' in c]
    model_info = info[mcols]
    model_info.name = 'values'
    model_vars = pd.DataFrame([c.split('_')[1:] for c in mcols], columns=['model', 'timeback', 'date', 'variable'])
    model_vars.index = mcols
    model_results = pd.concat([model_vars, model_info], axis=1).reset_index()
    model_results['timeback'] = model_results['timeback'].astype(int)
    model_results['date'] = pd.to_datetime(model_results['date']).dt.date

    # Get standar deviation of distribution
    model_std = model_results[(model_results['model'] == 'StudentT') &
                              (model_results['timeback'] == time_back) &
                              (model_results['variable'].isin([f'std{i:.0f}' for i in np.linspace(-2, 2, 5)]))]
    model_std = model_std.pivot(index='date', columns='variable', values='values')

    # Get parameters of distribution
    model_tparams = model_results[(model_results['model'] == 'StudentT') &
                                  (model_results['timeback'] == time_back) &
                                  (model_results['variable'].isin(['df', 'loc', 'scale']))]
    model_tparams = model_tparams.pivot(index='date', columns='variable', values='values')

    # Compute prediction
    predictions = info['quote.USD.price'] * model_std

    # Reindex
    historical.index = pd.DatetimeIndex(historical.index)
    predictions.index = pd.DatetimeIndex(predictions.index)

    last_prices = historical[-time_back:]

    # Initialize figure
    fig = go.Figure()

    # Real price
    fig.add_trace(go.Scatter(name='Prices', x=historical.index, y=historical,
                             line=dict(color='rgba(53,130,196,1)', width=4), showlegend=False))
    if predictions['std0'].iloc[-1] > predictions['std0'].iloc[0]:
        fillcolor1 = 'rgba(0,138,32,0.4)'
        fillcolor2 = 'rgba(0,112,23,0.6)'
        color = 'rgba(0,92,18,1)'
    else:
        fillcolor1 = 'rgba(138,36,36,0.4)'
        fillcolor2 = 'rgba(105,28,28,0.6)'
        color = 'rgba(69,19,19,1)'

    # Predicted prices (from wide to narrow)
    fig.add_trace(go.Scatter(name='95.5%',
                             x=pd.DatetimeIndex([*predictions.index, *predictions.index[::-1]]),
                             y=[*predictions['std2'], *predictions['std-2'][::-1]],
                             fill='toself',
                             fillcolor=fillcolor1,
                             line_color='rgba(255,255,255,0)',
                             showlegend=True,
                             ))
    fig.add_trace(go.Scatter(name='68.3%',
                             x=pd.DatetimeIndex([*predictions.index, *predictions.index[::-1]]),
                             y=[*predictions['std1'], *predictions['std-1'][::-1]],
                             fill='toself',
                             fillcolor=fillcolor2,
                             line_color='rgba(255,255,255,0)',
                             showlegend=True,
                             ))
    fig.add_trace(go.Scatter(name='Prediction mean', x=predictions.index, y=predictions['std0'],
                             line=dict(color=color, width=4)))

    # Formatting layout
    name = f' {info["name"]} ({info["symbol"]}) price forecast '

    fig.update_layout(title=name,
                      xaxis_title='Date',
                      yaxis_title='Price ($)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      yaxis_type=yaxis_type
                      )
    xmin = predictions.index.min() - datetime.timedelta(time_back)
    xmax = predictions.index.max()
    ymax = max(predictions.iloc[:, 1:-1].max().max(), last_prices.loc[xmin:].max())
    ymin = min(predictions.iloc[:, 1:-1].min().min(), last_prices.loc[xmin:].min())
    fig.update_xaxes(range=[xmin, xmax])
    if yaxis_type == 'linear':
        fig.update_yaxes(range=[ymin, ymax])
    else:
        fig.update_yaxes(range=[np.log(ymin) / np.log(10), np.log(ymax) / np.log(10)])

    description = info["description3"]
    logo = info["logo"]

    print('Generated forecast figure')

    hist_data = [np.log((last_prices / last_prices.shift(period)).dropna()) for period in range(1, 15)][::-1]
    group_labels = [f'{n} day{"s" if n > 1 else ""}' for n in range(1, 15)][::-1]  # name of the dataset

    fig2 = ff.create_distplot(hist_data, group_labels, show_hist=False)

    fig2.update_layout(title=f'{info["name"]} ({info["symbol"]}) kernel distribution estimation of change of price',
                       xaxis_title='LOG (ROCR)',
                       yaxis_title='Probability density',
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       yaxis_type='linear'
                       )

    for trace in fig2.select_traces():
        if trace.legendgroup not in ['1 day', '3 days', '14 days']:
            trace.visible = 'legendonly'

    xmin = min(hist_data[-1])
    xmax = max(hist_data[-1])
    fig2.update_xaxes(range=[xmin, xmax])
    print('Generated kde figure')

    # Initialize figure
    fig3 = go.Figure()

    q_data2 = []
    for i, (date, (df, loc, scale)) in enumerate(model_tparams[::-1].iloc[:-1, :].iterrows()):
        x = hist_data[i].sort_values()
        q_list = np.arange(len(x)) / (len(x) + 1) + 0.5 / (len(x) + 1)
        theoretical_x = [t.ppf(q=q, df=df, loc=loc, scale=scale) for q in q_list]
        fig3.add_trace(go.Scatter(name=group_labels[i], x=theoretical_x, y=x, showlegend=True, mode='markers'))

        # plt.scatter(theoretical_x,x)
        q_data = pd.DataFrame(np.array([q_list, x, theoretical_x]).T, columns=['q', 'real', 'theoretical'])
        q_data['label'] = group_labels[i]
        q_data2 += [q_data]

    q_data = pd.concat(q_data2)
    xmin = q_data[['real', 'theoretical']].min().min()
    xmax = q_data[['real', 'theoretical']].max().max()
    xmin = min(xmin, -xmax) * 1.02
    xmax = max(-xmin, xmax) * 1.02

    fig3.add_trace(go.Scatter(name='theoretical', x=[xmin, xmax], y=[xmin, xmax], showlegend=False))
    fig3.update_xaxes(range=[xmin, xmax])
    fig3.update_yaxes(range=[xmin, xmax])

    # Formatting layout
    fig3.update_layout(title=f'{info["name"]} ({info["symbol"]}) Q-Q plot ',
                       xaxis_title='Theoretical quantiles',
                       yaxis_title='Observed quantiles',
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       )

    for trace in fig3.select_traces():
        if trace.name not in ['1 day', '3 days', '14 days', 'theoretical']:
            trace.visible = 'legendonly'
    print('Generated qq figure')

    return [fig, fig2, fig3, name, logo, description, n1, n2, n3]


#########################
# Client side callbacks #
#########################

# Toggle Navigation
app.clientside_callback(
    """
    function (data1,n1) {
        $(".toggle").toggleClass("open");
        $(".side-navigation").toggleClass("open");
        $(".container").toggleClass("open");
        return {}
    }
    """
    ,
    Output('null1', 'data'),
    Input('null1', 'data'),
    Input('toggleB', 'n_clicks'),
)

# Activate Dash
app.clientside_callback(
    """
    function (x) {
        var divElement = document.getElementById('viz1625607118381');
        var vizElement = document.getElementById('viz1625607118381_object');
        vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';
        var scriptElement = document.createElement('script');
        scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
        vizElement.parentNode.insertBefore(scriptElement, vizElement);
        return {}
    }
    """
    ,
    Output('null2', 'data'),
    Input('activate_tableau', 'n_clicks')
)

# Activate Dash
app.clientside_callback(
    """
    function (x) {
        var divElement = document.getElementById('viz1628020240288');
        var vizElement = divElement.getElementsByTagName('object')[0];
        vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';
        var scriptElement = document.createElement('script');
        scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
        vizElement.parentNode.insertBefore(scriptElement, vizElement);
    }
    """
    ,
    Output('null3', 'data'),
    Input('activate_tableau_viz1628020240288', 'n_clicks')
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run_server(debug=debug, port=port, threaded=True)
