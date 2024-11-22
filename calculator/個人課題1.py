import flet as ft
import math

# CalcButtonクラス:電卓のボタンの基本クラス
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

# 数字ボタンのクラス
class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE

# 演算子ボタンのクラス
class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE

# 特殊操作ボタンクラス（ACや%など）
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.BLUE_GREY_100
        self.color = ft.colors.BLACK

# 科学計算のボタン（sin, cosなど）
class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.BLUE_ACCENT_200
        self.color = ft.colors.BLACK

# 電卓アプリ全体のクラス
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()   # 電卓の初期化

        # 結果表示のテキスト
        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)
        self.width = 500
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)   # 角丸
        self.padding = 20
        # 電卓のボタンを配置するコンテナ
        self.content = ft.Column(
            controls=[
                # 1行目のボタン
                ft.Row(controls=[self.result], alignment="end"),    # 結果表示
                ft.Row(
                    controls=[
                        ScientificButton(
                            text="sin", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(
                            text="AC", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(
                            text="+/-", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                # 2行目のボタン
                ft.Row(
                    controls=[
                        ScientificButton(
                            text="cos", button_clicked=self.button_clicked
                        ),
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                # 3行目のボタン
                ft.Row(
                    controls=[
                        ScientificButton(
                            text="tan", button_clicked=self.button_clicked
                        ),
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                # 4行目のボタン
                ft.Row(
                    controls=[
                        ScientificButton(
                            text="log", button_clicked=self.button_clicked
                        ),
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                # 5行目のボタン
                ft.Row(
                    controls=[
                        ScientificButton(
                            text="sqrt", button_clicked=self.button_clicked
                        ),
                        DigitButton(
                            text="0", expand=2, button_clicked=self.button_clicked
                        ),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
                
            ]
        )

# ボタンがクリックされたときの処理
    def button_clicked(self, e):
        data = e.control.data   # 押されたボタンのデータを取得
        print(f"Button clicked with data = {data}")
        try:
            if self.result.value == "Error" or data == "AC":
                self.result.value = "0"
                self.reset()

            elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
                # 数字ボタンが押されたときの処理
                if self.result.value == "0" or self.new_operand:
                    self.result.value = data
                    self.new_operand = False
                else:
                    self.result.value = self.result.value + data

            elif data in ("+", "-", "*", "/"):
                # 演算子ボタンが押されたときの処理
                self.result.value = self.calculate(
                    self.operand1, float(self.result.value), self.operator
                )
                self.operator = data
                self.operand1 = float(self.result.value)
                self.new_operand = True

            elif data == "=":
                # =ボタンが押されたときの処理
                self.result.value = self.calculate(
                    self.operand1, float(self.result.value), self.operator
                )
                self.reset()

            elif data == "%":
                self.result.value = float(self.result.value) / 100
                self.reset()

            elif data == "+/-":
                self.result.value = str(-float(self.result.value))

            elif data in ("sin", "cos", "tan", "log", "sqrt"):
                value = float(self.result.value)
                if data == "sin":
                    self.result.value = str(math.sin(math.radians(value)))
                elif data == "cos":
                    self.result.value = str(math.cos(math.radians(value)))
                elif data == "tan":
                    self.result.value = str(math.tan(math.radians(value)))
                elif data == "log":
                    if value > 0:
                        self.result.value = str(math.log10(value))
                    else:
                        self.result.value = "Error"
                elif data == "sqrt":
                    if value >= 0:
                        self.result.value = str(math.sqrt(value))
                    else:
                        self.result.value = "Error"

        except Exception:
            self.result.value = "Error"

        self.update()

    # 計算処理
    def calculate(self, operand1, operand2, operator):
        try:
            if operator == "+":
                return operand1 + operand2
            elif operator == "-":
                return operand1 - operand2
            elif operator == "*":
                return operand1 * operand2
            elif operator == "/":
                return operand1 / operand2 if operand2 != 0 else "Error"
        except:
            return "Error"

    # 電卓の初期化
    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Calc App"
    calc = CalculatorApp()
    page.add(calc)


ft.app(target=main)

