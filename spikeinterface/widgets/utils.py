import numpy as np
import random

try:
    import distinctipy
    HAVE_DISTINCTIPY = True
except ImportError:
    HAVE_DISTINCTIPY = False

try:
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False


def get_some_colors(keys, color_engine='auto', map_name='gist_ncar', format='RGBA', shuffle=False):
    """
    Return a dict of colors for given keys
    """
    assert color_engine in ('auto', 'distinctipy', 'matplotlib', 'colorsys')

    possible_formats = ('RGBA',)
    assert format in possible_formats, f'format must be {possible_formats}'

    # select the colormap engine
    if color_engine == 'auto':
        if HAVE_DISTINCTIPY:
            color_engine = 'distinctipy'
        elif HAVE_MPL:
            color_engine = 'matplotlib'
        else:
            color_engine = 'colorsys'

    N = len(keys)

    if color_engine == 'distinctipy':
        colors = distinctipy.get_colors(N)
        # add the alpha
        colors = [color + (1., ) for color in colors]

    elif color_engine == 'matplotlib':
        # some map have black or white at border so +10
        margin = max(4, N // 20) // 2
        cmap = plt.get_cmap(map_name, N + 2 * margin)
        colors = [cmap(i+margin) for i, key in enumerate(keys)]
        if shuffle:
            random.shuffle(colors)

    elif color_engine == 'colorsys':
        import colorsys
        colors = [colorsys.hsv_to_rgb(x * 1.0 / N, 0.5, 0.5) + (1., ) for x in range(N)]

    dict_colors = dict(zip(keys, colors))

    return dict_colors


def get_unit_colors(sorting, color_engine='auto', map_name='gist_ncar', format='RGBA', shuffle=False):
    """
    Return a dict colors per units.
    """
    colors = get_some_colors(sorting.unit_ids, color_engine=color_engine,
                             map_name=map_name, format=format, shuffle=shuffle)
    return colors


def array_to_image(data,
                   colormap='RdGy',
                   clim=None,
                   spatial_zoom=(0.75, 1.25),
                   num_timepoints_per_row=30000,
                   row_spacing=0.25):
    """
    Converts a 2D numpy array (width x height) to a 
    3D image array (width x height x RGB color).

    Useful for visualizing data before/after preprocessing

    Params
    =======
    data : np.array
        2D numpy array
    colormap : str 
        Identifier for a Matplotlib colormap
    clim : tuple or None
        The color limits. If None, the clim is the range of the traces
    spatial_zoom : tuple 
        Tuple specifying width & height scaling
    num_timepoints_per_row : int
        Max number of samples before wrapping
    row_spacing : float
        Ratio of row spacing to overall channel height

    Returns
    ========
    output_image : 3D numpy array

    """

    from scipy.ndimage import zoom
    
    if clim is not None:
        assert len(clim) == 2, "'clim' should have a minimum and maximum value"
    else:
        clim = [np.min(data), np.max(data)]

    num_timepoints = data.shape[0]
    num_channels = data.shape[1]
    num_channels_after_scaling = int(num_channels * spatial_zoom[1])
    spacing = int(num_channels * spatial_zoom[1] * row_spacing)

    num_timepoints_after_scaling = int(num_timepoints * spatial_zoom[0])
    num_timepoints_per_row_after_scaling = int(np.min([num_timepoints_per_row, num_timepoints]) * spatial_zoom[0])

    cmap = plt.get_cmap(colormap)
    zoomed_data = zoom(data, spatial_zoom)
    
    scaled_data = zoomed_data
    scaled_data[scaled_data < clim[0]] = clim[0]
    scaled_data[scaled_data > clim[1]] = clim[1]
    scaled_data = (scaled_data - clim[0]) / np.ptp(clim)
    a = (cmap(scaled_data.T)[:, :, :3]*255).astype(np.uint8)  # colorize and convert to uint8

    num_rows = int(np.ceil(num_timepoints / num_timepoints_per_row))

    output_image = np.ones(
        (num_rows * (num_channels_after_scaling + spacing) - spacing,
         num_timepoints_per_row_after_scaling, 3), dtype=np.uint8
    ) * 255

    for ir in range(num_rows):
        i1 = ir * num_timepoints_per_row_after_scaling
        i2 = min(i1 + num_timepoints_per_row_after_scaling, num_timepoints_after_scaling)
        output_image[ir * (num_channels_after_scaling + spacing):ir * (num_channels_after_scaling + spacing) +
                     num_channels_after_scaling, :i2-i1, :] = a[:, i1:i2, :]

    return output_image
