fetch("/status")
.then(resposta => resposta.json())
.then(dados => {

    document.getElementById("produtos").innerText = dados.produtos;
    document.getElementById("hora").innerText = dados.ultima_atualizacao;

})
.catch(() => {

    document.getElementById("produtos").innerText = "Erro";
    document.getElementById("hora").innerText = "Erro";

});

fetch("/produtos")
.then(resposta => resposta.json())
.then(produtos => {

    let lista = "";

    produtos.forEach(produto => {

        lista += `
        <div style="background:#2a2a2a;padding:15px;border-radius:10px;margin-bottom:10px;">
            <h3>${produto.nome}</h3>
            <p>Categoria: ${produto.categoria}</p>
            <p>Preço: R$ ${produto.preco.toFixed(2).replace(".", ",")}</p>
        </div>
        `;

    });

    document.getElementById("lista-produtos").innerHTML = lista;

});
