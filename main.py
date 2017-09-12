# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from collections import OrderedDict
from bokeh.core.properties import field
from bokeh.io import curdoc, output_file, save
from bokeh.layouts import layout, gridplot, column
from bokeh.models import (
    ColumnDataSource, HoverTool, SingleIntervalTicker, Slider, Button, Label,
    CategoricalColorMapper
)
from bokeh.plotting import figure
from bokeh.palettes import Spectral6 as palette  # @UnresolvedImport
from bokeh.sampledata.gapminder import regions

output_file('visualizations.html')


def process_data(df, r1, r2):
    df = df.unstack().unstack()
    df = df[(df.index >= r1) & (df.index <= r2)]
    df = df.unstack().unstack()
    return df


def animate_update():
    year = slider.value + 1
    if year > years[-1]:
        year = years[0]
    slider.value = year


def slider_update(attrname, old, new):
    year = slider.value
    label.text = str(year)
    source.data = data[year]


def animate():
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)


employment_data = pd.read_excel('indicator_t above 15 employ.xlsx', encoding='utf8', index_col=0)
hiv_data = pd.read_excel('indicator hiv estimated prevalence% 15-49.xlsx', encoding='utf8', index_col=0)
life_expectancy_data = pd.read_excel('indicator life_expectancy_at_birth.xlsx', encoding='utf8', index_col=0)
population = pd.read_excel('indicator gapminder population.xlsx', encoding='utf8', index_col=0)
per_capita_data = pd.read_excel('indicator gapminder gdp_per_capita_ppp.xlsx', encoding='utf8', index_col=0)

employment_data = process_data(employment_data, 1991, 2015)
hiv_data = process_data(hiv_data, 1991, 2015)
life_expectancy_data = process_data(life_expectancy_data, 1991, 2015)
population = process_data(population, 1991, 2015)
per_capita_data = process_data(per_capita_data, 1991, 2015)

# have common countries across all data
common_countries = (life_expectancy_data.index.intersection(employment_data.index)).intersection(hiv_data.index)
employment_data = employment_data.loc[common_countries]
population = population.loc[common_countries]
hiv_data = hiv_data.loc[common_countries]
life_expectancy_data = life_expectancy_data.loc[common_countries]
per_capita_data = per_capita_data.loc[common_countries]

# find minimum maximum value of each dataset
min_employment = np.min(employment_data.values.flatten())
max_employment = np.max(employment_data.values.flatten())
min_hiv_data = np.min(hiv_data.values.flatten())
max_hiv_data = np.max(hiv_data.values.flatten())
min_life_expectancy_data = np.min(life_expectancy_data.values.flatten())
max_life_expectancy_data = np.max(life_expectancy_data.values.flatten())
print(min_hiv_data)
print(max_hiv_data)
print(min_life_expectancy_data)
print(max_life_expectancy_data)

# Make the column names ints not strings for handling
columns = list(employment_data.columns)
years = list(range(int(columns[0]), int(columns[-1])))
rename_dict = dict(zip(columns, years))
employment_data = employment_data.rename(columns=rename_dict)
hiv_data = hiv_data.rename(columns=rename_dict)
population = population.rename(columns=rename_dict)
life_expectancy_data = life_expectancy_data.rename(columns=rename_dict)
per_capita_data = per_capita_data.rename(columns=rename_dict)
regions = regions.rename(columns=rename_dict)
regions_list = list(regions.Group.unique())

# Preprocess population data
scale_factor = 200
population = np.sqrt(population / np.pi) / scale_factor
min_size = 3
population = pd.DataFrame(population)
population = population.where(population >= min_size).fillna(min_size)

print(employment_data.head())
print(hiv_data.head())

p = pd.Panel(
    {'employed': employment_data, 'hiv': hiv_data, 'population': population, 'life_expectancy': life_expectancy_data,
     'per_capita': per_capita_data})

data = {}
region_name = regions.Group
region_name.name = 'region'
for year in years:
    df = pd.concat([p.loc[:, :, year], region_name], axis=1)
    data[year] = df.to_dict('series')

TOOLS = "box_select,lasso_select,help"

# plot 1
source = ColumnDataSource(data=data[years[-1]])
p1 = figure(tools=TOOLS, x_range=(1, 100),
            y_range=(1, 100), title='Employed Data', plot_height=300)
p1.xaxis.ticker = SingleIntervalTicker(interval=20)
p1.xaxis.axis_label = "Employed"
p1.yaxis.ticker = SingleIntervalTicker(interval=20)
p1.yaxis.axis_label = "Life expectancy(in years)"
label = Label(x=10, y=30, text=str(years[-1]), text_font_size='70pt', text_color='#eeeeee')
p1.add_layout(label)
color_mapper = CategoricalColorMapper(palette=palette, factors=regions_list)
p1.circle(
    x='employed',
    y='life_expectancy',
    size='population',
    source=source,
    fill_color={'field': 'region', 'transform': color_mapper},
    fill_alpha=0.8,
    line_color='#7c7e71',
    line_width=0.5,
    line_alpha=0.5,
    legend=field('region'),
)
p1.add_tools(HoverTool(tooltips=OrderedDict([('x', '@employed'), ('y', '@life_expectancy'), ('region', '@region')]),
                       show_arrow=False, point_policy='follow_mouse'))

# Plot 2
p2 = figure(tools=TOOLS, x_range=(1, 100), y_range=(0, 100),
            title='Scatter Data', plot_height=300)
p2.xaxis.ticker = SingleIntervalTicker(interval=20)
p2.xaxis.axis_label = "Employed"
p2.yaxis.ticker = SingleIntervalTicker(interval=20)
p2.yaxis.axis_label = "HIV prevalence"
label = Label(x=10, y=30, text=str(years[-1]), text_font_size='70pt', text_color='#eeeeee')
p2.add_layout(label)
color_mapper = CategoricalColorMapper(palette=palette, factors=regions_list)
p2.circle(
    x='employed',
    y='hiv',
    size='population',
    source=source,
    fill_color={'field': 'region', 'transform': color_mapper},
    fill_alpha=0.8,
    line_color='#7c7e71',
    line_width=0.5,
    line_alpha=0.5,
    legend=field('region'),
)
p2.add_tools(HoverTool(tooltips=OrderedDict([('x', '@employed'), ('y', '@hiv'), ('region', '@region')]),
                       show_arrow=False, point_policy='follow_mouse'))

#Plot 3
p3 = figure(tools=TOOLS, x_range=(1, 100), y_range=(1, 5000),
            title='Scatter Data', plot_height=300)
p3.xaxis.ticker = SingleIntervalTicker(interval=20)
p3.xaxis.axis_label = "life_expectancy"
p3.yaxis.ticker = SingleIntervalTicker(interval=100)
p3.yaxis.axis_label = "per_capita"
label = Label(x=10, y=30, text=str(years[-1]), text_font_size='70pt', text_color='#eeeeee')
p3.add_layout(label)
color_mapper = CategoricalColorMapper(palette=palette, factors=regions_list)
p3.circle(
    x='life_expectancy',
    y='per_capita',
    size='population',
    source=source,
    fill_color={'field': 'region', 'transform': color_mapper},
    fill_alpha=0.8,
    line_color='#7c7e71',
    line_width=0.5,
    line_alpha=0.5,
    legend=field('region'),
)
p3.add_tools(HoverTool(tooltips=OrderedDict([('x', '@life_expectancy'), ('y', '@per_capita'), ('region', '@region')]),
                       show_arrow=False, point_policy='follow_mouse'))

slider = Slider(start=years[0], end=years[-1], value=years[-1], step=1, title="Year")
slider.on_change('value', slider_update)

button = Button(label='► Play', width=60)
button.on_click(animate)

layout = layout([
    column([p1, p2, p3], sizing_mode='scale_width'),
    [slider, button],
], sizing_mode='scale_width')

curdoc().add_root(layout)
curdoc().title = "Gapminder Analysis"
save(curdoc())
