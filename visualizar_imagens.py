import streamlit as st
import requests
import time
import re # For more robust SKU splitting

# --- Configuration & Constants ---
st.set_page_config(page_title="Visualizador de Imagens por SKU", layout="wide")

IMAGE_BASE_URL = "https://topshop-tiny.com.br/wp-content/uploads/tiny"
MAX_IMAGES_TO_CHECK = 6
DEFAULT_FULL_SKU_SUFFIX = "6392" # Standard suffix for K-XXXX type SKUs
REQUEST_TIMEOUT = 5 # seconds

# SKU examples for placeholders
SKU_EXAMPLE_FULL = "K-7810-6392"
SKU_EXAMPLE_ROOT = "4251"
SKU_EXAMPLE_PARTIAL_FULL = "K-1234" # Will be completed to K-1234-6392

# --- Helper Functions ---
def normalize_sku(sku_input: str, sku_type: str) -> tuple[str | None, str]:
    """
    Normalizes the SKU based on its type and input.
    Returns a tuple: (normalized_sku_for_url_and_filename, display_name)
    Returns (None, display_name) if SKU is invalid for the selected type.
    """
    sku_input = sku_input.strip().upper()
    display_name = sku_input

    if sku_type == "SKU Completo (K-XXXX-6392)":
        if sku_input.startswith("K-"):
            parts = sku_input.split('-')
            if len(parts) == 2: # K-XXXX
                normalized_sku = f"{sku_input}-{DEFAULT_FULL_SKU_SUFFIX}"
                display_name = normalized_sku
                return normalized_sku, display_name
            elif len(parts) == 3: # K-XXXX-YYYY
                # Assume it's correctly formatted if all 3 parts are there
                return sku_input, display_name
            else: # Malformed K-SKU
                st.error(f"SKU Completo '{sku_input}' inválido. Formato esperado: K-XXXX ou K-XXXX-{DEFAULT_FULL_SKU_SUFFIX}.")
                return None, display_name
        else: # Does not start with K-, assume it's the XXXX part
            normalized_sku = f"K-{sku_input}-{DEFAULT_FULL_SKU_SUFFIX}"
            display_name = normalized_sku
            return normalized_sku, display_name
    elif sku_type == "SKU Raiz (ex: 4251)":
        # For root SKU, no specific K- prefix or suffix is expected, use as is
        # Add any validation for root SKU format if needed (e.g., must be all digits)
        if not sku_input.isalnum(): # Basic check: allow alphanumeric
             st.warning(f"SKU Raiz '{sku_input}' contém caracteres não alfanuméricos. Tentando usar mesmo assim.")
        return sku_input, display_name
    return None, display_name


def fetch_and_display_images(sku_identifier: str, display_name: str):
    """
    Fetches and displays images for a given normalized SKU identifier.
    The sku_identifier is used for both the folder and the image filename prefix.
    """
    st.subheader(f"SKU: {display_name}")
    cols = st.columns(MAX_IMAGES_TO_CHECK)
    found_any_for_this_sku = False
    
    # The URL structure is: IMAGE_BASE_URL / sku_identifier / sku_identifier_XX.jpg
    base_sku_path = f"{IMAGE_BASE_URL}/{sku_identifier}"

    for i in range(1, MAX_IMAGES_TO_CHECK + 1):
        image_number_str = f"{i:02d}"
        image_filename = f"{sku_identifier}_{image_number_str}.jpg"
        image_url = f"{base_sku_path}/{image_filename}?v={int(time.time())}" # Cache buster

        col_idx = (i - 1) % MAX_IMAGES_TO_CHECK

        try:
            response = requests.head(image_url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                cols[col_idx].image(image_url, caption=image_filename, use_container_width=True)
                # Text input for easy copying of the URL
                cols[col_idx].text_input(
                    label="🔗 Link:",
                    value=image_url,
                    key=f"link_{display_name}_{image_number_str}", # Unique key
                    help="URL da imagem para copiar."
                )
                found_any_for_this_sku = True
            # Optionally, provide feedback for non-200 images if desired
            # else:
            #     with cols[col_idx]:
            #         st.caption(f"{image_filename} (não encontrada - {response.status_code})")

        except requests.exceptions.Timeout:
            with cols[col_idx]:
                st.caption(f"{image_filename} (Timeout)")
        except requests.exceptions.RequestException:
            # Silently ignore other request exceptions (e.g., connection error) for a cleaner UI for now
            # or provide minimal feedback:
            # with cols[col_idx]:
            #     st.caption(f"{image_filename} (Erro)")
            pass

    if not found_any_for_this_sku:
        st.error(f"Nenhuma imagem encontrada para {display_name} com o prefixo '{sku_identifier}'.")
    st.markdown("---")


# --- Streamlit UI ---
st.title("🖼️ Visualizador de Imagens por SKU")

tipo_sku = st.radio(
    "Tipo de SKU:",
    ["SKU Completo (K-XXXX-6392)", "SKU Raiz (ex: 4251)"],
    horizontal=True,
    key="sku_type_selector"
)

# Dynamically update placeholder based on selected SKU type
placeholder_text = (
    f"Exemplo:\n{SKU_EXAMPLE_FULL}\n{SKU_EXAMPLE_PARTIAL_FULL}\nK-5555"
    if "Completo" in tipo_sku
    else f"Exemplo:\n{SKU_EXAMPLE_ROOT}\n7890"
)

input_skus_str = st.text_area(
    "Cole os SKUs (um por linha, separados por vírgula ou espaço):",
    height=200,
    placeholder=placeholder_text,
    key="sku_input_area"
)

if st.button("🔍 Visualizar Imagens", key="visualize_button"):
    # Split SKUs by comma, newline, or space, and remove empty strings
    raw_sku_list = re.split(r'[,\s\n]+', input_skus_str)
    cleaned_skus = [sku.strip() for sku in raw_sku_list if sku.strip()]

    if not cleaned_skus:
        st.warning("Por favor, insira ao menos um SKU.")
    else:
        processed_count = 0
        for sku_input_value in cleaned_skus:
            normalized_sku_id, display_name = normalize_sku(sku_input_value, tipo_sku)

            if normalized_sku_id:
                fetch_and_display_images(normalized_sku_id, display_name)
                processed_count +=1
            # Else, normalize_sku already showed an error for invalid format.
        
        if processed_count == 0 and cleaned_skus:
             st.error("Nenhum dos SKUs fornecidos era válido para o tipo selecionado.")
        elif processed_count > 0:
            st.success(f"Visualização concluída para {processed_count} SKU(s) válidos.")
