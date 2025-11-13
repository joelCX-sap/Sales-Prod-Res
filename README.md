# 🏭 Eaton Data Analysis Streamlit App

This is the main Streamlit application (`app.py`) that provides an interactive web interface for analyzing SAP data from Excel files. It combines sales, production, and reservations data with AI-powered analysis.

## 🚀 Features

- **Interactive Web Interface**: User-friendly Streamlit dashboard
- **Multiple File Upload**: Simultaneous upload of sales, production, and reservations Excel files
- **Real-time Data Visualization**: Instant display of uploaded data with shape information
- **AI-Powered Analysis**: Two types of analysis powered by GenAI Hub:
  - **Material-Specific Analysis**: Deep dive into individual materials across all datasets
  - **General Query Analysis**: Open-ended questions about the data
- **SAP Data Integration**: Specialized handling of SAP tables (VBAP, AFKO, RESB)
- **Cross-Dataset Correlation**: Links data between sales, production, and reservations using key fields

## 📋 Prerequisites

- Python 3.7+
- Streamlit
- GenAI Hub access (configured in `.env`)
- SAP Excel files (VBAP, AFKO, RESB)

## 🛠️ Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure GenAI Hub in `.env` file

## 🚀 How to Run

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📊 Application Structure

### Main Components

1. **Data Loading Tab**
   - Three-column layout for file uploads
   - Real-time data preview
   - Shape information display
   - Summary statistics

2. **Data Analysis Tab**
   - Material-specific analysis
   - General query interface
   - AI-powered insights
   - Interactive results display

## 🗂️ Supported Data Types

### Sales Data (VBAP table)
- **VBELN**: Sales Document Number (sales order)
- **POSNR**: Sales Document Item
- **MATNR**: Material Number
- **KWMENG**: Sales Quantity (of the finished product)
- **VRKME**: Sales Unit of Measure
- **NETWR**: Net value of the item

### Production Data (AFKO table)
- **AUFNR**: Production Order Number (links with reservations)
- **PLNBEZ**: Material to be Produced (the finished product)
- **GAMNG**: Total order quantity (of the finished product)
- **GMEIN**: Unit of Measure for the order (of the finished product)
- **GSTRP**: Basic start date
- **GLTRP**: Basic finish date

### Reservations Data (RESB table)
- **RSPOS**: Reservation Item
- **AUFNR**: Production Order Number (The key link!)
- **MATNR**: Component Material (the one being consumed)
- **BDMNG**: Reserved Quantity
- **MEINS**: Unit of Measure for the component

## 🤖 AI Analysis Features

### Material Analysis
- Enter a specific material code (e.g., MAT001, 12345)
- AI analyzes the material across all three datasets
- Provides comprehensive insights including:
  - Sales performance summary
  - Production order status
  - Reservation status
  - Cross-reference analysis
  - Risk assessment
  - Timeline analysis
  - Supply chain optimization recommendations

### General Query Analysis
- Ask open-ended questions about your data
- Examples:
  - "What are the top 5 materials by sales volume?"
  - "Are there any production delays that might affect reservations?"
  - "What patterns do you see in the supply chain data?"

## 🔍 Key Functions

### `ask_llm_simple(prompt: str)`
- Interfaces with GenAI Hub
- Sends prompts to GPT-5 model
- Returns AI-generated analysis

### `analyze_material_data(material_code, sales_df, production_df, reservations_df)`
- Filters all datasets by material code
- Counts matching records
- Returns structured analysis data

### `create_analysis_prompt(...)`
- Builds comprehensive prompts for AI analysis
- Includes field definitions and context
- Provides sample data for better AI understanding

## 💾 Session State Management

The app uses Streamlit's session state to maintain:
- `sales_df`: Sales DataFrame
- `production_df`: Production DataFrame
- `reservations_df`: Reservations DataFrame

This ensures data persistence across user interactions.

## 🎨 User Interface

### Layout
- **Header**: Application title and description
- **Tabs**: 
  - "Data Loading": File upload and data preview
  - "Data Analysis": AI-powered analysis tools
- **Columns**: Three-column layout for organized file uploads
- **Interactive Elements**: File uploaders, text inputs, buttons

### Visual Elements
- Data tables with scrolling
- Shape information badges
- Success/error messages
- Loading indicators during AI processing

## 🔄 Data Flow

1. **Upload**: User uploads Excel files → Pandas DataFrames → Session state
2. **Display**: DataFrames shown in interactive tables
3. **Analysis**: User selects analysis type → AI prompt generation
4. **Processing**: Prompt sent to GenAI Hub → AI response received
5. **Results**: Formatted analysis displayed to user

## 🚨 Error Handling

- GenAI Hub connection errors
- File upload validation
- Excel parsing errors
- Missing data scenarios
- Invalid material codes

## 📈 Analysis Capabilities

### Cross-Dataset Analysis
- Links sales orders to production orders via material numbers
- Connects production orders to reservations via AUFNR
- Identifies supply chain bottlenecks
- Detects potential delays and shortages

### Business Intelligence
- Sales performance metrics
- Production efficiency analysis
- Inventory optimization insights
- Supply chain risk assessment

## 🔧 Customization

### Prompts
Modify prompts in:
- `create_analysis_prompt()` for material analysis
- General prompt in the chat section

### UI Elements
- Streamlit components can be customized
- Layout modifications in column definitions
- Styling through Streamlit configuration

## 📊 Sample Usage Scenarios

1. **Material Manager**: Analyze specific material performance across sales, production, and reservations
2. **Supply Chain Analyst**: Identify bottlenecks and optimization opportunities
3. **Production Planner**: Monitor production orders and their impact on reservations
4. **Sales Analyst**: Understand sales patterns and their relationship to production capacity

## 🔒 Security Considerations

- Data stored in memory only (session-based)
- No persistent data storage
- GenAI Hub authentication required
- File type validation for uploads

## 🚀 Performance

- In-memory processing for fast analysis
- Efficient DataFrame operations with Pandas
- Streamlined AI prompt generation
- Real-time data visualization

## 📞 Support

For issues or questions about the Streamlit application:
1. Check GenAI Hub connectivity
2. Verify Excel file formats
3. Review error messages in the interface
4. Contact the development team

## 🔄 Comparison with FastAPI Version

| Aspect | Streamlit (app.py) | FastAPI (fastapi_app.py) |
|--------|-------------------|--------------------------|
| **Interface** | Interactive web app | REST API endpoints |
| **Usage** | Direct user interaction | Programmatic access |
| **Deployment** | Single application | Microservice architecture |
| **Integration** | Standalone | Easy external integration |
| **Documentation** | This README | Auto-generated Swagger |
| **Testing** | Manual through UI | Automated API testing |
| **Scalability** | Single user session | Multi-user, scalable |

Both versions provide the same core functionality but serve different use cases and deployment scenarios.
