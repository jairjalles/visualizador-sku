import streamlit as st

st.set_page_config(page_title="Visualizador de Imagens por SKU", layout="centered")
st.title("🖼️ Visualizador de Imagens por SKU")

input_skus = st.text_area(
    "Cole aqui os SKUs (um por linha ou separados por vírgula):",
    height=200,
    placeholder="Exemplo:\nK-5459-6392\nK-2077-6392"
)

if st.button("🔍 Visualizar Imagens"):
    # Processa os SKUs inseridos
    raw_skus = input_skus.replace(",", "\n").split("\n")
    skus = [sku.strip() for sku in raw_skus if sku.strip()]

    if not skus:
        st.warning("Por favor, insira ao menos um SKU.")
    else:
        for sku in skus:
            url = f"https://topshop-tiny.com.br/wp-content/uploads/tiny/{sku}/{sku}_06.jpg"
            st.image(url, caption=sku, use_container_width=True)
