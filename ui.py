import const
import data
import png
from math import floor
from pila import Pila

class Button:
    def __init__(self, x_pos, y_pos, text, on_click, gamelib, stay_pressed = False):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.on_click = on_click
        self.gamelib = gamelib
        self.selected = False
        self.color = const.DEFAULT_BUTTON_COLOR
        self.stay_pressed = stay_pressed

        self.x_size = len(text) * 6
        self.y_size = 30

    def draw(self):
        outline = const.PAINT_COLORS['BLACK']
        
        if self.selected:
            outline = const.PAINT_COLORS['WHITE']

        self.gamelib.draw_rectangle(self.x_pos, self.y_pos, self.x_pos + 2 * self.x_size, self.y_pos + self.y_size, outline=outline, fill=self.color)
        self.gamelib.draw_text(self.text, self.x_pos + self.x_size, self.y_pos + self.y_size / 2, fill=const.PAINT_COLORS['BLACK'])

    def update(self, mouse_event):
        if mouse_event.type == self.gamelib.EventType.ButtonPress and mouse_event.mouse_button == 1:
            if mouse_event.y - self.y_pos <= self.y_size and mouse_event.y >= self.y_pos and mouse_event.x <= 2 * self.x_size + self.x_pos and self.x_pos <= mouse_event.x:
                if not self.stay_pressed:
                    self.on_click()
                else:
                    self.selected = not self.selected

    def set_default_color(self):
        self.color = const.DEFAULT_BUTTON_COLOR

class ColorSelector:
    def __init__(self, x_pos, y_pos, gamelib, color_array):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.colors = list(color_array.values())
        self.size = const.COLOR_SELECTOR_SIZE
        self.selected_color = 0
        self.gamelib = gamelib
        self.custom_color = None

        self.rgb_button = Button(self.x_pos + len(self.colors) * self.size + self.size / 3, self.y_pos, 'RGB...', self.select_rgb_color, self.gamelib)

    def draw(self):
        for i in range(len(self.colors)):
            outline = const.PAINT_COLORS['BLACK']

            if i == self.selected_color:
                outline = const.PAINT_COLORS['WHITE']

            self.gamelib.draw_rectangle(self.x_pos + i * self.size, self.y_pos, self.x_pos + self.size + i * self.size - 2, self.y_pos + self.size, outline=outline,fill=self.colors[i])

        self.rgb_button.draw()
            
    def update(self, mouse_event):
        self.rgb_button.update(mouse_event)

        if mouse_event.type == self.gamelib.EventType.ButtonPress and mouse_event.mouse_button == 1:
            if mouse_event.y - self.y_pos <= self.size and mouse_event.y >= self.y_pos:
                selected_sq = floor((mouse_event.x - self.x_pos) / self.size)

                if selected_sq < len(self.colors):
                    self.selected_color = selected_sq
                    self.custom_color = None
                    self.rgb_button.selected = False
                    self.rgb_button.set_default_color()

    def get_selected_color(self):
        if self.custom_color:
            return self.custom_color
        else:
            return self.colors[self.selected_color]

    def select_rgb_color(self):
        input = self.gamelib.input('Ingrese un color RGB (en formato #rrggbb):')

        if input is None:
            return

        if data.rgb_to_tuple(input) is None:
            self.gamelib.say('Formato inválido.')
            return

        self.rgb_button.selected = True
        self.selected_color = None
        self.rgb_button.color = input
        self.custom_color = input

class Canvas:
    def __init__(self, picture, x_pos, y_pos, pixel_size, color_selector, gamelib, balde_button):
        self.picture = picture
        self.color_selector = color_selector
        self.gamelib = gamelib

        self.x_pos = x_pos
        self.y_pos = y_pos

        self.pixel_size = pixel_size
        self.mouse_pressed = False

        self.balde_button = balde_button

        self.undo_key_pressed = False
        self.redo_key_pressed = False

        self.events_stack = Pila()
        self.redo_events_stack = Pila()

    def draw(self):
        x = 0
        y = 0
        
        for pixel in self.picture.pixel_data:
            self.gamelib.draw_rectangle(x * self.pixel_size + self.x_pos, y * self.pixel_size + self.y_pos, x * self.pixel_size + self.pixel_size + self.x_pos, y * self.pixel_size + self.pixel_size + self.y_pos, outline=const.PAINT_COLORS['BLACK'],fill=pixel)
            x += 1

            if x == self.picture.size_x:
                x = 0
                y += 1
            elif y == self.picture.size_y:
                break

    def update(self, event):
        if event.type == self.gamelib.EventType.KeyPress:
            if event.keycode == const.UNDO_KEYCODE and not self.undo_key_pressed:
                if not self.events_stack.esta_vacia():
                    event = self.events_stack.desapilar()
                    self.redo_events_stack.apilar(event)

                    self.apply_canvas_event(event, True)

                self.undo_key_pressed = True
            elif event.keycode == const.REDO_KEYCODE and not self.redo_key_pressed:
                if not self.redo_events_stack.esta_vacia():
                    event = self.redo_events_stack.desapilar()
                    self.events_stack.apilar(event)

                    self.apply_canvas_event(event, False)

                self.redo_key_pressed = True

            return
        elif event.type == self.gamelib.EventType.KeyRelease:
            if event.keycode == const.UNDO_KEYCODE and self.undo_key_pressed:
                self.undo_key_pressed = False
            elif event.keycode == const.REDO_KEYCODE and self.redo_key_pressed:
                self.redo_key_pressed = False

            return

        if event.x > self.x_pos and event.y > self.y_pos and event.x < self.x_pos + self.picture.size_x * self.pixel_size and event.y < self.y_pos + self.picture.size_y * self.pixel_size:
            if (event.type == self.gamelib.EventType.ButtonPress or event.type == self.gamelib.EventType.Motion):
                    if event.mouse_button == 1:
                        self.mouse_pressed = not self.mouse_pressed
                    
                    if self.mouse_pressed:
                        x_square = floor((event.x - self.x_pos) / self.pixel_size)
                        y_square = floor((event.y - self.y_pos) / self.pixel_size)

                        pixel_num = x_square + y_square * self.picture.size_x

                        selected_color = self.color_selector.get_selected_color()

                        if self.picture.pixel_data[pixel_num] == selected_color:
                            return

                        if not self.balde_button.selected:
                            og_color = self.picture.pixel_data[pixel_num]

                            self.picture.pixel_data[pixel_num] = selected_color
                            canvas_event = (const.CANVAS_SINGLE_PIXEL_CHANGE, pixel_num, og_color, selected_color)

                            self.events_stack.apilar(canvas_event)

                            self.redo_events_stack = Pila()
                        else:
                            og_pixel_data = list(self.picture.pixel_data)
                            self.recursive_color_change(pixel_num, self.picture.pixel_data[pixel_num], selected_color)
                            new_pixel_data = list(self.picture.pixel_data)

                            canvas_event = (const.CANVAS_BUCKET_FILL, og_pixel_data, new_pixel_data)

                            self.events_stack.apilar(canvas_event)

                            self.redo_events_stack = Pila()

            elif event.mouse_button == 1:
                self.mouse_pressed = False
        elif event.mouse_button == 1:
            self.mouse_pressed = False

    def recursive_color_change(self, pixel_num, old_color, new_color):
        if self.picture.pixel_data[pixel_num] != old_color:
            return

        self.picture.pixel_data[pixel_num] = new_color

        nearby_pixels = []

        if pixel_num != 0 and pixel_num % self.picture.size_x != 0:
            nearby_pixels.append(pixel_num - 1)
        
        if pixel_num < len(self.picture.pixel_data) - 1 and (pixel_num + 1) % self.picture.size_x != 0:
            nearby_pixels.append(pixel_num + 1)

        possible_upper_pixel = pixel_num + self.picture.size_x
        possible_lower_pixel = pixel_num - self.picture.size_x

        if possible_lower_pixel >= 0:
            nearby_pixels.append(possible_lower_pixel)

        if possible_upper_pixel < (self.picture.size_x * self.picture.size_y):
            nearby_pixels.append(possible_upper_pixel)

        for nearby_pixel in nearby_pixels:
            self.recursive_color_change(nearby_pixel, old_color, new_color)

    def apply_canvas_event(self, event, isUndo):
        if event[0] == const.CANVAS_BUCKET_FILL:
            if isUndo:
                self.picture.pixel_data = event[1]
            else: 
                self.picture.pixel_data = event[2]
        elif event[0] == const.CANVAS_SINGLE_PIXEL_CHANGE:
            if isUndo:
                self.picture.pixel_data[event[1]] = event[2]
            else:
                self.picture.pixel_data[event[1]] = event[3]

class Paint:
    def __init__(self, gamelib):
        self.width = const.WIDTH
        self.height = const.HEIGHT

        self.ui_elements = []
        self.gamelib = gamelib

        self.cs = ColorSelector(10, 10, gamelib, const.PAINT_COLORS)
        self.balde_button = Button(10, 90, 'Balde', None, self.gamelib, True)
        self.canvas = Canvas(data.generate_empty_picture(const.DEFAULT_CANVAS_SIZE[0], const.DEFAULT_CANVAS_SIZE[1]), 10, 130, 20, self.cs, self.gamelib, self.balde_button)

        self.ui_elements.append(self.cs)
        self.ui_elements.append(self.canvas)

        self.ui_elements.append(Button(10, 50, 'Guardar PPM', self.save_to_ppm, self.gamelib))
        self.ui_elements.append(Button(150, 50, 'Cargar PPM', self.load_ppm, self.gamelib))
        self.ui_elements.append(Button(280, 50, 'Guardar PNG', self.save_png, self.gamelib))
        self.ui_elements.append(Button(420, 50, 'Nuevo', self.change_size, self.gamelib))

        self.ui_elements.append(self.balde_button)

    def draw(self):
        self.gamelib.draw_rectangle(0, 0, self.width, self.height, fill=const.PAINT_COLORS['GRAY'])

        for ui_element in self.ui_elements:
            ui_element.draw()

        self.gamelib.draw_text('Deshacer: Z, Rehacer: X', 180, 105, fill=const.PAINT_COLORS['BLACK'])

    def update(self, event):
        for ui_element in self.ui_elements:
            ui_element.update(event)

    def save_to_ppm(self):
        ppm_data = self.canvas.picture.convert_to_ppm()

        route = self.gamelib.input('Inserte nombre del archivo (sin el .ppm):')

        if route is None or route == '' or len(route.split('.')) != 1:
            self.gamelib.say('Ruta invalida')
            return

        try:
            with open(route + '.ppm', 'w') as file:
                file.write(ppm_data)
        except:
            self.gamelib.say('Error al guardar el archivo!')

    def load_ppm(self):
        route = self.gamelib.input('Inserte nombre del archivo (sin el .ppm):')

        if route is None or route == '' or len(route.split('.')) != 1:
            self.gamelib.say('Ruta invalida')
            return

        try:
            with open(route + '.ppm', 'r') as file:
                file.readline()
                width, height = file.readline().split()
                file.readline()

                raw_pixel_data = file.read().rstrip('\n').split()

                pixel_data = [ data.tuple_to_rgb(raw_pixel_data[i:i + 3]) for i in range(0, len(raw_pixel_data), 3) ]

                self.canvas.picture = data.Picture(int(width), int(height), pixel_data)

                self.canvas.events_stack = Pila()
                self.canvas.redo_events_stack = Pila()

                self.adjust_window()
        except:
            self.gamelib.say('Error al leer el archivo!')

    def save_png(self):
        pallette, pixel_data = self.canvas.picture.palletize_for_png()

        route = self.gamelib.input('Inserte nombre del archivo (sin el .png):')

        if route is None or route == '' or len(route.split('.')) != 1:
            self.gamelib.say('Ruta invalida')
            return

        try:
            png.escribir(route + '.png', pallette, pixel_data)
        except:
            self.gamelib.say('Error al guardar el archivo!')
    
    def adjust_window(self):
        self.width = self.canvas.pixel_size * self.canvas.picture.size_x + 20

        if self.width < const.WIDTH:
            self.width = const.WIDTH

        self.height = self.canvas.pixel_size * self.canvas.picture.size_y + 140

        if self.height < 100:
            self.height = 100

        self.gamelib.resize(self.width, self.height)

    def change_size(self):
        width = self.gamelib.input('Inserte el ancho:')
        
        try:
            width = int(width)
        except:
            self.gamelib.say('Valor invalido!')
            return

        height = self.gamelib.input('Inserte el alto:')

        try:
            height = int(height)
        except:
            self.gamelib.say('Valor invalido!')
            return

        self.canvas.picture = data.generate_empty_picture(width, height)
        self.canvas.events_stack = Pila()
        self.canvas.redo_events_stack = Pila()
        self.adjust_window()
