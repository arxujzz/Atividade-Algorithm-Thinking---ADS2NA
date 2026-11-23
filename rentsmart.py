"""RentSmart - orçamento de locação da R.M. Imóveis.
Execute com: python rentsmart.py
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import csv

CENTAVO = Decimal("0.01")


def dinheiro(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


@dataclass
class Imovel:
    quartos: int = 1
    garagem: bool = False
    vagas_estudio: int = 0
    sem_criancas: bool = False

    @property
    def tipo(self) -> str:
        raise NotImplementedError

    @property
    def aluguel_base(self) -> Decimal:
        raise NotImplementedError

    def adicionais(self) -> list[tuple[str, Decimal]]:
        """Retorna os adicionais mensais aplicáveis."""
        return []

    def desconto(self, subtotal: Decimal) -> Decimal:
        return Decimal("0.00")

    def calcular_aluguel(self) -> tuple[Decimal, Decimal, list[tuple[str, Decimal]]]:
        itens = self.adicionais()
        soma_adicionais = sum((valor for _, valor in itens), Decimal("0.00"))
        subtotal = self.aluguel_base + soma_adicionais
        desconto = dinheiro(self.desconto(subtotal))
        return dinheiro(subtotal - desconto), desconto, itens


class Apartamento(Imovel):
    @property
    def tipo(self) -> str:
        return "Apartamento"

    @property
    def aluguel_base(self) -> Decimal:
        return Decimal("700.00")

    def adicionais(self) -> list[tuple[str, Decimal]]:
        itens = []
        if self.quartos == 2:
            itens.append(("Adicional por 2 quartos", Decimal("200.00")))
        if self.garagem:
            itens.append(("Vaga de garagem", Decimal("300.00")))
        return itens

    def desconto(self, subtotal: Decimal) -> Decimal:
        return subtotal * Decimal("0.05") if self.sem_criancas else Decimal("0.00")


class Casa(Imovel):
    @property
    def tipo(self) -> str:
        return "Casa"

    @property
    def aluguel_base(self) -> Decimal:
        return Decimal("900.00")

    def adicionais(self) -> list[tuple[str, Decimal]]:
        itens = []
        if self.quartos == 2:
            itens.append(("Adicional por 2 quartos", Decimal("250.00")))
        if self.garagem:
            itens.append(("Vaga de garagem", Decimal("300.00")))
        return itens


class Studio(Imovel):
    @property
    def tipo(self) -> str:
        return "Estúdio"

    @property
    def aluguel_base(self) -> Decimal:
        return Decimal("1200.00")

    def adicionais(self) -> list[tuple[str, Decimal]]:
        if self.vagas_estudio == 0:
            return []
        itens = [("Pacote inicial de 2 vagas", Decimal("250.00"))]
        extras = max(0, self.vagas_estudio - 2)
        if extras:
            itens.append((f"{extras} vaga(s) adicional(is)", Decimal("60.00") * extras))
        return itens


@dataclass
class Orcamento:
    imovel: Imovel
    parcelas_contrato: int
    taxa_contrato: Decimal = Decimal("2000.00")

    def __post_init__(self):
        if not 1 <= self.parcelas_contrato <= 5:
            raise ValueError("A taxa contratual deve ser parcelada de 1 a 5 vezes.")

    @property
    def aluguel_mensal(self) -> Decimal:
        return self.imovel.calcular_aluguel()[0]

    @property
    def valor_parcela_contrato(self) -> Decimal:
        return dinheiro(self.taxa_contrato / self.parcelas_contrato)

    def resumo(self) -> str:
        aluguel, desconto, itens = self.imovel.calcular_aluguel()
        linhas = ["\n===== ORÇAMENTO RENTSMART =====", f"Imóvel: {self.imovel.tipo}",
                  f"Aluguel-base: R$ {self.imovel.aluguel_base:.2f}"]
        linhas.extend(f"{nome}: + R$ {valor:.2f}" for nome, valor in itens)
        if desconto:
            linhas.append(f"Desconto aplicado: - R$ {desconto:.2f}")
        linhas += [f"Aluguel mensal: R$ {aluguel:.2f}",
                   f"Taxa contratual: R$ {self.taxa_contrato:.2f}",
                   f"Parcelamento: {self.parcelas_contrato} x R$ {self.valor_parcela_contrato:.2f}",
                   "Nos meses com parcela, o total previsto inclui aluguel e parcela contratual.",
                   "==============================="]
        return "\n".join(linhas)

    def gerar_csv(self, caminho: Path) -> None:
        aluguel = self.aluguel_mensal
        parcela = self.valor_parcela_contrato
        with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mes", "Aluguel mensal (R$)", "Parcela taxa contratual (R$)", "Total previsto (R$)"])
            for mes in range(1, 13):
                taxa_mes = parcela if mes <= self.parcelas_contrato else Decimal("0.00")
                escritor.writerow([mes, f"{aluguel:.2f}", f"{taxa_mes:.2f}", f"{aluguel + taxa_mes:.2f}"])


def perguntar_opcao(pergunta: str, opcoes: set[str]) -> str:
    while True:
        valor = input(pergunta).strip().lower()
        if valor in opcoes:
            return valor
        print("Opção inválida. Tente novamente.")


def perguntar_sim_nao(pergunta: str) -> bool:
    return perguntar_opcao(pergunta + " (s/n): ", {"s", "n"}) == "s"


def perguntar_inteiro(pergunta: str, minimo: int, maximo: int) -> int:
    while True:
        try:
            valor = int(input(pergunta))
            if minimo <= valor <= maximo:
                return valor
        except ValueError:
            pass
        print(f"Informe um número inteiro entre {minimo} e {maximo}.")


def coletar_imovel() -> Imovel:
    tipo = perguntar_opcao("Tipo de imóvel (1-apartamento, 2-casa, 3-estúdio): ", {"1", "2", "3"})
    if tipo == "3":
        vagas = perguntar_inteiro("Número de vagas do estúdio (0 a 10): ", 0, 10)
        return Studio(vagas_estudio=vagas)
    quartos = perguntar_inteiro("Número de quartos (1 ou 2): ", 1, 2)
    garagem = perguntar_sim_nao("Deseja vaga de garagem?" )
    if tipo == "1":
        sem_criancas = perguntar_sim_nao("O cliente informou não possuir crianças?")
        return Apartamento(quartos=quartos, garagem=garagem, sem_criancas=sem_criancas)
    return Casa(quartos=quartos, garagem=garagem)


def main() -> None:
    print("RentSmart | Orçamento de locação - R.M. Imóveis")
    imovel = coletar_imovel()
    parcelas = perguntar_inteiro("Em quantas parcelas deseja pagar a taxa (1 a 5)? ", 1, 5)
    orcamento = Orcamento(imovel, parcelas)
    print(orcamento.resumo())
    nome = input("Nome do arquivo CSV [projecao_rentsmart.csv]: ").strip() or "projecao_rentsmart.csv"
    destino = Path(nome)
    if destino.suffix.lower() != ".csv":
        destino = destino.with_suffix(".csv")
    orcamento.gerar_csv(destino)
    print(f"Projeção salva em: {destino.resolve()}")


if __name__ == "__main__":
    main()
