import re

class LexerError(Exception):
    pass


class ParserError(Exception):
    pass


class EvalError(Exception):
    pass


#lexer
TOKEN_RE = re.compile(r'''
    \s*(?:
        (?P<NUMBER>\d+(?:\.\d+)?)          #числа
      | (?P<ID>[A-Za-z_][A-Za-z0-9_]*)     #функция (pow)
      | (?P<OP>[+\-*/|(),])                #операторы и скобки
    )
''', re.VERBOSE)


def tokenize(text: str):
    tokens = []
    pos = 0
    length = len(text)

    while pos < length:
        if text[pos].isspace():
            pos += 1
            continue

        m = TOKEN_RE.match(text, pos)
        if not m:
            raise LexerError(
                f'Нераспознанный символ в позиции {pos}: {text[pos]!r}.'
            )

        if m.lastgroup == 'NUMBER':
            tokens.append(('NUMBER', float(m.group('NUMBER'))))
        elif m.lastgroup == 'ID':
            tokens.append(('ID', m.group('ID')))
        else:
            tokens.append(('OP', m.group('OP')))

        pos = m.end()

    tokens.append(('EOF', None))
    return tokens


#парсер (дерево)
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, op_value):
        tok = self.peek()
        if tok[0] == 'OP' and tok[1] == op_value:
            return self.advance()
        raise ParserError(f'Ожидается {op_value!r}.')

    def parse(self):
        node = self.parse_or()
        if self.peek()[0] != 'EOF':
            raise ParserError(f'Лишний символ: {self.peek()[1]!r}.')
        return node

    def parse_or(self):
        node = self.parse_add()
        while self.peek() == ('OP', '|'):
            self.advance()
            node = ('binop', '|', node, self.parse_add())
        return node

    def parse_add(self):
        node = self.parse_mul()
        while self.peek() in (('OP', '+'), ('OP', '-')):
            op = self.advance()[1]
            node = ('binop', op, node, self.parse_mul())
        return node

    def parse_mul(self):
        node = self.parse_unary()
        while self.peek() in (('OP', '*'), ('OP', '/')):
            op = self.advance()[1]
            node = ('binop', op, node, self.parse_unary())
        return node

    def parse_unary(self):
        tok = self.peek()
        if tok == ('OP', '-'):
            self.advance()
            return ('unary', '-', self.parse_unary())
        if tok == ('OP', '+'):
            self.advance()
            return ('unary', '+', self.parse_unary())
        return self.parse_power()

    def parse_power(self):
        base = self.parse_primary()
        if self.peek() == ('OP', '**'):
            self.advance()
            return ('binop', '**', base, self.parse_unary())
        return base

    def parse_primary(self):
        tok = self.peek()

        if tok[0] == 'NUMBER':
            self.advance()
            return ('num', tok[1])

        if tok[0] == 'ID':
            name = tok[1]
            self.advance()
            if name != 'pow':
                raise ParserError(f'Неизвестная функция: {name!r}.')
            self.expect('(')
            arg1 = self.parse_or()
            self.expect(',')
            arg2 = self.parse_or()
            self.expect(')')
            return ('call', name, [arg1, arg2])

        if tok == ('OP', '('):
            self.advance()
            node = self.parse_or()
            self.expect(')')
            return node

        raise ParserError('Некорректный ввод.')


#семантика и калькуляция
def evaluate(node):
    kind = node[0]

    if kind == 'num':
        return node[1]

    if kind == 'unary':
        val = evaluate(node[2])
        return -val if node[1] == '-' else val

    if kind == 'binop':
        op = node[1]
        left = evaluate(node[2])
        right = evaluate(node[3])

        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise EvalError('Деление на ноль!')
            return left / right
        if op == '**':
            try:
                return left ** right
            except (OverflowError, ValueError) as e:
                raise EvalError(f'Ошибка возведения в степень: {e}.')
        if op == '|':
            if not (float(left).is_integer() and float(right).is_integer()):
                raise EvalError('Оператор '|' применим только к целым числам.')
            return int(left) | int(right)

    if kind == 'call':
        name = node[1]
        args = [evaluate(a) for a in node[2]]
        if name == 'pow':
            try:
                return pow(args[0], args[1])
            except (OverflowError, ValueError) as e:
                raise EvalError(f'Ошибка в pow: {e}')

    raise EvalError(f'Неизвестная конструкция: {node}.')


#main
def calculate(expr: str):
    tokens = tokenize(expr)
    tree = Parser(tokens).parse()
    return evaluate(tree)


def format_result(value):
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e16:
        return str(int(value))
    return str(value)


def main():
    print("#для выхода введите 'exit'\n")

    while True:
        try:
            expr = input('Введите выражение: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nПока!')
            break

        if not expr:
            continue
        if expr.lower()=='exit':
            break

        try:
            result = calculate(expr)
            print(f'Результат: {format_result(result)}\n')
        except LexerError as e:
            print(f'[Ошибка лексики] {e} Попробуйте ещё раз\n')
        except ParserError as e:
            print(f'[Ошибка синтаксиса] {e} Проверьте запись\n')
        except EvalError as e:
            print(f'[Ошибка вычисления] {e} Попробуйте ещё раз\n')
        except Exception as e:
            print(f'{e} Попробуйте ещё раз\n')


main()
