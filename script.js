// Constantes
const categoria = document.getElementById("categoria");
const valor = document.getElementById("valor");
const salvar = document.getElementById("salvar");
const despesas = document.getElementById("despesas");
const calculo = document.getElementById("calculo");

// Salvar as despesas
salvar.addEventListener("click",
    function()
    {
        const novaDespesa = document.createElement("div");

        novaDespesa.textContent =
            categoria.options[categoria.selectedIndex].text + ": R$ " + valor.value;

        const excluirDespesa = document.createElement("button");

        excluirDespesa.textContent = "Excluir";

        excluirDespesa.addEventListener("click",
            function()
            {
                novaDespesa.remove();
                calcularDespesas();
            }
        );

        novaDespesa.appendChild(excluirDespesa);
        despesas.appendChild(novaDespesa);

        calcularDespesas();
    }
);

// Calcular despesas
function calcularDespesas()
{
    let soma = 0;

    const todasDespesas = despesas.children;

    for (let i = 0; i < todasDespesas.length; i++)
    {
        const texto = todasDespesas[i].textContent;
        const valorDespesa = parseFloat(
            texto.match(/R\$ ([\d.]+)/)[1]
        );

        soma += valorDespesa;
    }

    calculo.textContent = "Calculo das despesas: R$ " + soma.toFixed(2);
}

valor.addEventListener("input",
    function()
    {
        let numero = valor.value;

        numero = numero.replace(/[^\d,.]/g, "");

        let partes = numero.split(",");

        let inteiro = partes[0];
        let decimal = partes[1];

        inteiro = inteiro.replace(/\./g, "");

        inteiro = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

        if (decimal !== undefined)
        {
            decimal = decimal.replace(/\D/g, "");
            decimal = decimal.substring(0, 2);

            valor.value = inteiro + "," + decimal;
        }
        else
        {
            valor.value = inteiro;
        }
    }
);
