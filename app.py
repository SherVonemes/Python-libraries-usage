import zipfile
import wget
import dash
from dash import html, dcc, Input, Output
import numpy as np
import json
import pandas as pd
import plotly.express as px
from urllib.request import urlopen

with urlopen(
        "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
) as response:
    brazil = json.load(response)

for feature in brazil["features"]:
    feature["id"] = feature["properties"]["sigla"]

url = 'https://github.com/Palladain/Deep_Python/raw/main/Homeworks/Homework_1/archive.zip'
filename = wget.download(url)

with zipfile.ZipFile(filename, 'r') as zip_ref:
    zip_ref.extractall('./')

customers = pd.read_csv('olist_customers_dataset.csv')
location = pd.read_csv('olist_geolocation_dataset.csv')
items = pd.read_csv('olist_order_items_dataset.csv')
payments = pd.read_csv('olist_order_payments_dataset.csv')
reviews = pd.read_csv('olist_order_reviews_dataset.csv')
orders = pd.read_csv('olist_orders_dataset.csv')
products = pd.read_csv('olist_products_dataset.csv')
translation = pd.read_csv('product_category_name_translation.csv')
sellers = pd.read_csv('olist_sellers_dataset.csv')

orders_products = orders.merge(items, on='order_id')
orders_products = orders_products.merge(products, on='product_id')
orders_products = orders_products.merge(sellers, on='seller_id')
orders_products = orders_products.merge(customers, on='customer_id')
orders_products = orders_products.merge(translation, on='product_category_name')

orders_products['order_purchase_timestamp'] = pd.to_datetime(orders_products['order_purchase_timestamp']).dt.date

orders_products = orders_products[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp',
                                   'product_id', 'seller_id', 'product_category_name', 'seller_zip_code_prefix',
                                   'seller_city', 'seller_state', 'customer_unique_id',
                                   'customer_zip_code_prefix', 'customer_state',
                                   'product_category_name_english']]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Дашборд по бразильскому маркетплейсу", style={
        'fontFamily': 'Montserrat, black',
        'fontSize': '50px',
    }),
    html.P("Так, все, что написано ниже - это буквально README, но не в гите", style={
        'fontFamily': 'Helvetica, light',
        'fontSize': '10px'
    }),

    html.P("Ниже даны три фильтра и кнопка их возвращающая в исходное положение (заполненными): по штатам, по статусу, по промежутку дат. Нажать эту кнопку, чтобы смотреть на карту полноценно", style={
        'fontFamily': 'Helvetica, regular',
        'fontSize': '15px'
    }),
    html.Button("заполнить фильтры", id='button_filters', n_clicks=0, style={
    'fontFamily': 'Helvetica, light',
    'fontSize': '15px',
    }),
    dcc.Dropdown(
        id='any_state_filter',
        options=[{'label': state, 'value': state} for state in orders_products['seller_state'].unique()],
        value=orders_products['seller_state'].unique(),
        multi=True,
        style={
            'fontFamily': 'Helvetica, light',
            'fontSize': '15px',
        },
    ),
    dcc.Dropdown(
        id='any_status_filter',
        options=[{'label': status, 'value': status} for status in orders_products['order_status'].unique()],
        value=orders_products['order_status'].unique(),
        multi=True,
        style={
            'fontFamily': 'Helvetica, light',
            'fontSize': '15px',
        },
    ),
    dcc.DatePickerRange(
        id='date_filter',
        start_date=orders_products['order_purchase_timestamp'].min(),
        end_date=orders_products['order_purchase_timestamp'].max(),
        style={
            'fontFamily': 'Helvetica, light',
            'fontSize': '15px',
        }
    ),
    html.H3("Графики продавцов ", style={
        'fontFamily': 'Montserrat, black',
        'fontSize': '40px',
    }),

    html.P("Я сделал следующее, организовал графики два по два, первые два графика по продавцам. Первый из них скорее для задания 4 - чтобы можно было выбрать несколько штатов. Второй для задания 5 и 6 - он обновляется по карте. Аналогично для графиков покупателей", style={
        'fontFamily': 'Helvetica, regular',
        'fontSize': '16px'
    }),
    dcc.Graph(id='sellers_states_count'),
    dcc.Graph(id='sellers_category_count'),
    html.H3("Графики покупателей", style={
        'fontFamily': 'Montserrat, black',
        'fontSize': '40px',
    }),
    dcc.Graph(id='customers_states_count'),
    dcc.Graph(id='customers_category_count'),
    html.H3("Карта", style={
        'fontFamily': 'Montserrat, black',
        'fontSize': '40px',
    }),
    dcc.Dropdown(
        id='type_filter',
        options=[
            {'label': 'sellers', 'value': 'seller'},
            {'label': 'buyers', 'value': 'buyer'}
        ],
        style={
            'fontFamily': 'Helvetica, light',
            'fontSize': '15px',
        },
        value='seller'
    ),
    html.Button('Дрыц-тыц, обнулятор карты, дрыц-тыц, обнулятор карты', id='button_map', n_clicks=0, style={
    'fontFamily': 'Helvetica, light',
    'fontSize': '15px',
}),
    dcc.Graph(id='map_states_count'),
])


@app.callback(
    Output('button_filters', 'n_clicks'),
    Output('sellers_states_count', 'figure'),
    Output('sellers_category_count', 'figure'),
    Output('customers_states_count', 'figure'),
    Output('customers_category_count', 'figure'),
    Output('map_states_count', 'figure'),
    Output('button_map', 'n_clicks'),
    [Input('button_filters', 'n_clicks'),
     Input('any_state_filter', 'value'),
     Input('any_status_filter', 'value'),
     Input('date_filter', 'start_date'),
     Input('date_filter', 'end_date'),
     Input('type_filter', 'value'),
     Input('map_states_count', 'clickData'),
     Input('button_map', 'n_clicks')
     ]
)
def update_sales_chart(n_clicks_filters, selected_states, selected_statuses, start_date, end_date, selected_type, click_data, n_clicks):
    # На разных этапах здесь были ошибки, так что я просто оставил это
    start_date = pd.to_datetime(start_date).date() if start_date else None
    end_date = pd.to_datetime(end_date).date() if end_date else None
    selected_statuses = [selected_statuses] if isinstance(selected_statuses, str) else selected_statuses
    selected_states = [selected_states] if isinstance(selected_states, str) else selected_states

    if n_clicks_filters>=1:
        n_clicks_filters=0
        start_date=orders_products['order_purchase_timestamp'].min()
        start_date = pd.to_datetime(start_date).date() if start_date else None

        end_date=orders_products['order_purchase_timestamp'].max()
        end_date = pd.to_datetime(end_date).date() if end_date else None

        selected_statuses=orders_products['order_status'].unique()
        selected_statuses = [selected_statuses] if isinstance(selected_statuses, str) else selected_statuses

        selected_states=orders_products['seller_state'].unique()
        selected_states = [selected_states] if isinstance(selected_states, str) else selected_states

    seller_filtered_data = orders_products[orders_products['seller_state'].isin(selected_states) &
                                           orders_products['order_status'].isin(selected_statuses) &
                                           (orders_products['order_purchase_timestamp'] >= start_date) &
                                           (orders_products['order_purchase_timestamp'] <= end_date)]
    seller_summary_states = seller_filtered_data.groupby(['seller_state', "product_category_name_english"])[
        'order_id'].count().reset_index().rename(columns={"order_id": "count"})
    seller_summary_categories = seller_filtered_data.groupby(["product_category_name_english"])[
        'order_id'].count().reset_index().rename(columns={"order_id": "count"})
    sellers_category_count_fig = px.bar(seller_summary_categories, x='product_category_name_english', y='count',
                                        color="product_category_name_english", title='sellers_category_count',
                                        hover_data={
                                            'count': True,
                                            'product_category_name_english': False
                                        }
                                        )
    sellers_category_count_fig.update_traces(
        hovertemplate='%{y}' # дальше так же будет - топ тема,
        # убирает название колонок и при этом при наведении показываем каунт - то что передали в hover dara
    )
    sellers_category_count_fig.update_xaxes(tickfont=dict(size=5)) #большие они некрасивые, при этом если хочется рассмотреть -
    # можно просто навести курсор на столбец

    selected_states = [selected_states] if isinstance(selected_states, str) else selected_states
    customer_filtered_data = orders_products[orders_products['customer_state'].isin(selected_states) &
                                             orders_products['order_status'].isin(selected_statuses) &
                                             (orders_products['order_purchase_timestamp'] >= start_date) &
                                             (orders_products['order_purchase_timestamp'] <= end_date)]

    customer_summary_states = customer_filtered_data.groupby(['customer_state', "product_category_name_english"])[
        'order_id'].count().reset_index().rename(columns={"order_id": "count"})
    customer_summary_categories = customer_filtered_data.groupby(["product_category_name_english"])[
        'order_id'].count().reset_index().rename(
        columns={"order_id": "count"})
    customers_category_count_fig = px.bar(customer_summary_categories, x='product_category_name_english', y='count',
                                          color="product_category_name_english",
                                          title='customers_category_count',
                                          hover_data={
                                              'count': True,
                                              'product_category_name_english': False
                                          })
    customers_category_count_fig.update_traces(
        hovertemplate='%{y}'
    )
    customers_category_count_fig.update_xaxes(tickfont=dict(size=5))

    sellers_states_count_fig = px.bar(seller_summary_states, x='seller_state', y='count',
                                      color="product_category_name_english", title='sellers_states_count',
                                      hover_data={
                                          'seller_state': False,
                                          'count': True,
                                          'product_category_name_english': True
                                      }
                                      )
    sellers_states_count_fig.update_traces(
        hovertemplate='%{y}'
    )

    customers_states_count_fig = px.bar(customer_summary_states, x='customer_state', y='count',
                                        color="product_category_name_english",
                                        title='customers_states_count', hover_data={
            'customer_state': False,
            'count': True,
            'product_category_name_english': True
        })
    customers_states_count_fig.update_traces(
        hovertemplate='%{y}'
    )
    # Идейно работает примерно так: сначала выбираем или продавцов или покупателей
    # и потом уже выбираем был ли клик или может нужно его обнулить через кнопку
    if selected_type == 'seller':
        summary = seller_filtered_data.groupby(['seller_state'])['seller_id'].nunique().reset_index().rename(
            columns={"seller_id": "count"})
        map_title = 'number_of_sellers'
        summary.columns = ['id', 'count']

        all_states = pd.DataFrame([feature['id'] for feature in brazil['features']], columns=['id'])
        state_counts = all_states.merge(summary, on='id', how='left')
        state_counts['count'] = state_counts['count'].fillna(0)

        state_counts['sqrt_count'] = np.sqrt(np.sqrt(state_counts['count'])) # вот это был challenge -
        # я то хотел юзать понятно np.log2, но он ругался на 0 - пришлось юзать квадрат по степени 4 - я проверил, они похожи
        state_counts['sqrt_count'] = state_counts['sqrt_count'].fillna(0)

        if n_clicks >= 1: #нажатия на кнопку
            selected_states = [selected_states] if isinstance(selected_states, str) else selected_states
            seller_filtered_data = orders_products[orders_products['seller_state'].isin(selected_states) &
                                                   orders_products['order_status'].isin(selected_statuses) &
                                                   (orders_products['order_purchase_timestamp'] >= start_date) &
                                                   (orders_products['order_purchase_timestamp'] <= end_date)]
            seller_summary_categories = seller_filtered_data.groupby(["product_category_name_english"])[
                'order_id'].count().reset_index().rename(columns={"order_id": "count"})
            sellers_category_count_fig = px.bar(seller_summary_categories, x='product_category_name_english', y='count',
                                                color="product_category_name_english", title='sellers_category_count',
                                                hover_data={
                                                    'count': True,
                                                    'product_category_name_english': False
                                                }
                                                )
            sellers_category_count_fig.update_traces(
                hovertemplate='%{y}'
            )
            sellers_category_count_fig.update_xaxes(tickfont=dict(size=5))
            fig_map = px.choropleth(
                state_counts,
                geojson=brazil,
                locations='id',
                color='sqrt_count',
                color_continuous_scale='Reds',
                hover_name='id',
                hover_data={'id': False, 'count': True, 'sqrt_count': False},
                title=map_title
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title='sqrt4_count',
                    tickvals=state_counts['count'],
                )
            )
            n_clicks = 0

        elif click_data != None:
            state_click = click_data['points'][0]['location']
            state_counts = state_counts[state_counts["id"] == state_click]
            selected_states = [state_click] if isinstance(state_click, str) else state_click
            seller_filtered_data = orders_products[orders_products['seller_state'].isin(selected_states) &
                                                   orders_products['order_status'].isin(selected_statuses) &
                                                   (orders_products['order_purchase_timestamp'] >= start_date) &
                                                   (orders_products['order_purchase_timestamp'] <= end_date)]
            seller_summary_categories = seller_filtered_data.groupby(["product_category_name_english"])[
                'order_id'].count().reset_index().rename(columns={"order_id": "count"})
            sellers_category_count_fig = px.bar(seller_summary_categories, x='product_category_name_english', y='count',
                                                color="product_category_name_english", title='sellers_category_count',
                                                hover_data={
                                                    'count': True,
                                                    'product_category_name_english': False
                                                }
                                                )
            sellers_category_count_fig.update_traces(
                hovertemplate='%{y}'
            )
            sellers_category_count_fig.update_xaxes(tickfont=dict(size=5))

            fig_map = px.choropleth(
                state_counts,
                geojson=brazil,
                locations='id',
                color='sqrt_count',
                color_continuous_scale='Reds',
                hover_name='id',
                hover_data={'id': False, 'count': True, 'sqrt_count': False},
                title=map_title
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title='sqrt4_count',
                    tickvals=state_counts['count'],
                )
            )
        else:  #для старта программы
            n_clicks = 0
            fig_map = px.choropleth(
                state_counts,
                geojson=brazil,
                locations='id',
                color='sqrt_count',
                color_continuous_scale='Reds',
                hover_name='id',
                hover_data={'id': False, 'count': True, 'sqrt_count': False},
                title=map_title
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title='sqrt4_count',
                    tickvals=state_counts['count'],
                )
            )

    else: #покупатели
        summary = customer_filtered_data.groupby(['customer_state'])['customer_id'].nunique().reset_index().rename(
            columns={"customer_id": "count"})
        map_title = 'number_of_customers'
        summary.columns = ['id', 'count']

        all_states = pd.DataFrame([feature['id'] for feature in brazil['features']], columns=['id'])
        state_counts = all_states.merge(summary, on='id', how='left')
        state_counts['count'] = state_counts['count'].fillna(0)

        state_counts['sqrt_count'] = np.sqrt(np.sqrt(state_counts['count']))
        state_counts['sqrt_count'] = state_counts['sqrt_count'].fillna(0)

        if n_clicks >= 1:
            selected_states = [selected_states] if isinstance(selected_states, str) else selected_states
            customer_filtered_data = orders_products[orders_products['customer_state'].isin(selected_states) &
                                                     orders_products['order_status'].isin(selected_statuses) &
                                                     (orders_products['order_purchase_timestamp'] >= start_date) &
                                                     (orders_products['order_purchase_timestamp'] <= end_date)]

            customer_filtered_data.groupby(['customer_state', "product_category_name_english"])[
                    'order_id'].count().reset_index().rename(columns={"order_id": "count"})
            customer_summary_categories = customer_filtered_data.groupby(["product_category_name_english"])[
                'order_id'].count().reset_index().rename(
                columns={"order_id": "count"})
            customers_category_count_fig = px.bar(customer_summary_categories, x='product_category_name_english',
                                                  y='count',
                                                  color="product_category_name_english",
                                                  title='customers_category_count',
                                                  hover_data={
                                                      'count': True,
                                                      'product_category_name_english': False
                                                  }
                                                  )
            customers_category_count_fig.update_traces(
                hovertemplate='%{y}'
            )
            customers_category_count_fig.update_xaxes(tickfont=dict(size=5))
            fig_map = px.choropleth(
                state_counts,
                geojson=brazil,
                locations='id',
                color='sqrt_count',
                color_continuous_scale='Reds',
                hover_name='id',
                hover_data={'id': False, 'count': True, 'sqrt_count': False},
                title=map_title
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title='sqrt4_count',
                    tickvals=state_counts['count'],
                )
            )
            n_clicks = 0


        elif click_data != None:
            state_click = click_data['points'][0]['location']
            state_counts = state_counts[state_counts["id"] == state_click]
            selected_states = [state_click] if isinstance(state_click, str) else state_click
            customer_filtered_data = orders_products[orders_products['customer_state'].isin(selected_states)&
                                                     orders_products['order_status'].isin(selected_statuses) &
                                                     (orders_products['order_purchase_timestamp'] >= start_date) &
                                                     (orders_products['order_purchase_timestamp'] <= end_date)]
            customer_summary_categories = customer_filtered_data.groupby(["product_category_name_english"])[
                'order_id'].count().reset_index().rename(
                columns={"order_id": "count"})
            customers_category_count_fig = px.bar(customer_summary_categories, x='product_category_name_english',
                                                  y='count',
                                                  color="product_category_name_english",
                                                  title='customers_category_count',
                                                  hover_data={
                                                      'count': True,
                                                      'product_category_name_english': False
                                                  }
                                                  )
            customers_category_count_fig.update_traces(
                hovertemplate='%{y}'
            )
            customers_category_count_fig.update_xaxes(tickfont=dict(size=5))
            fig_map = px.choropleth(
                state_counts,
                geojson=brazil,
                locations='id',
                color='sqrt_count',
                color_continuous_scale='Reds',
                hover_name='id',
                hover_data={'id': False, 'count': True, 'sqrt_count': False},
                title=map_title
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title='sqrt4_count',
                    tickvals=state_counts['count'],
                )
            )
        else:
            n_clicks = 0
            fig_map = px.choropleth(
                state_counts,
                geojson=brazil,
                locations='id',
                color='sqrt_count',
                color_continuous_scale='Reds',
                hover_name='id',
                hover_data={'id': False, 'count': True, 'sqrt_count': False},
                title=map_title
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title='sqrt4_count',
                    tickvals=state_counts['count'],
                )
            )

    return n_clicks_filters, sellers_states_count_fig, sellers_category_count_fig, customers_states_count_fig, customers_category_count_fig, fig_map, n_clicks

#крч код жутко плохой из-за шестого задания, я не знал как быстро сделать его не ифая
# и не переписывая код для других график, сделал как было быстрее - понятно, что можно оптимизировать
if __name__ == '__main__':
    app.run_server(debug=True)
