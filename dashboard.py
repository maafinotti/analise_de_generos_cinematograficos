import json
import pandas as pd
import requests
import time
import ast
import sqlite3
from sqlite3 import Error
import plotly.express as px

df_genres = pd.read_csv('genres.csv')
df_genres = df_genres.sort_values(by='name')

genres_id = df_genres['id'].tolist()

df = pd.read_csv('filmes.csv')

id_to_name = dict(zip(df_genres['id'], df_genres['name']))

df['genre_ids'] = df['genre_ids'].apply(ast.literal_eval)

df['genres_names'] = df['genre_ids'].map(lambda ids: [id_to_name[id] for id in ids])

df = df.drop_duplicates(subset='original_title')
df.reset_index(drop=True, inplace=True)

map_language = {
    'en': 'English',
    'id': 'Indonesian',
    'pt': 'Portuguese',
    'zh': 'Chinese',
    'es': 'Spanish',
    'ko': 'Korean',
    'it': 'Italian',
    'ja': 'Japanese',
    'th': 'Thai',
    'fr': 'French',
    'hi': 'Hindi',
    'da': 'Danish',
    'sv': 'Swedish',
    'tr': 'Turkish',
    'ru': 'Russian',
    'de': 'German',
    'mn': 'Mongolian',
    'no': 'Norwegian',
    'tl': 'Tagalog',
    'pl': 'Polish',
    'fi': 'Finnish'
}

# Substituindo os códigos de idiomas pelos nomes dos países no DataFrame
df['original_language'] = df['original_language'].map(map_language)

unique_languages = df['original_language'].unique()

id_idioma = {idioma: id for id, idioma in enumerate(unique_languages, start=1)}
df['id_language'] = df['original_language'].map(id_idioma)

df.drop(['adult', 'backdrop_path', 'poster_path', 'video', 'original_title'], axis = 1, inplace = True)

df = df[['id', 'title', 'overview', 'id_language', 'original_language', 'release_date', 'genre_ids', 'genres_names', 'popularity', 'vote_average', 'vote_count']]

df['release_date'] = pd.to_datetime(df['release_date'])

df = df[df['release_date'] <= '2024-04-04']

# Obter todos os gêneros únicos presentes nos dados
generos_unicos = set([genero for lista_generos in df['genres_names'] for genero in lista_generos])

# Criar colunas dinamicamente com base nos genres_names únicos
for genero in generos_unicos:
    df[genero] = df['genres_names'].apply(lambda x: 1 if genero in x else 0)

genres_columns = df.columns[11:]


films_genres = df[genres_columns].sum().reset_index()
films_genres = films_genres.rename(columns={'index': 'genero', 0: 'qtd_filmes'}).reset_index(drop=True).sort_values(by='genero')

language_genres = df.groupby('original_language')[genres_columns].sum().reset_index()

df['release_date'] = pd.to_datetime(df['release_date'])
df['release_year'] = df['release_date'].dt.year
date_genres = df.groupby('release_year')[genres_columns].sum().reset_index()

date_count_films = df['release_year'].value_counts().reset_index()

popularity_genres = pd.DataFrame(columns=['genero', 'avg_popularidade'])
for genero in genres_columns:
    films_w_genre = df[df[genero] == 1]  # Filtrar os filmes com o gênero atual
    avg_popularity = films_w_genre['popularity'].mean()
    df_temp = pd.DataFrame({'genero': [genero], 'avg_popularidade': [avg_popularity]})
    popularity_genres = pd.concat([popularity_genres, df_temp], ignore_index=True)
popularity_genres = popularity_genres.sort_values(by='genero')

avg_vote = pd.DataFrame(columns=['genero', 'avg_voto'])
for genero in genres_columns:
    films_w_genre = df[df[genero] == 1]  # Filtrar os filmes com o gênero atual
    vote = films_w_genre['vote_average'].mean()
    df_temp = pd.DataFrame({'genero': [genero], 'avg_voto': [vote]})
    avg_vote = pd.concat([avg_vote, df_temp], ignore_index=True)
avg_vote = avg_vote.sort_values(by='genero')

qty_vote = pd.DataFrame(columns=['genero', 'qtd_voto'])
for genero in genres_columns:
    films_w_genre = df[df[genero] == 1]  # Filtrar os filmes com o gênero atual
    count_vote = films_w_genre['vote_count'].sum()
    df_temp = pd.DataFrame({'genero': [genero], 'qtd_voto': [count_vote]})
    qty_vote = pd.concat([qty_vote, df_temp], ignore_index=True)
qty_vote = qty_vote.sort_values(by='genero')

avg_popularity_date = df.groupby('release_year')['popularity'].mean().reset_index()

vote_count_date = df.groupby('release_year')['vote_count'].sum().reset_index()



films_genres_fig = px.bar(films_genres, x='qtd_filmes', y='genero', orientation='h', color_discrete_sequence=['#3A5569'])
films_genres_fig.update_layout(xaxis_title='Quantidade de Filmes', yaxis_title='Gênero', title={'text': 'Quantidade de Filmes por Gênero', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

language_genres_fig = px.imshow(language_genres.set_index('original_language'),  width=600, height=500, color_continuous_scale='ice_r')
language_genres_fig.update_layout(xaxis_title='Gêneros', yaxis_title='Idioma Original', title={'text': 'Quantidade de Filmes por Gênero e Idioma Original', 'font': {'size': 17}}, coloraxis_colorbar=dict(x=0.9, y=0.5))

date_genres_fig = px.line(date_genres, x='release_year', y=genres_columns)
date_genres_fig.update_layout(xaxis_title='Ano', yaxis_title='Quantidade de Filmes', title={'text': 'Quantidade de Filmes por Gênero ao longo dos Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

date_count_films_fig = px.bar(date_count_films, x='release_year', y='count', color_discrete_sequence=['#3A5569'])
date_count_films_fig.update_layout(xaxis_title='Ano', yaxis_title='Quantidade de Filmes', title={'text': 'Quantidade de Filmes Lançados nos Últimos Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

date_count_films_10_fig = px.bar(date_count_films.head(10), x='release_year', y='count', color_discrete_sequence=['#3A5569'])
date_count_films_10_fig.update_layout(xaxis_title='Ano', yaxis_title='Quantidade de Filmes', title={'text': 'Quantidade de Filmes Lançados nos Últimos 10 Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50), xaxis=dict(tickmode='linear', dtick=1))

popularity_genres_fig = px.bar(popularity_genres, x='avg_popularidade', y='genero', orientation='h', color_discrete_sequence=['#3A5569'])
popularity_genres_fig.update_layout(xaxis_title='Média de Popularidade', yaxis_title='Gênero', title={'text': 'Média de Popularidade por Gênero', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

avg_vote_fig = px.bar(avg_vote, x='avg_voto', y='genero', orientation='h', color_discrete_sequence=['#3A5569'])
avg_vote_fig.update_layout(xaxis_title='Média de Votos', yaxis_title='Gênero', title={'text': 'Média de Votos por Gênero', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

qty_vote_fig = px.bar(qty_vote, x='qtd_voto', y='genero', orientation='h', color_discrete_sequence=['#3A5569'])
qty_vote_fig.update_layout(xaxis_title='Quantidade de Votos', yaxis_title='Gênero', title={'text': 'Quantidade de Votos por Gênero', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

avg_popularity_date_fig = px.line(avg_popularity_date, x='release_year', y='popularity', color_discrete_sequence=['#3A5569'])
avg_popularity_date_fig.update_layout(xaxis_title='Ano', yaxis_title='Popularidade', title={'text': 'Média de Popularidade ao longo dos Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

vote_count_date_fig = px.line(vote_count_date, x='release_year', y='vote_count', color_discrete_sequence=['#3A5569'])
vote_count_date_fig.update_layout(xaxis_title='Ano', yaxis_title='Quantiddade de Votos', title={'text': 'Quantidade Total de Votos ao longo dos Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

option_genre = [{'label': 'Todos Gêneros', 'value': 0}]
for i in films_genres['genero'].unique():
    option_genre.append({'label': i, 'value': i})

####dashboard

import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import ast
from dash.exceptions import PreventUpdate


# import from folders/ theme changer
from dash_bootstrap_templates import ThemeSwitchAIO

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
server = app.server


#styles
tab_card = {'height': '100%'}

main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.9, 
                "xanchor":"left",
                "x":0.1,
                "title": {"text": None},
                "font" :{"color":"white"},
                "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":10, "r":10, "t":10, "b":10}
}

config_graph={"displayModeBar": False, "showTips": False}

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

#layout
app.layout = dbc.Container(children = [ 
    # Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([  
                            html.Legend("Análise de Filmes por Gênero")
                        ], sm=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])
                        ]),
                    dbc.Row([
                        html.Img(src='https://www.pucsp.br/sites/default/files/download/brasao-PUCSP-assinatura-principal-RGB.png', height="200px")
                        ]),
                    ], style={'margin-top': '10px'}),
                    dbc.Row([
                        dbc.Button("Acesse o Github", href="https://github.com/maafinotti/analise_de_generos_de_filmes", target="_blank")
                    ], style={'margin-top': '10px'})
                ])
            ], style=tab_card)
        ], sm=4, lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph1', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=7),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5('Escolha o Gênero'),
                            dcc.Dropdown(
                                id="genre-select",
                                options=option_genre,
                                value=option_genre[0]['value'],
                                multi=False,
                                clearable=False,
                                className='dbc'
                            )
                        ])
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            html.H5('Filtrar por Ano'),
                            dbc.Input(
                                id='year-start', 
                                type='number', 
                                min=df['release_year'].min(), 
                                max=df['release_year'].max(), 
                                placeholder='Ano Inicial',
                                className='dbc',
                                value=df['release_year'].min()
                                ),
                            html.Br(),
                            dbc.Input(
                                id='year-end', 
                                type='number', 
                                min=df['release_year'].min(), 
                                max=df['release_year'].max(), 
                                placeholder='Ano Final', 
                                className='dbc',
                                value=df['release_year'].max()
                                ),
                            dbc.Button('Filtrar', 
                                       id='year_select', 
                                       color='primary', 
                                       className='mt-2',
                                       n_clicks=1)
                        ])
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=3),
    ], className='g-2 my-auto', style={'margin-top': '7px'}),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph2', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph3', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph4', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph5', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph6', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph7', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph8', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph9', className='dbc', config=config_graph)
                        ], sm=12, md=12)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
    ], className='g-2 my-auto', style={'margin-top': '7px'})
    

], fluid = True, style = {'height': '100vh'})

# ======== Callbacks ========== #
# Graph 1
@app.callback(
    Output('graph1', 'figure'),
    Input('genre-select', 'value'),
     Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph1(genre, toggle):

    template = template_theme1 if toggle else template_theme2
    
    if genre == 0:  # Se o valor selecionado for 0 (Todos Gêneros), mostrar o gráfico padrão
        fig = films_genres_fig
    else:  # Caso contrário, filtrar os dados por gênero selecionado
        filtered_df = df[df[genre] == 1]  # Filtrar os filmes com o gênero selecionado
        films_genres_filtered = filtered_df[genres_columns].sum().reset_index()
        films_genres_filtered = films_genres_filtered.rename(columns={'index': 'genero', 0: 'qtd_filmes'}).reset_index(drop=True).sort_values(by='genero')
        fig = px.bar(films_genres_filtered, x='qtd_filmes', y='genero', orientation='h', color_discrete_sequence=['#3A5569'])
        fig.update_layout(xaxis_title='Quantidade de Filmes', yaxis_title='Gênero', title={'text': 'Quantidade de Filmes por Gênero', 'font': {'size': 17}})
    
    return fig
#graph 2
@app.callback(
    Output('graph2', 'figure'),
    Input('year_select', 'n_clicks'),
    State('year-start', 'value'),
    State('year-end', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def graph2(n_clicks, year_start, year_end, toggle):

    template = template_theme1 if toggle else template_theme2

    if n_clicks is None:
        raise PreventUpdate
 
    else:
        filtered_df = df[(df['release_year'] >= year_start) & (df['release_year'] <= year_end)]
        filtered_date_genres = filtered_df.groupby('release_year')[genres_columns].sum().reset_index()

        fig = px.line(filtered_date_genres, x='release_year', y=genres_columns)
        fig.update_layout(xaxis_title='Ano', yaxis_title='Quantidade de Filmes', 
                        title={'text': 'Quantidade de Filmes por Gênero ao longo dos Anos', 'font': {'size': 17}},
                        margin=dict(t=50, b=50, r=50))

    return fig
#graph3
@app.callback(
    Output('graph3', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph3(toggle):

    template = template_theme1 if toggle else template_theme2

    language_genres = df.groupby('original_language')[genres_columns].sum().reset_index()
    language_genres_fig = px.imshow(language_genres.set_index('original_language'),  width=600, height=500, color_continuous_scale='ice_r')
    language_genres_fig.update_layout(xaxis_title='Gêneros', yaxis_title='Idioma Original', title={'text': 'Quantidade de Filmes por Gênero e Idioma Original', 'font': {'size': 17}}, coloraxis_colorbar=dict(x=0.9, y=0.5))
    return language_genres_fig

#graph4
@app.callback(
    Output('graph4', 'figure'),
    Input('year_select', 'n_clicks'),
    State('year-start', 'value'),
    State('year-end', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def graph4(n_clicks, year_start, year_end, toggle):

    template = template_theme1 if toggle else template_theme2

    if n_clicks is None:
        raise PreventUpdate
 
    else:
        filtered_df = df[(df['release_year'] >= year_start) & (df['release_year'] <= year_end)]
        filtered_date_vote = filtered_df['release_year'].value_counts().reset_index()
        date_count_films_fig = px.bar(filtered_date_vote, x='release_year', y='count', color_discrete_sequence=['#3A5569'])
        date_count_films_fig.update_layout(xaxis_title='Ano', yaxis_title='Quantidade de Filmes', title={'text': 'Quantidade de Filmes Lançados nos Últimos Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

    return date_count_films_fig


#graph5
@app.callback(
    Output('graph5', 'figure'),
    Input('year_select', 'n_clicks'),
    State('year-start', 'value'),
    State('year-end', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def graph5(n_clicks, year_start, year_end, toggle):

    template = template_theme1 if toggle else template_theme2

    if n_clicks is None:
        raise PreventUpdate
 
    else:
        filtered_df = df[(df['release_year'] >= year_start) & (df['release_year'] <= year_end)]
        filtered_date_vote = filtered_df.groupby('release_year')['vote_count'].sum().reset_index()
        fig = px.line(filtered_date_vote, x='release_year', y='vote_count', color_discrete_sequence=['#3A5569'])
        fig.update_layout(xaxis_title='Ano', yaxis_title='Quantiddade de Votos', title={'text': 'Quantidade Total de Votos ao longo dos Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

    return fig

#graph6
@app.callback(
    Output('graph6', 'figure'),
    Input('year_select', 'n_clicks'),
    State('year-start', 'value'),
    State('year-end', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def graph6(n_clicks, year_start, year_end, toggle):

    template = template_theme1 if toggle else template_theme2

    if n_clicks is None:
        raise PreventUpdate
 
    else:
        filtered_df = df[(df['release_year'] >= year_start) & (df['release_year'] <= year_end)]
        filtered_date_vote = filtered_df.groupby('release_year')['popularity'].mean().reset_index()
        avg_popularity_date_fig = px.line(filtered_date_vote, x='release_year', y='popularity', color_discrete_sequence=['#3A5569'])
        avg_popularity_date_fig.update_layout(xaxis_title='Ano', yaxis_title='Popularidade', title={'text': 'Média de Popularidade ao longo dos Anos', 'font': {'size': 17}}, margin=dict(t=50, b = 50, r = 50))

    return avg_popularity_date_fig

# Graph7
@app.callback(
    Output('graph7', 'figure'),
     Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph7(toggle):

    template = template_theme1 if toggle else template_theme2
    return popularity_genres_fig

# Graph8
@app.callback(
    Output('graph8', 'figure'),
     Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph8(toggle):

    template = template_theme1 if toggle else template_theme2
    return qty_vote_fig

# Graph9
@app.callback(
    Output('graph9', 'figure'),
     Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph9(toggle):

    template = template_theme1 if toggle else template_theme2
    return avg_vote_fig

if __name__ == '__main__':
    app.run_server(debug=True)
