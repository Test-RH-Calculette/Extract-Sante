import pandas as pd
import pdfplumber
import os
import streamlit as st
import re

def extract_data_from_pdf(pdf_path):
    """Extracts reimbursement data from Ameli-like PDF statements."""
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    match = re.search(r'(\d{2}/\d{2}/\d{4})\s+([A-ZÉÀÙÂÊÎÔÛÄËÏÖÜÇ \-]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d]+)%\s+([\d,\.]+)', line)
                    if match:
                        date = match.group(1)
                        prestation = match.group(2).strip()
                        montant_base = float(match.group(3).replace(',', '.'))
                        montant_rembourse = float(match.group(6).replace(',', '.'))
                        data.append([date, prestation, montant_base, montant_rembourse])
    
    return pd.DataFrame(data, columns=['Date', 'Prestation', 'Base Remb.', 'Montant Remb.'])

def main():
    st.set_page_config(page_title="Suivi des Remboursements Ameli", layout="wide")
    st.title("📄 Suivi des Remboursements Ameli")
    st.markdown("Importez vos relevés Ameli au format PDF et suivez vos remboursements.")
    
    uploaded_file = st.file_uploader("📤 Importez votre relevé Ameli (PDF)", type="pdf")
    
    if uploaded_file is not None:
        pdf_path = f"temp_{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        
        data = extract_data_from_pdf(pdf_path)
        
        if not data.empty:
            st.success("✅ Données extraites avec succès !")
            st.dataframe(data)
            csv_data = data.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Télécharger le fichier CSV",
                data=csv_data,
                file_name="remboursements.csv",
                mime="text/csv"
            )
        else:
            st.error("⚠️ Aucune donnée de remboursement trouvée dans ce fichier.")
        
        os.remove(pdf_path)  # Nettoyage du fichier temporaire

if __name__ == "__main__":
    main()
