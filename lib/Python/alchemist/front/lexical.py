from dataclasses import dataclass, field
from enum import Flag


@dataclass
class Token:
    type: Flag
    start_position: tuple[int, int, int]
    end_position: tuple[int, int, int]
    value: str
    next: "Token | None" = field(default=None, init=False, repr=False)


@dataclass
class Lexer:
    input: str
    filename: str
    newline: str
    start: Token | None = field(default=None, init=False, repr=False)

    def advance(self, position: tuple[int, int, int], length: int) -> tuple[int, int, int]:
        if position[0] + length <= len(self.input):
            lines = self.input.count(self.newline, position[0], position[0] + length)

            if lines > 0:
                position = (
                    position[0] + length,
                    position[1] + lines,
                    position[0] + length - self.input.rfind(self.newline, position[0], position[0] + length)
                )
            else:
                position = (position[0] + length, position[1], position[2] + length)

        return position

    def next_token(self, token: Token | None) -> Token:
        if token is None:
            if self.start is None:
                self.start = self.tokenize((0, 1, 1))

            return self.start

        if token.next is None:
            token.next = self.tokenize(token.end_position)

        return token.next

    def tokenize(self, position: tuple[int, int, int]) -> Token:
        raise NotImplementedError()
