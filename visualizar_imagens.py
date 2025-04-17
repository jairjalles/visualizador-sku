import streamlit as st
import requests
import time

st.set_page_config(page_title="Visualizador de Imagens por SKU", layout="wide")
st.title("🖼️ Visualizador de Imagens por SKU")

# Seletor do tipo de SKU
tipo_sku = st.radio("Tipo de SKU:", ["SKU Completo (K-XXXX-6392)", "SKU Raiz (ex: 4251)"], horizontal=True)

input_skus = st.text_area(
    "Cole os SKUs (um por linha ou separados por vírgula):",
    height=200,
    placeholder="Exemplo:\nK-7810-6392\nK-4251-6392" if "Completo" in tipo_sku else "Exemplo:\n4251\n7890"
)

if st.button("🔍 Visualizar Imagens"):
    raw = input_skus.replace(",", "\n").split("\n")
    skus = [s.strip() for s in raw if s.strip()]

    if not skus:
        st.warning("Por favor, insira ao menos um SKU.")
    else:
        for sku in skus:
            if tipo_sku == "SKU Completo (K-XXXX-6392)":
                full_sku = sku if sku.startswith("K-") else f"K-{sku}-6392"
                base_path = f"https://topshop-tiny.com.br/wp-content/uploads/tiny/{full_sku}"
                prefix = full_sku
            else:
                full_sku = sku  # Raiz
                base_path = f"https://topshop-tiny.com.br/wp-content/uploads/tiny/{full_sku}"
                prefix = full_sku

            st.subheader(f"SKU: {prefix}")
            cols = st.columns(6)  # Garante que até 6 fiquem lado a lado

            found_any = False
            for idx, i in enumerate(range(1, 7)):  # 1 a 6
                num = f"{i:02d}"
                url = f"{base_path}/{prefix}_{num}.jpg?v={int(time.time())}"

                try:
                    resp = requests.head(url, timeout=3)
                except requests.RequestException:
                    resp = None

                if resp and resp.status_code == 200:
                    cols[idx].image(url, caption=f"{prefix}_{num}", use_container_width=True)
                    found_any = True

            if not found_any:
                st.error(f"Nenhuma imagem encontrada para {prefix}")
            st.markdown("---")
