const categoria = document.getElementById("categoria");
const valor = document.getElementById("valor");
const salvar = document.getElementById("salvar");
const despesas = document.getElementById("despesas");

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
            }
        );

        novaDespesa.appendChild(excluirDespesa);
        despesas.appendChild(novaDespesa);
    }
);
