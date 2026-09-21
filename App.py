import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS (Matches Presentation Style)
# ---------------------------------------------------------
st.set_page_config(
    page_title="GSDSS Decision Support & Recommendation",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS styling for rounded card borders and presentation fonts
st.markdown("""
    <style>
    .main-title {
        color: #1e3d59;
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 25px;
    }
    .card-box {
        background-color: #f7fafc;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    .sub-heading {
        color: #1e3d59;
        font-weight: 700;
        font-size: 1.4rem;
        margin-bottom: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">GSDSS Decision Support & Recommendation</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Sidebar Navigation Mode
# ---------------------------------------------------------
st.sidebar.title("⚙️ Workflow Settings")
mode = st.sidebar.radio("Select Input Mode:", ["1. Manual Inputs", "2. Upload STAAD.Pro File (.xlsx/.csv)"])

st.sidebar.divider()

# ---------------------------------------------------------
# MODE 1: MANUAL INPUTS & RECOMMENDATION
# ---------------------------------------------------------
if mode == "1. Manual Inputs":
    st.sidebar.header("📥 Dashboard Inputs Controls")
    
    building_type = st.sidebar.selectbox("Building Type", ["Commercial", "Residential", "Industrial", "Public Building"])
    span_length = st.sidebar.number_input("Span Length (m)", value=6.0, step=0.5)
    grid_spacing = st.sidebar.number_input("Grid Spacing (m)", value=4.5, step=0.5)
    beam_depth = st.sidebar.number_input("Beam Depth (mm)", value=600, step=50)
    slab_thickness = st.sidebar.number_input("Slab Thickness (mm)", value=150, step=10)
    concrete_grade = st.sidebar.selectbox("Concrete Grade", ["M20", "M25", "M30", "M35", "M40"], index=2)
    steel_grade = st.sidebar.selectbox("Steel Grade", ["Fe415", "Fe500", "Fe550", "Fe500D"], index=1)
    seismic_zone = st.sidebar.selectbox("Seismic Zone", ["Zone II", "Zone III", "Zone IV", "Zone V"], index=1)
    loading_parameters = st.sidebar.number_input("Loading Parameters (Live Load kN/m²)", value=3.0, step=0.5)

    # Engineering Decision Logic based on inputs
    rec_grid_type = "Rectangular" if grid_spacing <= 6.0 else "Flat Slab Layout"
    
    if span_length >= 8.0 or loading_parameters >= 5.0 or seismic_zone in ["Zone IV", "Zone V"]:
        rec_concrete = "M35"
    elif span_length >= 6.0 or loading_parameters >= 3.0:
        rec_concrete = "M30"
    else:
        rec_concrete = concrete_grade

    rec_steel = "Fe500D" if seismic_zone in ["Zone IV", "Zone V"] else steel_grade
    rec_beam_depth = f"{int(beam_depth)} mm"
    rec_grid_spacing = f"{grid_spacing} × {span_length} m"

    # Screen Layout: Two Columns matching the slide layout
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="card-box"><div class="sub-heading">Dashboard Inputs</div>', unsafe_allow_html=True)
        inputs_data = pd.DataFrame({
            "Input Parameter": [
                "• Building Type", "• Span Length", "• Grid Spacing", 
                "• Beam Depth", "• Slab Thickness", "• Concrete Grade", 
                "• Steel Grade", "• Seismic Zone", "• Loading Parameters"
            ],
            "Selected Value": [
                building_type, f"{span_length} m", f"{grid_spacing} m", 
                f"{beam_depth} mm", f"{slab_thickness} mm", concrete_grade, 
                steel_grade, seismic_zone, f"{loading_parameters} kN/m²"
            ]
        })
        st.table(inputs_data)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown(f"""
        <div class="card-box">
            <div class="sub-heading">EXAMPLE RECOMMENDATION</div>
            <br>
            <div style="font-size: 1.15rem; line-height: 2.2; color: #334155;">
                <b>Recommended Grid Type:</b> {rec_grid_type}<br>
                <b>Recommended Concrete Grade:</b> {rec_concrete}<br>
                <b>Recommended Steel Grade:</b> {rec_steel}<br>
                <b>Recommended Beam Depth:</b> {rec_beam_depth}<br>
                <b>Recommended Grid Spacing:</b> {rec_grid_spacing}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MODE 2: STAAD.PRO EXCEL/CSV UPLOAD
# ---------------------------------------------------------
else:
    st.subheader("📂 Upload STAAD.Pro Output File")
    uploaded_file = st.file_uploader("Upload Excel (.xlsx) or CSV (.csv) file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            df_staad = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success("STAAD.Pro Output File Successfully Processed!")
            
            st.subheader("📄 STAAD Data Preview")
            st.dataframe(df_staad.head(10), use_container_width=True)

            num_cols = df_staad.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if num_cols:
                st.subheader("📈 Structural Results Visualizer")
                x_axis = st.selectbox("Select X-Axis Parameter:", df_staad.columns, index=0)
                y_axis = st.selectbox("Select Y-Axis Parameter (Bending Moment / Shear Force):", num_cols, index=0)

                fig = px.bar(df_staad, x=x_axis, y=y_axis, title=f"{y_axis} Analysis across {x_axis}", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

                max_val = df_staad[y_axis].max()
                st.markdown(f"""
                <div class="card-box">
                    <div class="sub-heading">GSDSS Recommendation based on STAAD Analysis</div>
                    <ul>
                        <li><b>Peak Design Value ({y_axis}):</b> {max_val:.2f}</li>
                        <li><b>Recommended Concrete Grade:</b> M30 or higher</li>
                        <li><b>Recommended Steel Grade:</b> Fe500D (high ductility)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error processing STAAD file: {e}")7
