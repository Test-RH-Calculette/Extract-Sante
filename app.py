import pandas as pd
import pdfplumber
import os
import streamlit as st

def extract_data_from_pdf(pdf_path):
    """Extracts reimbursement data from Ameli PDF statements."""
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    if 'REMBOURSEMENT' in line.upper():
                        parts = line.split()
                        if len(parts) >= 3:
                            date = parts[0]  # Assuming first part is date
                            montant = parts[-1].replace('€', '').replace(',', '.')  # Last part is amount
                            description = ' '.join(parts[1:-1])  # Middle part is description
                            data.append([date, description, float(montant)])
    
    return pd.DataFrame(data, columns=['Date', 'Description', 'Montant'])

def save_to_csv(dataframe, csv_path):
    """Saves extracted data to a CSV file."""
    dataframe.to_csv(csv_path, index=False)

def main():
    st.title("Suivi des Remboursements Ameli")
    
    uploaded_file = st.file_uploader("Importez votre relevé Ameli (PDF)", type="pdf")
    
    if uploaded_file is not None:
        pdf_path = f"temp_{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        
        data = extract_data_from_pdf(pdf_path)
        
        if not data.empty:
            st.success("Données extraites avec succès !")
            st.dataframe(data)
            save_to_csv(data, "remboursements.csv")
            st.download_button(
                label="Télécharger le fichier CSV",
                data=data.to_csv(index=False),
                file_name="remboursements.csv",
                mime="text/csv"
            )
        else:
            st.error("Aucune donnée de remboursement trouvée dans ce fichier.")
        
        os.remove(pdf_path)  # Nettoyage du fichier temporaire

if __name__ == "__main__":
    main()
