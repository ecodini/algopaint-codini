import const

class Picture:
    def __init__(self, size_x, size_y, pixel_data):
        self.size_x = size_x
        self.size_y = size_y
        self.pixel_data = pixel_data

    def convert_to_ppm(self):
        string = 'P3\n'
        string += f'{self.size_x} {self.size_y}\n255\n'

        for pixel in self.pixel_data:
            color = rgb_to_tuple(pixel)
            string += f'{color[0]} {color[1]} {color[2]} '

        return string

    def palletize_for_png(self):
        unique_colors = set(self.pixel_data)

        color_pallette_array = list(unique_colors)
        pixel_data = []

        for pixel in self.pixel_data:
            pixel_data.append(color_pallette_array.index(pixel))

        formatted_color_pallette = [ rgb_to_tuple(s) for s in color_pallette_array ]

        return formatted_color_pallette, [ pixel_data[i:i+self.size_x] for i in range(0, len(pixel_data), self.size_x) ]
        
def rgb_to_tuple(rgb_as_string):
    values = rgb_as_string.split('#')

    if len(values) != 2:
        return None

    color_values = values[1]

    if len(color_values) != 6:
        return None

    try:
        return tuple([ int(color_values[i:i+2], 16) for i in range(0, 6, 2) ])
    except:
        return None

def tuple_to_rgb(rgb_tuple):
    return f'#{int(rgb_tuple[0]):02x}{int(rgb_tuple[1]):02x}{int(rgb_tuple[2]):02x}'

def generate_empty_picture(width, height):
    dummy_pixel = []

    for i in range(width * height):
        dummy_pixel.append(const.PAINT_COLORS['WHITE'])

    return Picture(width, height, dummy_pixel)
