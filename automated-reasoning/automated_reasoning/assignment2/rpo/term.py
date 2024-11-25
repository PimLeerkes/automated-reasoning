from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class VariableSymbol:
    """Represents a variable with this name."""
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class FunctionApplication:
    """Represents a function application of function with this symbol to a list of terms."""
    symbol: str
    terms: list["Term"]

    def __str__(self) -> str:
        return f"{self.symbol}({",".join([str(x) for x in self.terms])})"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(str(self))

# A term is either a variable or a function application.
Term = Union[VariableSymbol, FunctionApplication]

def get_subterms(term: Term) -> set[Term]:
    """Get all subterms of this term."""
    match term:
        case VariableSymbol(_name):
            return set([term])
        case FunctionApplication(_symbol, subterms):
            s = set([term])
            for subterm in subterms:
                s.add(subterm)
                s.update(get_subterms(subterm))
            return s

def get_function_symbols(trs: list[tuple[Term, Term]]) -> set[str]:
    """Get all function symbols that occurs in trs."""
    symbols = set()
    for rule in trs:
        for term in rule:
            for subterm in get_subterms(term):
                match subterm:
                    case FunctionApplication(symbol, _args):
                        symbols.add(symbol)
    return symbols
