# RentSmart — sistema de orçamento de locação

Aplicação de linha de comando em Python para calcular orçamento de apartamentos, casas e estúdios da R.M. Imóveis e gerar a projeção de 12 meses em CSV.

## Requisitos

- Python 3.10 ou superior
- Não usa bibliotecas externas

## Como executar

No terminal, dentro da pasta do projeto:

```bash
python rentsmart.py
```

Responda às perguntas. O programa exibe o orçamento e pergunta o nome do CSV; por padrão, cria `projecao_rentsmart.csv` na pasta atual. O CSV usa ponto e vírgula como separador e codificação UTF-8 com BOM para facilitar a abertura em planilhas.

## Regras implementadas

- Apartamento: base R$ 700,00; segundo quarto +R$ 200,00; garagem +R$ 300,00; 5% de desconto para cliente que informa não possuir crianças, calculado após os adicionais.
- Casa: base R$ 900,00; segundo quarto +R$ 250,00; garagem +R$ 300,00.
- Estúdio: base R$ 1.200,00; quando há estacionamento, o pacote inicial de duas vagas custa R$ 250,00; vagas acima de duas custam R$ 60,00 cada.
- Taxa contratual: R$ 2.000,00, parcelada de 1 a 5 vezes e exibida separadamente do aluguel.

## Projeção

O CSV tem 12 linhas, uma por mês. Cada uma informa aluguel, parcela da taxa contratual e total previsto. A parcela é lançada nos primeiros meses conforme o número escolhido; nos meses restantes, fica zerada. O aluguel mensal permanece igual durante o período projetado.

## Organização orientada a objetos

`Imovel` concentra o cálculo comum; `Apartamento`, `Casa` e `Studio` especializam as regras de cada categoria. `Orcamento` combina o imóvel e as condições contratuais, apresenta o resumo e gera o CSV.

## Exemplo de conferência manual

Apartamento de 2 quartos, com garagem e sem crianças: base R$ 700,00 + R$ 200,00 + R$ 300,00 = subtotal R$ 1.200,00; desconto de 5% = R$ 60,00; aluguel mensal = R$ 1.140,00. Em 5 parcelas, a taxa contratual resulta em R$ 400,00 por parcela. Nos cinco primeiros meses, a previsão é R$ 1.540,00; nos sete seguintes, R$ 1.140,00.

## Observação para a entrega acadêmica

Revise o código, execute-o no seu computador e adapte nomes, explicações e apresentação para refletirem o que você compreendeu e consegue explicar. A atividade também exige publicar o projeto no GitHub e gravar um vídeo pitch de até 4 minutos; esses itens dependem da sua conta e da sua apresentação.
