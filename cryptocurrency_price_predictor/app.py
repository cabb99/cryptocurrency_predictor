import os

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import chart_studio.plotly as py
import pandas as pd
import plotly.graph_objs as go

from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv

import plotly.graph_objects as go
from scipy.stats import norm
from scipy.stats import t
import talib
import numpy as np
import pandas as pd
import datetime

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

theme = {"font-family": "Arial",
         "background-color": "#e0e0e0"}

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
                    dbc.NavLink([html.I(className="fas fa-coins"), " Coins"],
                                href="/coins", id="page-4-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-chart-pie"), " Market Cap"],
                                href="/marketcap", id="page-5-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-heart"), " Sentiment"],
                                href="/sentiment", id="page-6-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-virus"), " COVID"],
                                href="/covid", id="page-7-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-code"), " Code"],
                                href="/code", id="page-8-link", className="page-link"),
                    dbc.NavLink([html.I(className="fab fa-github"), " Github"],
                                href="https://github.com/cabb99/cryptocurrency_predictor",
                                target='_blank', id="page-9-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-users"), " Group"],
                                href="/group", id="page-10-link", className="page-link"),
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

    div = html.Div([p0, p1, a_fa],
                   id="foot",
                   className="footer", )
    footer = html.Footer(children=div)
    return footer


def home():
    content = html.Div([
        html.H2('Overview'),
        html.P("""Cryptocurrency is a burgeoning asset class with investors flocking to invest in all types of cryptos. 
Bitcoin by itself has been the best performing asset in the past 10 years with an annualized return of 230%.
1 bitcoin was valued at $1 in 2011 and now (2021) hovers in the $50,000 range, a whopping 5,000,000% increase."""),
        html.Br(),
        html.P("""As more and more people look to diversify their portfolio and have exposure to this new asset class,
having a tool to give investors and speculators alike an idea of how crypto prices will move will be a tremendous 
advantage."""),
        html.Br(),
        html.P("""Because cryptocurrency is still relatively new, it is difficult to determine what drives price 
movement and volatility. Technical analysis alone would not be sufficient to predict price movement and it may not even 
be the strongest determinant of price due to the lack of empirical evidence and history. In the example of Dogecoin, 
price movement has been driven by tweets from Elon Musk and momentum investing with very little to-no fundamental 
support. We want to provide a tool for people to use to make informed investment decisions when it comes to 
cryptocurrencies.
"""),
    ])
    return content


def forecast():
    df = pd.read_csv('s3://ds4a-team151/Forecast_coins.csv', index_col=0)
    df2 = df[:100].copy()
    df2['label'] = df2['name']
    df2['value'] = df2.index
    crypto_options = list(df2[['label', 'value']].T.to_dict().values())
    # print(crypto_options)

    content = html.Div([
        html.H2('Price forecast'),
        html.Div(
            #[html.H3('Coin forecast'), ] +
            [dcc.Dropdown(id='forecast-coin', className='forecast-selection', options=crypto_options,
                          value=1, placeholder='Cryptocurrencies sorted by future gains')] +
            [html.Button(i, id=f'button-{i}', n_clicks=0, className='forecast-button') for i in ['1Y', '3M', '1M']] +
            [dcc.RadioItems(id='forecast-yaxis-type', className='forecast-radio', options=[
                {'label': 'Linear', 'value': 'linear'},
                {'label': 'Logarithmic', 'value': 'log'}],
                            value='linear')] +
            [html.H2([html.Img(id='forecast-coin-logo', className='forecast-coin-logo'),
                      html.P('sample-name', id='forecast-coin-name', className='forecast-coin-name')])] +
            [dcc.Graph(id='forecast-graph', )] +
            [html.P('Sample description', id='forecast-coin-description')]
        ), html.Div(
            [html.H3('Forecast overview'),
             html.Div('Barplot overview of forecasts for some coins', className='placeholder')]
        )])
    return content


def historical():
    content = html.Div([
        html.H2('Historical prices'),
        html.Hr(),
        html.Div([
            dcc.DatePickerRange(),
            dcc.Dropdown(id='historical-coin', options=[
                {'label': 'Bitcoin', 'value': 'BTC'},
                {'label': 'Ethereum', 'value': 'ETH'},
                {'label': 'Dogecoin', 'value': 'DOGE'}
            ], value='BTC', placeholder='Select coin to compare history'),
            html.Div('Historical Crypto Price Line Chart for Specific Dates', className='placeholder'),
            html.Div('Historical Events aligned with above chart timeline (Hover to know event)',
                     className='placeholder'),
        ])
    ])
    return content


def indicators():
    content = html.Div([
        html.H2('Indicators'),
        html.Hr(),
        html.Div([
            html.Div('Correlation Matrix for each crypto with all indicators', className='placeholder')
        ])
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
        html.P("""One of the most important recent events has been the COVID-19 pandemic. 
        It disrupted the life of people around the world, forcing them to rethink their jobs, stay at home, 
        practice social distancing, and to change their life priorities. During the same time some cryptocurrencies 
        like bitcoin had a trend upwards. We observed that this correlation is stronger when we focus on particular 
        countries, like UK, US or Russia."""),
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
                           style={
                               "marginLeft": "0rem",
                               "marginRight": "rem",
                               "padding": "2rem 1rem", }
                           )

    layout = html.Div((dcc.Location(id="url"),
                       create_null(10),
                       create_toggle(),
                       create_sidebar(),
                       html.Div(
                           children=[create_header(), content_box, create_footer()],
                           id='cont1',
                           className="container",
                           style={"fontFamily": theme["font-family"]},
                       ),

                       ))
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


@app.callback([
    Output('forecast-graph', 'figure'),
    Output('forecast-coin-name', 'children'),
    Output('forecast-coin-logo', 'src'),
    Output('forecast-coin-description', 'children'),
    Output('button-1Y', 'n_clicks'),
    Output('button-3M', 'n_clicks'),
    Output('button-1M', 'n_clicks'),
], [
    Input('forecast-coin', 'value'),
    Input('button-1Y', 'n_clicks'),
    Input('button-3M', 'n_clicks'),
    Input('button-1M', 'n_clicks'),
    Input('forecast-yaxis-type', 'value')
])
def update_forecast_figure(col, n1, n2, n3, yaxis_type):
    print(col,n1,n2,n3,yaxis_type)
    forecast_coins = pd.read_csv('s3://ds4a-team151/Forecast_coins.csv', index_col=0)
    yearly_historical = pd.read_csv('s3://ds4a-team151/yearly_historical.csv', index_col='date')
    last_prices = yearly_historical
    last_prices.columns = last_prices.columns.astype(int)

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
    if col not in (last_prices.columns):
        print(f'{col} is not a valid id')

    # Fit prices to a T

    price_ts = last_prices[-prediction_time_back:][col]
    tt = []
    for period in range(1, 15):
        y = np.log(talib.ROCR(price_ts, timeperiod=period).dropna())
        tdof, tloc, tscale = t.fit(y)
        tt += [[tdof, tloc, tscale] +
               list(np.exp(t.ppf(q=[norm.cdf(np.linspace(-3, 3, 7))], df=tdof, loc=tloc, scale=tscale)[0])) +
               list(np.exp(t.rvs(df=tdof, loc=tloc, scale=tscale, size=100)))]
        print(period, tdof, tloc, tscale)

    # Format predictions
    tt = pd.DataFrame(tt,
                      columns=['df', 'loc', 'scale'] + [f'std{i:.0f}' for i in np.linspace(-3, 3, 7)] + [f'gain{i:02d}'
                                                                                                         for i in
                                                                                                         range(100)])

    # Format predictions
    predictions = last_prices[col].iloc[-1] * tt.iloc[:, 3:10]
    predictions.index = [(pd.DatetimeIndex(last_prices.index)[-1] + datetime.timedelta(1 + i)).date().isoformat() for i
                         in predictions.index]
    for q in predictions.columns:
        predictions.at[pd.DatetimeIndex(last_prices.index)[-1].date().isoformat(), q] = last_prices[col].iloc[-1]
    predictions = predictions.sort_index()

    # Reindex
    last_prices.index = pd.DatetimeIndex(last_prices.index)
    predictions.index = pd.DatetimeIndex(predictions.index)

    # Initialize figure
    fig = go.Figure()

    # Real price
    fig.add_trace(go.Scatter(name='Prices', x=last_prices.index, y=last_prices[col],
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
    fig.update_layout(title=f'{forecast_coins["name"][col]} ({forecast_coins["symbol"][col]}) price prediction',
                      xaxis_title='Date',
                      yaxis_title='Price ($)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      yaxis_type=yaxis_type
                      )
    xmin = predictions.index.min() - datetime.timedelta(time_back)
    xmax = predictions.index.max()
    ymax = max(predictions.iloc[:, 1:-1].max().max(), last_prices.loc[xmin:, col].max())
    ymin = min(predictions.iloc[:, 1:-1].min().min(), last_prices.loc[xmin:, col].min())
    fig.update_xaxes(range=[xmin, xmax])
    if yaxis_type == 'linear':
        fig.update_yaxes(range=[ymin, ymax])
    else:
        fig.update_yaxes(range=[np.log(ymin) / np.log(10), np.log(ymax) / np.log(10)])

    description = forecast_coins["description3"][col]
    logo = forecast_coins["logo"][col]
    name = f' {forecast_coins["name"][col]} price forecast '
    # Show figure
    print('Generated forecast figure')
    return [fig, name, logo, description, n1, n2, n3]


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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run_server(debug=debug, port=port, threaded=True)
