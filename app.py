import streamlit as st
import pandas as pd
import io

# GenAI Hub Setup
from dotenv import load_dotenv


load_dotenv()
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Initialize proxy client
try:
    proxy_client = get_proxy_client("gen-ai-hub")
except Exception as e:
    proxy_client = None
    st.error(f"GenAI Hub connection error: {str(e)}")

def ask_llm_simple(prompt: str) -> str:
    """Simple LLM function using GenAI Hub"""
    if proxy_client is None:
        return "GenAI Hub is not available. Please check your configuration."
    
    try:
        llm = ChatOpenAI(proxy_model_name="gpt-5", proxy_client=proxy_client)
        response = llm.invoke(prompt).content
        return response
    except Exception as e:
        return f"Error querying LLM: {str(e)}"

def analyze_material_data(material_code, sales_df, production_df, reservations_df):
    """Analyze data for a specific material across all three datasets"""
    analysis_data = {}
    
    # Sales analysis
    if sales_df is not None:
        sales_data = sales_df[sales_df.astype(str).apply(lambda x: x.str.contains(str(material_code), case=False, na=False)).any(axis=1)]
        analysis_data['sales'] = {
            'count': len(sales_data),
            'data': sales_data.to_dict('records') if len(sales_data) > 0 else []
        }
    
    # Production analysis
    if production_df is not None:
        production_data = production_df[production_df.astype(str).apply(lambda x: x.str.contains(str(material_code), case=False, na=False)).any(axis=1)]
        analysis_data['production'] = {
            'count': len(production_data),
            'data': production_data.to_dict('records') if len(production_data) > 0 else []
        }
    
    # Reservations analysis
    if reservations_df is not None:
        reservations_data = reservations_df[reservations_df.astype(str).apply(lambda x: x.str.contains(str(material_code), case=False, na=False)).any(axis=1)]
        analysis_data['reservations'] = {
            'count': len(reservations_data),
            'data': reservations_data.to_dict('records') if len(reservations_data) > 0 else []
        }
    
    return analysis_data

def create_analysis_prompt(material_code, analysis_data, sales_df, production_df, reservations_df):
    """Create a comprehensive prompt for LLM analysis with full context"""
    
    # Get sample data and column information
    sales_sample = sales_df.head(5).to_dict('records') if sales_df is not None else []
    production_sample = production_df.head(5).to_dict('records') if production_df is not None else []
    reservations_sample = reservations_df.head(5).to_dict('records') if reservations_df is not None else []
    
    prompt = f"""
You are an expert SAP data analyst specializing in supply chain and production analysis. 

FIELD DEFINITIONS FOR CONTEXT:

RESERVATIONS DATA (RESB table):
- RSPOS: Reservation Item
- AUFNR: Production Order Number (The key link!)
- MATNR: Component Material (the one being consumed)
- BDMNG: Reserved Quantity
- MEINS: Unit of Measure for the component

PRODUCTION DATA (AFKO table):
- AUFNR: Production Order Number (links with reservations)
- PLNBEZ: Material to be Produced (the finished product)
- GAMNG: Total order quantity (of the finished product)
- GMEIN: Unit of Measure for the order (of the finished product)
- GSTRP: Basic start date
- GLTRP: Basic finish date

SALES DATA (VBAP table):
- VBELN: Sales Document Number (sales order)
- POSNR: Sales Document Item
- MATNR: Material Number
- KWMENG: Sales Quantity (of the finished product)
- VRKME: Sales Unit of Measure
- NETWR: Net value of the item

ANALYSIS REQUEST FOR MATERIAL: {material_code}

CURRENT DATASET INFORMATION:

SALES DATA ({analysis_data.get('sales', {}).get('count', 0)} records found for material {material_code}):
Available columns: {list(sales_df.columns) if sales_df is not None else []}
Sample of full dataset (first 5 rows): {sales_sample}
Filtered data for material {material_code}: {analysis_data.get('sales', {}).get('data', [])}

PRODUCTION DATA ({analysis_data.get('production', {}).get('count', 0)} records found for material {material_code}):
Available columns: {list(production_df.columns) if production_df is not None else []}
Sample of full dataset (first 5 rows): {production_sample}
Filtered data for material {material_code}: {analysis_data.get('production', {}).get('data', [])}

RESERVATIONS DATA ({analysis_data.get('reservations', {}).get('count', 0)} records found for material {material_code}):
Available columns: {list(reservations_df.columns) if reservations_df is not None else []}
Sample of full dataset (first 5 rows): {reservations_sample}
Filtered data for material {material_code}: {analysis_data.get('reservations', {}).get('data', [])}

Please provide a comprehensive analysis including:
1. Summary of sales performance and quantities for this material
2. Production orders status and quantities (linking via AUFNR when possible)
3. Reservation status and component consumption
4. Cross-reference analysis: How do sales orders relate to production orders and material reservations?
5. Risk analysis: Could sales orders be affected by reservation shortages or production delays?
6. Timeline analysis using start dates (GSTRP) and finish dates (GLTRP)
7. Recommendations for supply chain optimization

Focus on the relationships between AUFNR (production orders), MATNR (materials), quantities (BDMNG, GAMNG, KWMENG), and dates.
"""
    return prompt

def main():
    st.title("Excel File Loader - Sales, Production & Reservations")
    
    # Initialize session state for dataframes
    if 'sales_df' not in st.session_state:
        st.session_state.sales_df = None
    if 'production_df' not in st.session_state:
        st.session_state.production_df = None
    if 'reservations_df' not in st.session_state:
        st.session_state.reservations_df = None
    
    # Create tabs
    tab1, tab2 = st.tabs(["Data Loading", "Data Analysis"])
    
    with tab1:
        st.markdown("---")
        
        # Create three columns for file uploaders
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Sales Data")
            sales_file = st.file_uploader(
                "Upload Sales Excel File", 
                type=['xlsx', 'xls'], 
                key="sales_uploader"
            )
            
            if sales_file is not None:
                try:
                    st.session_state.sales_df = pd.read_excel(sales_file)
                    st.success(f"Sales file loaded successfully!")
                    st.info(f"Shape: {st.session_state.sales_df.shape}")
                except Exception as e:
                    st.error(f"Error loading sales file: {str(e)}")
        
        with col2:
            st.subheader("Production Data")
            production_file = st.file_uploader(
                "Upload Production Excel File", 
                type=['xlsx', 'xls'], 
                key="production_uploader"
            )
            
            if production_file is not None:
                try:
                    st.session_state.production_df = pd.read_excel(production_file)
                    st.success(f"Production file loaded successfully!")
                    st.info(f"Shape: {st.session_state.production_df.shape}")
                except Exception as e:
                    st.error(f"Error loading production file: {str(e)}")
        
        with col3:
            st.subheader("Reservations Data")
            reservations_file = st.file_uploader(
                "Upload Reservations Excel File", 
                type=['xlsx', 'xls'], 
                key="reservations_uploader"
            )
            
            if reservations_file is not None:
                try:
                    st.session_state.reservations_df = pd.read_excel(reservations_file)
                    st.success(f"Reservations file loaded successfully!")
                    st.info(f"Shape: {st.session_state.reservations_df.shape}")
                except Exception as e:
                    st.error(f"Error loading reservations file: {str(e)}")
        
        st.markdown("---")
        
        # Display DataFrames if they exist
        if st.session_state.sales_df is not None:
            st.subheader("Sales DataFrame")
            st.dataframe(st.session_state.sales_df)
            st.text(f"Sales DataFrame shape: {st.session_state.sales_df.shape}")
        
        if st.session_state.production_df is not None:
            st.subheader("Production DataFrame")
            st.dataframe(st.session_state.production_df)
            st.text(f"Production DataFrame shape: {st.session_state.production_df.shape}")
        
        if st.session_state.reservations_df is not None:
            st.subheader("Reservations DataFrame")
            st.dataframe(st.session_state.reservations_df)
            st.text(f"Reservations DataFrame shape: {st.session_state.reservations_df.shape}")
        
        # Show summary if all files are loaded
        if all([st.session_state.sales_df is not None, 
                st.session_state.production_df is not None, 
                st.session_state.reservations_df is not None]):
            st.markdown("---")
            st.success("All three DataFrames have been created successfully!")
            
            # Summary information
            st.subheader("Summary")
            summary_data = {
                "DataFrame": ["Sales", "Production", "Reservations"],
                "Rows": [
                    st.session_state.sales_df.shape[0],
                    st.session_state.production_df.shape[0],
                    st.session_state.reservations_df.shape[0]
                ],
                "Columns": [
                    st.session_state.sales_df.shape[1],
                    st.session_state.production_df.shape[1],
                    st.session_state.reservations_df.shape[1]
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            st.table(summary_df)
    
    with tab2:
        st.subheader("AI-Powered Data Analysis")
        
        # Check if all dataframes are loaded
        if not all([st.session_state.sales_df is not None, 
                   st.session_state.production_df is not None, 
                   st.session_state.reservations_df is not None]):
            st.warning("Please load all three Excel files in the 'Data Loading' tab before using the analysis features.")
            return
        
        st.markdown("---")
        
        # Analysis options
        analysis_type = st.selectbox(
            "Select Analysis Type:",
            ["Material Analysis", "General Query"]
        )
        
        if analysis_type == "Material Analysis":
            st.subheader("Material-Specific Analysis")
            st.write("Enter a material code to get comprehensive analysis across sales, production, and reservations data.")
            
            material_code = st.text_input("Enter Material Code:", placeholder="e.g., MAT001, 12345")
            
            if st.button("Analyze Material", type="primary"):
                if material_code:
                    with st.spinner("Analyzing material data..."):
                        # Get material data from all sources
                        analysis_data = analyze_material_data(
                            material_code, 
                            st.session_state.sales_df, 
                            st.session_state.production_df, 
                            st.session_state.reservations_df
                        )
                        
                        # Create prompt for LLM
                        prompt = create_analysis_prompt(
                            material_code, 
                            analysis_data, 
                            st.session_state.sales_df, 
                            st.session_state.production_df, 
                            st.session_state.reservations_df
                        )
                        
                        # Get AI analysis
                        ai_response = ask_llm_simple(prompt)
                        
                        # Display results
                        st.subheader(f"Analysis Results for Material: {material_code}")
                        
                        # Show data summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Sales Records", analysis_data.get('sales', {}).get('count', 0))
                        with col2:
                            st.metric("Production Records", analysis_data.get('production', {}).get('count', 0))
                        with col3:
                            st.metric("Reservation Records", analysis_data.get('reservations', {}).get('count', 0))
                        
                        # Show AI analysis
                        st.subheader("AI Analysis")
                        st.write(ai_response)
                        
                        # Show detailed data if available
                        if analysis_data.get('sales', {}).get('count', 0) > 0:
                            st.subheader("Sales Data for Material")
                            sales_filtered = st.session_state.sales_df[
                                st.session_state.sales_df.astype(str).apply(
                                    lambda x: x.str.contains(str(material_code), case=False, na=False)
                                ).any(axis=1)
                            ]
                            st.dataframe(sales_filtered)
                        
                        if analysis_data.get('production', {}).get('count', 0) > 0:
                            st.subheader("Production Data for Material")
                            production_filtered = st.session_state.production_df[
                                st.session_state.production_df.astype(str).apply(
                                    lambda x: x.str.contains(str(material_code), case=False, na=False)
                                ).any(axis=1)
                            ]
                            st.dataframe(production_filtered)
                        
                        if analysis_data.get('reservations', {}).get('count', 0) > 0:
                            st.subheader("Reservations Data for Material")
                            reservations_filtered = st.session_state.reservations_df[
                                st.session_state.reservations_df.astype(str).apply(
                                    lambda x: x.str.contains(str(material_code), case=False, na=False)
                                ).any(axis=1)
                            ]
                            st.dataframe(reservations_filtered)
                        
                else:
                    st.error("Please enter a material code to analyze.")
        
        elif analysis_type == "General Query":
            st.subheader("General Data Analysis")
            st.write("Ask any question about your sales, production, and reservations data.")
            
            user_query = st.text_area("Enter your question:", 
                                    placeholder="e.g., What are the top 5 materials by sales volume? Are there any production delays that might affect reservations?",
                                    height=100)
            
            if st.button("Ask AI", type="primary"):
                if user_query:
                    with st.spinner("Analyzing your query..."):
                        # Create a general analysis prompt with SAP context
                        general_prompt = f"""
You are an expert SAP data analyst specializing in supply chain and production analysis.

FIELD DEFINITIONS FOR CONTEXT:

RESERVATIONS DATA (RESB table):
- RSPOS: Reservation Item
- AUFNR: Production Order Number (The key link!)
- MATNR: Component Material (the one being consumed)
- BDMNG: Reserved Quantity
- MEINS: Unit of Measure for the component

PRODUCTION DATA (AFKO table):
- AUFNR: Production Order Number (links with reservations)
- PLNBEZ: Material to be Produced (the finished product)
- GAMNG: Total order quantity (of the finished product)
- GMEIN: Unit of Measure for the order (of the finished product)
- GSTRP: Basic start date
- GLTRP: Basic finish date

SALES DATA (VBAP table):
- VBELN: Sales Document Number (sales order)
- POSNR: Sales Document Item
- MATNR: Material Number
- KWMENG: Sales Quantity (of the finished product)
- VRKME: Sales Unit of Measure
- NETWR: Net value of the item

CURRENT DATASETS:

SALES DATA: {st.session_state.sales_df.shape[0]} rows, {st.session_state.sales_df.shape[1]} columns
Available columns: {list(st.session_state.sales_df.columns)}
Sample data (first 5 rows): {st.session_state.sales_df.head(5).to_dict('records')}

PRODUCTION DATA: {st.session_state.production_df.shape[0]} rows, {st.session_state.production_df.shape[1]} columns
Available columns: {list(st.session_state.production_df.columns)}
Sample data (first 5 rows): {st.session_state.production_df.head(5).to_dict('records')}

RESERVATIONS DATA: {st.session_state.reservations_df.shape[0]} rows, {st.session_state.reservations_df.shape[1]} columns
Available columns: {list(st.session_state.reservations_df.columns)}
Sample data (first 5 rows): {st.session_state.reservations_df.head(5).to_dict('records')}

USER QUESTION: {user_query}

Please provide a comprehensive analysis and answer based on:
1. The SAP field definitions above
2. The actual data structure and sample records
3. Relationships between tables (especially via AUFNR and MATNR)
4. Focus on quantities, dates, and business implications
5. Include specific recommendations and insights where appropriate

Analyze the data relationships and provide actionable insights for supply chain optimization.
"""
                        
                        ai_response = ask_llm_simple(general_prompt)
                        
                        st.subheader("AI Response")
                        st.write(ai_response)
                else:
                    st.error("Please enter a question to analyze.")

if __name__ == "__main__":
    main()
