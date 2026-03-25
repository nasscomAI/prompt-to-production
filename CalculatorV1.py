"""Pastel-themed Tkinter calculator with modular architecture."""

from __future__ import annotations

import ast
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk


@dataclass(frozen=True)
class Theme:
	"""Centralized visual settings for consistent pastel styling."""

	app_bg: str = "#EAF7F2"
	display_bg: str = "#FFF9EC"
	display_fg: str = "#355C63"
	number_bg: str = "#EADCF8"
	operator_bg: str = "#CFE8FF"
	control_bg: str = "#FFDDE1"
	equals_bg: str = "#D7F5D1"
	button_fg: str = "#23414A"
	active_bg: str = "#F3F6D8"


class SafeEvaluator(ast.NodeVisitor):
	"""Safely evaluates arithmetic AST with supported operations only."""

	_binary_operators = {
		ast.Add: lambda a, b: a + b,
		ast.Sub: lambda a, b: a - b,
		ast.Mult: lambda a, b: a * b,
		ast.Div: lambda a, b: a / b,
	}

	_unary_operators = {
		ast.UAdd: lambda a: +a,
		ast.USub: lambda a: -a,
	}

	def visit_Expression(self, node: ast.Expression) -> float:
		return self.visit(node.body)

	def visit_BinOp(self, node: ast.BinOp) -> float:
		left_value = self.visit(node.left)
		right_value = self.visit(node.right)
		operator_type = type(node.op)

		if operator_type not in self._binary_operators:
			raise ValueError("Unsupported operator")

		operation = self._binary_operators[operator_type]
		return operation(left_value, right_value)

	def visit_UnaryOp(self, node: ast.UnaryOp) -> float:
		operand_value = self.visit(node.operand)
		operator_type = type(node.op)

		if operator_type not in self._unary_operators:
			raise ValueError("Unsupported unary operator")

		operation = self._unary_operators[operator_type]
		return operation(operand_value)

	def visit_Constant(self, node: ast.Constant) -> float:
		if isinstance(node.value, (int, float)):
			return float(node.value)
		raise ValueError("Invalid literal")

	def generic_visit(self, node: ast.AST) -> float:
		raise ValueError(f"Invalid expression node: {type(node).__name__}")


class CalculatorEngine:
	"""Handles expression state and calculation rules independent from UI."""

	def __init__(self) -> None:
		self.expression = ""

	def clear_all(self) -> str:
		self.expression = ""
		return "0"

	def clear_last(self) -> str:
		self.expression = self.expression[:-1]
		return self.expression or "0"

	def append_token(self, token: str) -> str:
		if token.isdigit():
			self.expression += token
			return self.expression

		if token == ".":
			if self._can_add_decimal():
				self.expression += token
			return self.expression or "0"

		if token in "+-*/":
			if not self.expression:
				if token == "-":
					self.expression = token
				return self.expression or "0"

			if self.expression[-1] in "+-*/":
				if token == "-" and self.expression[-1] != "-":
					self.expression += token
				else:
					self.expression = self.expression[:-1] + token
			else:
				self.expression += token

		return self.expression or "0"

	def evaluate_expression(self) -> str:
		if not self.expression:
			return "0"

		if self.expression[-1] in "+-*/":
			return "Error"

		try:
			parsed = ast.parse(self.expression, mode="eval")
			result = SafeEvaluator().visit(parsed)
			if result.is_integer():
				self.expression = str(int(result))
			else:
				self.expression = str(result)
			return self.expression
		except (SyntaxError, ValueError, ZeroDivisionError):
			self.expression = ""
			return "Error"

	def _can_add_decimal(self) -> bool:
		current_segment = self._current_number_segment()
		if "." in current_segment:
			return False
		if not current_segment or current_segment in {"+", "-", "*", "/"}:
			self.expression += "0"
		return True

	def _current_number_segment(self) -> str:
		index = len(self.expression) - 1
		while index >= 0 and self.expression[index] not in "+-*/":
			index -= 1
		return self.expression[index + 1 :]


class CalculatorUI:
	"""Builds and manages Tkinter user interface and interactions."""

	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Pastel Calculator")
		self.root.minsize(300, 420)

		self.theme = Theme()
		self.engine = CalculatorEngine()
		self.display_value = tk.StringVar(value="0")

		self._configure_root()
		self._build_widgets()
		self._bind_keyboard()

	def _configure_root(self) -> None:
		self.root.configure(bg=self.theme.app_bg)
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		style = ttk.Style()
		style.configure("TFrame", background=self.theme.app_bg)

	def _build_widgets(self) -> None:
		container = ttk.Frame(self.root, padding=12)
		container.grid(row=0, column=0, sticky="nsew")
		container.rowconfigure(0, weight=1)
		for row_index in range(1, 6):
			container.rowconfigure(row_index, weight=3)
		for col_index in range(4):
			container.columnconfigure(col_index, weight=1)

		display_label = tk.Label(
			container,
			textvariable=self.display_value,
			font=("Segoe UI", 28, "bold"),
			anchor="e",
			bg=self.theme.display_bg,
			fg=self.theme.display_fg,
			padx=12,
			pady=16,
			relief="flat",
		)
		display_label.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(0, 10))

		buttons = [
			("C", 1, 0, "control"),
			("DEL", 1, 1, "control"),
			("/", 1, 2, "operator"),
			("*", 1, 3, "operator"),
			("7", 2, 0, "number"),
			("8", 2, 1, "number"),
			("9", 2, 2, "number"),
			("-", 2, 3, "operator"),
			("4", 3, 0, "number"),
			("5", 3, 1, "number"),
			("6", 3, 2, "number"),
			("+", 3, 3, "operator"),
			("1", 4, 0, "number"),
			("2", 4, 1, "number"),
			("3", 4, 2, "number"),
			("=", 4, 3, "equals"),
			("0", 5, 0, "number"),
			(".", 5, 1, "number"),
		]

		for text, row, column, role in buttons:
			button = tk.Button(
				container,
				text=text,
				font=("Segoe UI", 16, "bold"),
				bg=self._button_color(role),
				fg=self.theme.button_fg,
				activebackground=self.theme.active_bg,
				activeforeground=self.theme.button_fg,
				relief="flat",
				borderwidth=0,
				command=lambda value=text: self._on_button_click(value),
			)
			button.grid(
				row=row,
				column=column,
				sticky="nsew",
				padx=5,
				pady=5,
				ipadx=4,
				ipady=8,
			)

	def _bind_keyboard(self) -> None:
		self.root.bind("<Key>", self._on_key_press)
		self.root.bind("<Return>", lambda _: self._on_button_click("="))
		self.root.bind("<KP_Enter>", lambda _: self._on_button_click("="))
		self.root.bind("<BackSpace>", lambda _: self._on_button_click("DEL"))
		self.root.bind("<Escape>", lambda _: self._on_button_click("C"))

	def _on_key_press(self, event: tk.Event) -> None:
		if event.char in "0123456789.+-*/":
			self._on_button_click(event.char)

	def _on_button_click(self, token: str) -> None:
		if token == "C":
			self.display_value.set(self.engine.clear_all())
			return

		if token == "DEL":
			self.display_value.set(self.engine.clear_last())
			return

		if token == "=":
			self.display_value.set(self.engine.evaluate_expression())
			return

		self.display_value.set(self.engine.append_token(token))

	def _button_color(self, role: str) -> str:
		if role == "operator":
			return self.theme.operator_bg
		if role == "control":
			return self.theme.control_bg
		if role == "equals":
			return self.theme.equals_bg
		return self.theme.number_bg


def main() -> None:
	"""Application entry point."""
	root = tk.Tk()
	CalculatorUI(root)
	root.mainloop()


if __name__ == "__main__":
	main()
