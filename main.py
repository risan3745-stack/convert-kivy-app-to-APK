from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.window import Window
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from tabulate import tabulate

Window.size = (360, 640)  # Tamanho típico de celular


class MistwoodScorer:
    def __init__(self, vila, fichas, jornada, ev_bas, maravilhas, descoberta, expedicao, condec, visitantes, dific, perolas, enfeites, ev_especial, cartas_0, prosp):
        self.vila = vila
        self.fichas = fichas
        self.jornada = jornada
        self.ev_bas = ev_bas
        self.maravilhas = maravilhas
        self.descoberta = descoberta
        self.expedicao = expedicao
        self.condec = condec
        self.visitantes = visitantes
        self.dific = dific
        self.perolas = perolas
        self.enfeites = enfeites
        self.ev_especial = ev_especial
        self.cartas_0 = cartas_0
        self.prosp = prosp

    def get_result(self, d, ev_e, enf, v_0, cartas):
        dificuldade = d * self.dific
        self.Visitantes = sum(sorted(self.visitantes, reverse=True)[:d])
        ev_esp = ev_e * self.ev_especial
        self.Enfeites = enf * self.enfeites
        val_0 = v_0 * self.cartas_0
        cartas_prosp = cartas * self.prosp
        total_base = self.vila + self.fichas + self.jornada + self.ev_bas + self.maravilhas + self.descoberta + self.expedicao + self.condec + self.perolas
        self.Total = dificuldade + self.Visitantes + ev_esp + self.Enfeites + val_0 + cartas_prosp + total_base
        self.Fichas = self.fichas + dificuldade
        self.Eventos = self.ev_bas + ev_esp
        self.Bonus = val_0 + cartas_prosp


class ScoreApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.inputs = {}

        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=10, spacing=10)
        content.bind(minimum_height=content.setter("height"))  # type: ignore

        def add_section(title, fields, labels):
            content.add_widget(Label(text=title, bold=True, size_hint_y=None, height=30))
            grid = GridLayout(cols=2, size_hint_y=None, height=len(fields) * 50)
            for field, label in zip(fields, labels):
                grid.add_widget(Label(text=label))
                ti = TextInput(multiline=False, size_hint_x=None, width=70)
                self.inputs[field] = ti
                grid.add_widget(ti)
            content.add_widget(grid)

        add_section(
            "Valores impressos",
            ["vila", "fichas", "jornada", "ev_bas", "maravilhas", "descoberta", "expedicao", "condec", "visitantes"],
            ["Valores base da vila", "Fichas (exceto ptos dific.)", "Jornada", "Eventos básicos", "Maravilhas", "Descoberta", "Expedição", "Condecorações", "Visitantes (sep. por espaço)"],
        )

        add_section("Em vez do valor impresso (informar a qtd)", ["dific", "perolas", "enfeites", "ev_especial"], ["Pontos de dific.", "Pérolas", "Enfeites", "Eventos especiais"])

        add_section("Pontos bônus (informar a qtd)", ["cartas_0", "prosp"], ["Cartas de valor 0", "Cartas de Prosp., Lendárias ou Newleaf"])

        self.calc_button = Button(text="Calcular pontuação", size_hint_y=None, height=50)
        self.calc_button.bind(on_press=self.calcular)  # type: ignore
        content.add_widget(self.calc_button)

        self.result = Label(text="", size_hint_y=None, height=1)
        content.add_widget(self.result)
        self.grid = GridLayout(cols=2, size_hint_y=None, height=1200)
        content.add_widget(self.grid)

        scroll.add_widget(content)
        self.add_widget(scroll)

    def calcular(self, instance):
        table = []
        try:
            vila = int(self.inputs["vila"].text) if self.inputs["vila"].text else 0
            fichas = int(self.inputs["fichas"].text) if self.inputs["fichas"].text else 0
            jornada = int(self.inputs["jornada"].text) if self.inputs["jornada"].text else 0
            ev_bas = int(self.inputs["ev_bas"].text) if self.inputs["ev_bas"].text else 0
            maravilhas = int(self.inputs["maravilhas"].text) if self.inputs["maravilhas"].text else 0
            descoberta = int(self.inputs["descoberta"].text) if self.inputs["descoberta"].text else 0
            expedicao = int(self.inputs["expedicao"].text) if self.inputs["expedicao"].text else 0
            condec = int(self.inputs["condec"].text) if self.inputs["condec"].text else 0
            visitantes = list(map(int, self.inputs["visitantes"].text.strip().split())) if self.inputs["visitantes"].text else [0]
            dific = int(self.inputs["dific"].text) if self.inputs["dific"].text else 0
            perolas = 2 * int(self.inputs["perolas"].text) if self.inputs["perolas"].text else 0
            enfeites = int(self.inputs["enfeites"].text) if self.inputs["enfeites"].text else 0
            ev_especial = int(self.inputs["ev_especial"].text) if self.inputs["ev_especial"].text else 0
            cartas_0 = int(self.inputs["cartas_0"].text) if self.inputs["cartas_0"].text else 0
            prosp = int(self.inputs["prosp"].text) if self.inputs["prosp"].text else 0

            jogo = MistwoodScorer(vila, fichas, jornada, ev_bas, maravilhas, descoberta, expedicao, condec, visitantes, dific, perolas, enfeites, ev_especial, cartas_0, prosp)

            for n in range(5)[::-1]:
                if n == 0:
                    nome = "Mansa"
                    jogo.get_result(0, 3, 3, 0, 0)

                if n == 1:
                    nome = "Complicada"
                    jogo.get_result(1, 4, 4, 1, 0)

                if n == 2:
                    nome = "Problemática"
                    jogo.get_result(2, 5, 5, 1, 1)

                if n == 3:
                    nome = "Atormentadora"
                    jogo.get_result(3, 6, 6, 1, 2)

                if n == 4:
                    nome = "Aterrorizante"
                    jogo.get_result(4, 6, 7, 2, 3)

                table.append(["-" * 45, "-" * 40])
                table.append([nome + f" ({n})", ""])  # type: ignore
                table.append(["-" * 45, "-" * 40])
                table.append(["Base", str(jogo.vila)])
                table.append(["Bônus", str(jogo.Bonus)])
                table.append(["Eventos", str(jogo.Eventos)])
                table.append(["Jornada", str(jogo.jornada)])
                table.append(["Fichas", str(jogo.Fichas)])
                if jogo.perolas != 0:
                    table.append(["Pérolas", str(jogo.perolas)])
                if jogo.maravilhas != 0:
                    table.append(["Maravilhas", str(jogo.maravilhas)])
                if jogo.Enfeites != 0:
                    table.append(["Enfeites", str(jogo.Enfeites)])
                if jogo.expedicao != 0:
                    table.append(["Expedição", str(jogo.expedicao)])
                if jogo.descoberta != 0:
                    table.append(["Descoberta", str(jogo.descoberta)])
                if jogo.Visitantes != 0:
                    table.append(["Visitantes", str(jogo.Visitantes)])
                if jogo.condec != 0:
                    table.append(["Condecorações", str(jogo.condec)])

                table.append(["Total", str(jogo.Total)])
                table.append(["-" * 45, "-" * 40])

            self.grid.clear_widgets()
            for i in table:
                self.grid.add_widget(Label(text=i[0]))
                self.grid.add_widget(Label(text=i[1]))

        except Exception as e:
            self.result.text = f"Erro: {e}"


class MistwoodApp(App):
    def build(self):
        return ScoreApp()


if __name__ == "__main__":
    MistwoodApp().run()
