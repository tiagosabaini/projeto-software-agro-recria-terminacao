document.addEventListener("DOMContentLoaded", function() {
    const categoria = document.getElementById("categoria");
    const valor = document.getElementById("valor");
    const salvar = document.getElementById("salvar");
    const despesas = document.getElementById("despesas");

    if (salvar) {
        salvar.addEventListener("click", function() {
            if (!valor.value || valor.value <= 0) {
                alert("Por favor, insira um valor válido.");
                return;
            }

            const novaDespesa = document.createElement("div");
            novaDespesa.className = "item-despesa";

            const textoDespesa = document.createElement("span");
            textoDespesa.textContent = categoria.options[categoria.selectedIndex].text + ": R$ " + parseFloat(valor.value).toFixed(2);

            const excluirDespesa = document.createElement("button");
            excluirDespesa.textContent = "Excluir";
            excluirDespesa.className = "btn-excluir";

            excluirDespesa.addEventListener("click", function() {
                novaDespesa.remove();
            });

            novaDespesa.appendChild(textoDespesa);
            novaDespesa.appendChild(excluirDespesa);
            despesas.appendChild(novaDespesa);

            valor.value = "";
        });
    }
});