import datetime
import json
import string
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from wordcloud import WordCloud as wc
import tweepy

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbar_format="{x:.0f}", cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar_formatter = matplotlib.ticker.StrMethodFormatter(cbar_format)    
    cbar = ax.figure.colorbar(im, ax=ax, format=cbar_formatter, **cbar_kw)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    ax.set_xlabel(cbarlabel, rotation=0, va="baseline")

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

def nube_de_palabras(path, data):
    wordcloud = wc(font_path='C:\Windows\Fonts\consola.ttf',width=1280,height=720,background_color="black",colormap=cmap_del_dia(),min_font_size=14,prefer_horizontal=1,relative_scaling=1).generate_from_frequencies(data)
    wordcloud.recolor(100)
    wordcloud.to_file(path)

def histograma(path, titulo, etiquetas, unidad, data, valfmt="{x:.2f}"):
    y_pos = np.arange(len(etiquetas))

    fig, ax = plt.subplots()
    plt.bar(y_pos, data, align='center', alpha=0.5)
    plt.xticks(y_pos, etiquetas)
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right",
             rotation_mode="anchor")
    plt.ylabel(unidad)
    plt.title(titulo)
    plt.savefig(path)

    # plt.show()

def lollipop(path, colormap, titulo, etiquetas, unidad, data, valfmt="{x:.2f}"):
    # Create a dataframe
    df = pd.DataFrame({'etiquetas':etiquetas, 'valores':data })

    a = df.etiquetas
    b = df.valores

    # Reorder it following the values:
    ordered_df = df.sort_values(by='valores')
    my_range=range(0,len(df.index))
    
    # The vertival plot is made using the hline function
    # I load the seaborn library only to benefit the nice looking feature
    fig, ax = plt.subplots()

    ax.hlines(y=ordered_df.etiquetas, xmin=0, xmax=ordered_df.valores, color='skyblue')
    ax.plot(ordered_df.valores, my_range, "o")

    # Add titles and axis names
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    ax.xaxis.set_major_formatter(valfmt)
    plt.set_cmap(colormap)
    plt.yticks(my_range, ordered_df.etiquetas)
    plt.title(titulo, loc='left')
    plt.xlabel(unidad)
    plt.savefig(path, bbox_inches='tight',dpi=100)

def cmap_del_dia():

    # cmaps = plt.colormaps()
    cmaps = ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
             
    hoy = datetime.datetime.now()
    idx = (hoy.year + hoy.month + hoy.day) % len(cmaps)

    return cmaps[idx]

def color_del_dia():
# ARREGLAR ESTOOOO
    colores = [color for color in matplotlib.colors.get_named_colors_mapping()]
    
    hoy = datetime.datetime.now()
    idx = (hoy.year + hoy.month + hoy.day) % len(colores)

    return colores[idx]

def twittear(texto, path_imagen):
    claves = open("twitter.keys", "r")
    json_claves = json.load(claves)

    consumer_key = json_claves['consumer_key']
    consumer_secret = json_claves['consumer_secret']
    access_token = json_claves['access_token']
    access_token_secret = json_claves['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    api.update_with_media(filename=path_imagen, status=texto)

def twittear_hilo(textos_e_imagenes):
    claves = open("twitter.keys", "r")
    json_claves = json.load(claves)

    consumer_key = json_claves['consumer_key']
    consumer_secret = json_claves['consumer_secret']
    access_token = json_claves['access_token']
    access_token_secret = json_claves['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    id_a_responder = 0
    for texto_e_imagen in textos_e_imagenes:
        # estado = api.update_with_media(filename=path_img, status=texto, in_replay_to_status_id=id_a_responder)
        medias = []
        for path_img in texto_e_imagen['media']:
            media = api.media_upload(path_img)
            i = 1
        estado = api.update_status(status=texto_e_imagen['texto'], in_replay_to_status_id=id_a_responder, media_ids=medias)
        id_a_responder = estado.id

def texto_en_imagenes(texto, font_path, font_tam, anchomax, altomax, nombre_imagen, modo='RGBA', color_texto=(0,0,0,0), color_fondo=(255,255,255,255) ,xy=(5,5)):
    textos_por_imagen = []
    font = ImageFont.truetype(font_path, font_tam)
    
    if font.getsize(texto)[0] <= anchomax:
        textos_por_imagen.append(texto)
    else:
        palabras = texto.split(' ')
        i = 0
        while i < len(palabras):
            texto = ''
            altura = font.getsize(texto + palabras[i])[1]
            while i < len(palabras) and altura <= altomax:
                linea = ''
                while i < len(palabras) and font.getsize(linea + palabras[i] + " ")[0] <= anchomax:
                    if palabras[i] != "\n":
                        linea = linea + palabras[i]+  " "
                        i += 1
                    else:
                        i += 1
                        break
                if not linea:
                    linea = palabras[i]
                    i += 1
                texto = texto + linea + '\n'
                altura += font.getsize(texto)[1] + 2

            textos_por_imagen.append(texto)

    i = 0
    paths = []
    x, y = xy
    for texto in textos_por_imagen:
        img = Image.new(modo, (anchomax, altomax), color_fondo)
        dibujo = ImageDraw.Draw(img)
        dibujo.text((x,y), texto, font=font, fill=color_texto)
        path = nombre_imagen + str(i) + ".png"
        img.save(path)
        paths.append(path)
        i += 1

    return paths

    
# class ImageText(object):
#     def __init__(self, filename_or_size, mode='RGBA', background=(0, 0, 0, 0), encoding='utf8'):
#         if isinstance(filename_or_size, str):
#             self.filename = filename_or_size
#             self.image = Image.open(self.filename)
#             self.initial_image = Image.open(self.filename)
#             self.size = self.image.size
#         elif isinstance(filename_or_size, (list, tuple)):
#             self.size = filename_or_size
#             self.image = Image.new(mode, self.size, color=background)
#             self.initial_image = Image.new(mode, self.size, color=background)
#             self.filename = None
#         self.draw = ImageDraw.Draw(self.image)
#         self.encoding = encoding

#     def reset_image(self):
#         self.image = self.initial_image
#         self.draw = ImageDraw.Draw(self.image)

#     def save(self, filename=None):
#         self.image.save(filename or self.filename)

#     def texto_en_imagenes(self, texto, font, anchomax, altomax):
#         textos_por_imagen = []

#         if font.getsize(texto)[0] <= anchomax:
#             textos_por_imagen.append(texto)
#         else:
#             palabras = texto.split(' ')
#             i = 0
#             texto = ''
#             while i < len(palabras):
#                 while i < len(palabras) and font.getsize(texto + palabras[i])[1] <= altomax:
#                     while i < len(palabras) and font.getsize(texto + palabras[i])[0] <= anchomax:
#                         texto = texto + palabras[i] +  " "
#                         i += 1
#                     if not texto:
#                         texto = palabras[i]
#                     texto = texto + '\n'
#                 textos_por_imagen.append(texto)
#         return textos_por_imagen

#     def text_wrap(self, text, font, max_width):
#         lines = []
#         # If the width of the text is smaller than image width
#         # we don't need to split it, just add it to the lines array
#         # and return
#         if font.getsize(text)[0] <= max_width:
#             lines.append(text) 
#         else:
#             # split the line by spaces to get words
#             words = text.split(' ')  
#             i = 0
#             # append every word to a line while its width is shorter than image width
#             while i < len(words):
#                 line = ''         
#                 while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
#                     line = line + words[i] + " "
#                     i += 1
#                 if not line:
#                     line = words[i]
#                     i += 1
#                 # when the line gets longer than the max width do not append the word, 
#                 # add the line to the lines array
#                 lines.append(line)    
#         return lines

#     def get_image(self):
#         return self.image

#     def get_font_size(self, text, font, max_width=None, max_height=None):
#         if max_width is None and max_height is None:
#             raise ValueError('You need to pass max_width or max_height')
#         font_size = 1
#         text_size = self.get_text_size(font, font_size, text)
#         if (max_width is not None and text_size[0] > max_width) or \
#            (max_height is not None and text_size[1] > max_height):
#             raise ValueError("Text can't be filled in only (%dpx, %dpx)" % text_size)
#         while True:
#             if (max_width is not None and text_size[0] >= max_width) or \
#                (max_height is not None and text_size[1] >= max_height):
#                 return font_size - 1
#             font_size += 1
#             text_size = self.get_text_size(font, font_size, text)

#     def write_text(self, xy, text, font_filename, font_size=11, color=(0, 0, 0), max_width=None, max_height=None, wrap_text=True):

#         x, y = xy
#         if isinstance(text, str):
#             try:
#                 text = text.decode(self.encoding)
#             except Exception as e:
#                 pass

#         if wrap_text and max_width is not None and isinstance(font_size, int):
#             font = ImageFont.truetype(font_filename, font_size)
#             text = self.text_wrap(text, font, max_width) # ERROR ACA: DEVUELVE UNA LISTA; DEBERIA SER UN STRING CON '\n'
#             text = '\n'.join(text)

#         if font_size == 'fill' and (max_width is not None or max_height is not None):
#             font_size = self.get_font_size(text, font_filename, max_width, max_height)

#         text_size = self.get_text_size(font_filename, font_size, text)
#         font = ImageFont.truetype(font_filename, font_size)
#         if x == 'center':
#             x = (self.size[0] - text_size[0]) / 2
#         if y == 'center':
#             y = (self.size[1] - text_size[1]) / 2
#         self.draw.text((x, y), text, font=font, fill=color)
#         return text_size

#     def get_text_size(self, font_filename, font_size, text):
#         font = ImageFont.truetype(font_filename, font_size)
#         return font.getsize(text)

#     def fill_text_box(self, xy, text, box_width, box_height, font_filename, 
#                         start_font_size=1, color=(0,0,0), place='left',
#                         justify_last_line=False):
#         font_size = start_font_size
#         while True:
#             width, height, box_width = self.write_text_box(xy, text, box_width,
#                                         font_filename, font_size, color, place)
            
#             if (width >= box_width) or (height >= box_height):
#                 font_size -= 1
#                 self.reset_image()
#                 self.write_text_box(xy, text, box_width,
#                                     font_filename, font_size, color, place)
#                 break
            
#             font_size += 1
        
#         return (box_width, box_height)

#     def write_text_box(self, xy, text, box_width, font_filename,
#                        font_size=11, color=(0, 0, 0), place='left',
#                        justify_last_line=False):
#         x, y = xy
        
#         lines = []
#         line = []
#         words = text.split()
#         for word in words:
#             new_line = ' '.join(line + [word])
#             size = self.get_text_size(font_filename, font_size, new_line)
#             text_height = size[1]
#             if size[0] <= box_width:
#                 line.append(word)
#             else:
#                 lines.append(line)
#                 line = [word]
#         if line:
#             lines.append(line)
#         lines = [' '.join(line) for line in lines if line]

#         height = y
#         for index, line in enumerate(lines):
#             if place == 'left':
#                 total_size = self.get_text_size(font_filename, font_size, line)
#                 self.write_text((x, height), line, font_filename, font_size,
#                                 color)
#             elif place == 'right':
#                 total_size = self.get_text_size(font_filename, font_size, line)
#                 x_left = x + box_width - total_size[0]
#                 self.write_text((x_left, height), line, font_filename,
#                                 font_size, color)
#             elif place == 'center':
#                 total_size = self.get_text_size(font_filename, font_size, line)
#                 x_left = int(x + ((box_width - total_size[0]) / 2))
#                 self.write_text((x_left, height), line, font_filename,
#                                 font_size, color)
#             elif place == 'justify':
#                 words = line.split()
#                 if (index == len(lines) - 1 and not justify_last_line) or \
#                    len(words) == 1:
#                     self.write_text((x, height), line, font_filename, font_size,
#                                     color)
#                     continue
#                 line_without_spaces = ''.join(words)
#                 total_size = self.get_text_size(font_filename, font_size,
#                                                 line_without_spaces)
#                 space_width = (box_width - total_size[0]) / (len(words) - 1.0)
#                 start_x = x
#                 for word in words[:-1]:
#                     self.write_text((start_x, height), word, font_filename,
#                                     font_size, color)
#                     word_size = self.get_text_size(font_filename, font_size,
#                                                     word)
#                     start_x += word_size[0] + space_width
#                 last_word_size = self.get_text_size(font_filename, font_size,
#                                                     words[-1])
#                 last_word_x = x + box_width - last_word_size[0]
#                 self.write_text((last_word_x, height), words[-1], font_filename,
#                                 font_size, color)
#             height += text_height
#         return (total_size[0], height - y, box_width)