import os

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import chart_studio.plotly as py
import plotly.graph_objs as go

from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv
from exceptions import ImproperlyConfigured

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
    raise ImproperlyConfigured("Plotly credentials not set in .env")

app_name = "Cryptocurrency Price Predictor"
server = Flask(app_name)

try:
    # server.secret_key = os.environ["SECRET_KEY"]
    pass
except KeyError:
    raise ImproperlyConfigured("SECRET KEY not set in .env:")

external_js = [
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML",  # Latex
    "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js",  # Animations
]

external_css = [

    "https://codepen.io/chriddyp/pen/bWLwgP.css",  # Dash stylesheet
    "https://fonts.googleapis.com/css?family=Lobster|Raleway",  # Fonts
    #"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.3/css/fontawesome.min.css",  # Fonts
    {
        'href': 'https://use.fontawesome.com/releases/v5.15.3/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-SZXxX4whJ79/gErwcOYf+zWLeJdY/qpuqC4cAa9rOGUstPomtqpuNWT9wdPEn2fk',
        'crossorigin': 'anonymous'
    },
]

external_stylesheets = [

]

theme = {"font-family": "Lobster",
         "background-color": "#e0e0e0"}

app = Dash(name=app_name, server=server,
           external_stylesheets=external_css,
           external_scripts=external_js,
           meta_tags=[{"name": "viewport", "content": "width=device-width"}])


def create_null(n):
    return html.Div(children=[dcc.Store(id=f'null{i}', data=[]) for i in range(n)])

def create_toggle():
    button = html.A(className="toggle", id="toggleB",
                    children=[html.I(),
                              html.I(),
                              html.I()])
    return button


def create_sidebar():
    sidebar = html.Div(
        [
            html.H2("Menu", className="menu-tittle", id='menuTittle'),
            dbc.Nav(
                [
                    dbc.NavLink([html.I(className="fas fa-home"), " Home"],
                                href="/home", id="page-home-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-chart-line"), " Real-time"],
                                href="/real-time", id="page-1-link", className="page-link"),
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
                                href="/page-9", id="page-9-link", className="page-link"),
                    dbc.NavLink([html.I(className="fas fa-users"), " Group"],
                                href="/page-10", id="page-10-link", className="page-link"),
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
    header = html.Header(
        children=[html.H1(children=html.A(app_name, href="/home"), id='headTittle')],
        id="head", className="header")
    return header


def create_content():
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


def create_footer():
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


# for js in external_js:
#    app.scripts.append_script({"external_url": js})
# for css in external_css:
#    app.css.append_css({"external_url": css})


# TODO: callbacks

@app.callback(Output("body", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/code"]:
        return create_content()
    elif pathname == "/real-time":
        return html.P("This is the content of page 1!")
    elif pathname == "/historical":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/indicators":
        return html.P("Oh cool, this is page 3!")

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


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

#Activate Dash
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
