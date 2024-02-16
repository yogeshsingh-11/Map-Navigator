import os

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from tqdm import tqdm

from Entities import Query, Navigator, Result

INPUT_ROOT = './input'
OUTPUT_PATH = './output'
NEED_GENERATE_MAP = True
PLOT_ALL_NODES = True


class FileSelectionPopup(Popup):
    def __init__(self, callback, path, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.file_chooser = FileChooserListView()
        self.file_chooser.path = path
        self.file_chooser.bind(on_submit=self.callback)
        self.file_chooser.bind(on_cancel=self.dismiss)
        self.content = self.file_chooser


class NavigatorApplication(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.navigator = None
        self.queries = None
        self.map_button = None
        self.queries_button = None
        self.queries_table = None
        self.execute_all_button = None
        self.result_summary = None
        self.image_box = None

    def build(self):
        Window.fullscreen = 'auto'
        self._set_up_output_path()

        layout = BoxLayout(orientation='vertical')

        top_bar = self._build_top_bar()
        layout.add_widget(top_bar)

        table = self._build_table()
        layout.add_widget(table)

        image_box = self._build_image()
        layout.add_widget(image_box)

        summary = self._build_summary()
        layout.add_widget(summary)

        bottom_bar = self._build_bottom_bar()
        layout.add_widget(bottom_bar)

        return layout

    def _set_up_output_path(self):
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
        else:
            self._clear_output_directory(OUTPUT_PATH)

    def _clear_output_directory(self, path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)

            if os.path.isfile(item_path):
                os.remove(item_path)

            elif os.path.isdir(item_path):
                self._clear_output_directory(item_path)
                os.rmdir(item_path)

    def _build_top_bar(self):
        # BoxLayout to contain buttons and labels
        box_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))

        # Button 1
        map_label = Label(text='Map:', size_hint=(0.1, 1))
        box_layout.add_widget(map_label)
        self.map_button = Button(text='Select Map File', size_hint=(0.4, 1), background_color=(0, 1, 0, 1))
        self.map_button.bind(
            on_press=lambda button, *_: self._open_file_chooser(button, 'Select Map File', INPUT_ROOT,
                                                                self._on_map_selected))
        box_layout.add_widget(self.map_button)

        # Button 2
        queries_label = Label(text='Query:', size_hint=(0.1, 1))
        box_layout.add_widget(queries_label)
        self.queries_button = Button(text='Select Query File', size_hint=(0.4, 1), disabled=True,
                                     background_color=(0, 1, 0, 1))
        self.queries_button.bind(on_press=lambda button, *_: self._open_file_chooser(button, 'Select Query File',
                                                                                     INPUT_ROOT,
                                                                                     self._on_queries_selected))
        box_layout.add_widget(self.queries_button)

        return box_layout

    def _build_table(self):
        # Scrollable table below the Navigate button
        self.queries_table = GridLayout(cols=5, size_hint=(1, None), row_default_height=40)
        self.queries_table.bind(minimum_height=self.queries_table.setter('height'))
        table_scroll = ScrollView(size_hint=(1, 0.3), do_scroll_x=True, do_scroll_y=True)
        table_scroll.add_widget(self.queries_table)
        self._build_table_header()
        return table_scroll

    def _build_table_header(self):
        self.queries_table.add_widget(Label(text='#'))
        self.queries_table.add_widget(Label(text='Source (x,y)'))
        self.queries_table.add_widget(Label(text='Destination (x,y)'))
        self.queries_table.add_widget(Label(text='R (km)'))
        self.execute_all_button = Button(text='Execute All', size_hint=(None, None), size=(100, 40),
                                         background_color=(0, 0, 1, 1))
        self.execute_all_button.bind(on_press=lambda button, *_: self._on_execute_all())
        self.execute_all_button.disabled = True
        self.queries_table.add_widget(self.execute_all_button)

    def _build_image(self):
        self.image_box = BoxLayout(size_hint=(1, 0.6))
        return self.image_box

    def _build_summary(self):
        # Scrollable Label to display multi-line text below the image
        scroll_view = ScrollView(size_hint=(1, 0.2))
        self.result_summary = Label(text='', size_hint=(1, 1), halign='left', valign='middle', size_hint_y=None,
                                    text_size=(Window.width, None))
        self.result_summary.bind(texture_size=lambda instance, size: setattr(self.result_summary, 'height', size[1]))
        scroll_view.add_widget(self.result_summary)
        return scroll_view

    def _build_bottom_bar(self):
        box_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
        reset_button = Button(text='Reset', size_hint=(0.5, 1), background_color=(0, 0, 1, 1))
        reset_button.bind(on_press=lambda button, *_: self._on_reset())
        box_layout.add_widget(reset_button)

        exit_button = Button(text='Exit', size_hint=(0.5, 1), background_color=(1, 0, 0, 1))
        exit_button.bind(on_press=lambda button, *_: self._on_exit())
        box_layout.add_widget(exit_button)

        return box_layout

    def _on_map_selected(self, map_path):
        self.map_button.text = self._get_file_name(map_path)
        self.map_button.disabled = True
        self.navigator = Navigator(map_path)
        self.queries_button.disabled = False

    def _on_queries_selected(self, path):
        self.queries = Query.read_queries(path)
        self.execute_all_button.disabled = len(self.queries) == 0
        self.queries_button.text = self._get_file_name(path)
        self.queries_button.disabled = True
        self._bind_table(self.queries)

    def _on_query_picked(self, query):
        result = self.navigator.navigate(query, NEED_GENERATE_MAP, OUTPUT_PATH, PLOT_ALL_NODES)
        self.image_box.clear_widgets()
        self.image_box.add_widget(Image(source=f'{OUTPUT_PATH}/{result.query.file_name}'))
        self.result_summary.text = str(result)

    def _on_execute_all(self):
        solved_queries = 0
        count = len(self.queries)
        for query in tqdm(self.queries):
            result = self.navigator.navigate(query, NEED_GENERATE_MAP, OUTPUT_PATH, PLOT_ALL_NODES)
            if result.reason == Result.REASON_SUCCESS:
                solved_queries += 1
            print(result)
            print(f'\nSolved Queries= {solved_queries} of {count}')
            print('\n==========================================================================\n')
            with open(f'{OUTPUT_PATH}/results.txt', 'a') as file:
                file.write(str(result))
                file.write(f'\nSolved Queries= {solved_queries} of {count}')
                file.write('\n============================================================================\n')

    def _on_reset(self):
        self.navigator = None
        self.queries = None
        self.map_button.text = 'Select Map File'
        self.map_button.disabled = False

        self.queries_button.text = 'Select Query File'
        self.queries_button.disabled = True

        self.queries_table.clear_widgets()
        self._build_table_header()

        self.image_box.clear_widgets()
        self.result_summary.text = ''

        self._clear_output_directory(OUTPUT_PATH)

    def _on_exit(self):
        exit()

    def _bind_table(self, queries):
        for i, query in enumerate(queries):
            self.queries_table.add_widget(Label(text=f'{i + 1}'))
            self.queries_table.add_widget(Label(text=f'({query.src_x} , {query.src_y})'))
            self.queries_table.add_widget(Label(text=f'({query.dst_x} , {query.dst_y})'))
            self.queries_table.add_widget(Label(text=f'{query.r}'))
            row_button = Button(text='Navigate', size_hint=(None, None), size=(100, 40), background_color=(0, 1, 0, 1))
            row_button.query = query
            row_button.bind(on_press=lambda button, *_: self._on_query_picked(button.query))
            self.queries_table.add_widget(row_button)

    # Function to open file chooser and set the selected file path
    def _open_file_chooser(self, button, title, path, callback):
        def on_file_chosen(instance, *_):
            file_path = instance.selection and instance.selection[0]
            if file_path:
                button.text = "Selected"
                callback(file_path)
            popup.dismiss()

        popup = FileSelectionPopup(on_file_chosen, title=title, path=path)
        popup.open()

    @staticmethod
    def _get_file_name(path):
        return os.path.basename(path)
