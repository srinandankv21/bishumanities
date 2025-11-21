import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(page_title="School Results Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Grade order for consistent sorting
GRADE_ORDER = ['A*', 'A', 'B', 'C', 'D', 'E', 'U']
GRADE_COLORS = {
    'A*': '#2ecc71',
    'A': '#3498db',
    'B': '#9b59b6',
    'C': '#f39c12',
    'D': '#e67e22',
    'E': '#e74c3c',
    'U': '#95a5a6'
}

def load_sample_data():
    """Generate sample data structure for demonstration"""
    data = {
        'Division': ['Primary'] * 30 + ['Secondary'] * 30,
        'Class': (
            ['Class 1'] * 10 + ['Class 2'] * 10 + ['Class 3'] * 10 +
            ['Class 4'] * 10 + ['Class 5'] * 10 + ['Class 6'] * 10
        ),
        'Grade': GRADE_ORDER * 8 + ['A*', 'A', 'B', 'C'],
        'Count': [5, 8, 12, 10, 8, 5, 2, 4, 6, 10, 8, 6, 4, 3, 6, 9, 11, 9, 7, 4,
                 3, 7, 10, 12, 8, 5, 3, 8, 12, 15, 10, 7, 5, 4, 10, 14, 16, 12, 8,
                 6, 4, 9, 13, 14, 11, 7, 5, 5, 11, 15, 13, 9, 6, 4, 8, 12, 14, 11, 8, 5]
    }
    return pd.DataFrame(data)

def process_data(df):
    """Process uploaded data"""
    # Ensure grade ordering
    df['Grade'] = pd.Categorical(df['Grade'], categories=GRADE_ORDER, ordered=True)
    df = df.sort_values('Grade')
    return df

def create_distribution_chart(df, title, chart_type='bar'):
    """Create grade distribution chart"""
    grade_dist = df.groupby('Grade')['Count'].sum().reindex(GRADE_ORDER, fill_value=0)
    
    if chart_type == 'bar':
        fig = go.Figure(data=[
            go.Bar(x=grade_dist.index, y=grade_dist.values,
                   marker_color=[GRADE_COLORS[g] for g in grade_dist.index],
                   text=grade_dist.values, textposition='auto')
        ])
    else:  # pie chart
        fig = go.Figure(data=[
            go.Pie(labels=grade_dist.index, values=grade_dist.values,
                   marker_colors=[GRADE_COLORS[g] for g in grade_dist.index],
                   textinfo='label+percent+value')
        ])
    
    fig.update_layout(
        title=title,
        xaxis_title="Grade" if chart_type == 'bar' else None,
        yaxis_title="Number of Students" if chart_type == 'bar' else None,
        height=400,
        showlegend=True if chart_type == 'pie' else False
    )
    return fig

def create_stacked_comparison(df, classes):
    """Create stacked bar chart comparing multiple classes"""
    fig = go.Figure()
    
    for grade in GRADE_ORDER:
        values = []
        for class_name in classes:
            class_data = df[(df['Class'] == class_name) & (df['Grade'] == grade)]
            values.append(class_data['Count'].sum() if not class_data.empty else 0)
        
        fig.add_trace(go.Bar(
            name=grade,
            x=classes,
            y=values,
            marker_color=GRADE_COLORS[grade],
            text=values,
            textposition='auto'
        ))
    
    fig.update_layout(
        barmode='stack',
        title='Grade Distribution Comparison Across Classes',
        xaxis_title='Class',
        yaxis_title='Number of Students',
        height=500,
        legend_title='Grade'
    )
    return fig

# Main App
st.markdown('<div class="main-header">🎓 School Results Dashboard</div>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
view_option = st.sidebar.radio("Select View:", ["Overview", "Primary School", "Secondary School"])

# File upload
st.sidebar.markdown("---")
st.sidebar.subheader("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = process_data(df)
    st.sidebar.success("Data loaded successfully!")
else:
    st.sidebar.info("Using sample data for demonstration")
    df = load_sample_data()
    df = process_data(df)

# Overview Section
if view_option == "Overview":
    st.markdown('<div class="section-header">📊 Overall School Performance</div>', unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_students = df['Count'].sum()
        st.metric("Total Students", f"{total_students:,}")
    with col2:
        primary_students = df[df['Division'] == 'Primary']['Count'].sum()
        st.metric("Primary Students", f"{primary_students:,}")
    with col3:
        secondary_students = df[df['Division'] == 'Secondary']['Count'].sum()
        st.metric("Secondary Students", f"{secondary_students:,}")
    with col4:
        pass_rate = ((df[df['Grade'] != 'U']['Count'].sum() / total_students) * 100) if total_students > 0 else 0
        st.metric("Pass Rate", f"{pass_rate:.1f}%")
    
    st.markdown("---")
    
    # Primary vs Secondary comparison
    col1, col2 = st.columns(2)
    
    with col1:
        primary_data = df[df['Division'] == 'Primary']
        fig1 = create_distribution_chart(primary_data, "Primary School Grade Distribution", 'bar')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        secondary_data = df[df['Division'] == 'Secondary']
        fig2 = create_distribution_chart(secondary_data, "Secondary School Grade Distribution", 'bar')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Combined comparison
    st.markdown('<div class="section-header">🔄 Primary vs Secondary Comparison</div>', unsafe_allow_html=True)
    
    fig_combined = go.Figure()
    for division in ['Primary', 'Secondary']:
        division_data = df[df['Division'] == division]
        grade_dist = division_data.groupby('Grade')['Count'].sum().reindex(GRADE_ORDER, fill_value=0)
        fig_combined.add_trace(go.Bar(
            name=division,
            x=grade_dist.index,
            y=grade_dist.values,
            text=grade_dist.values,
            textposition='auto'
        ))
    
    fig_combined.update_layout(
        barmode='group',
        title='Primary vs Secondary Grade Distribution',
        xaxis_title='Grade',
        yaxis_title='Number of Students',
        height=500
    )
    st.plotly_chart(fig_combined, use_container_width=True)

# Primary School Section
elif view_option == "Primary School":
    st.markdown('<div class="section-header">📚 Primary School Detailed View</div>', unsafe_allow_html=True)
    
    primary_df = df[df['Division'] == 'Primary']
    classes = sorted(primary_df['Class'].unique())
    
    # Overall primary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Primary Students", f"{primary_df['Count'].sum():,}")
    with col2:
        pass_rate = ((primary_df[primary_df['Grade'] != 'U']['Count'].sum() / primary_df['Count'].sum()) * 100)
        st.metric("Pass Rate", f"{pass_rate:.1f}%")
    with col3:
        st.metric("Number of Classes", len(classes))
    
    st.markdown("---")
    
    # Chart type selector
    chart_type = st.radio("Select Chart Type:", ['Bar Chart', 'Pie Chart'], horizontal=True)
    chart_type_value = 'bar' if chart_type == 'Bar Chart' else 'pie'
    
    # Individual class charts
    st.subheader("Individual Class Performance")
    cols_per_row = 2
    rows = [classes[i:i+cols_per_row] for i in range(0, len(classes), cols_per_row)]
    
    for row in rows:
        cols = st.columns(len(row))
        for idx, class_name in enumerate(row):
            with cols[idx]:
                class_data = primary_df[primary_df['Class'] == class_name]
                fig = create_distribution_chart(class_data, f"{class_name} Grade Distribution", chart_type_value)
                st.plotly_chart(fig, use_container_width=True)
    
    # Stacked comparison
    st.markdown("---")
    st.subheader("📊 Comparative Analysis - All Primary Classes")
    fig_stacked = create_stacked_comparison(primary_df, classes)
    st.plotly_chart(fig_stacked, use_container_width=True)

# Secondary School Section
elif view_option == "Secondary School":
    st.markdown('<div class="section-header">🎒 Secondary School Detailed View</div>', unsafe_allow_html=True)
    
    secondary_df = df[df['Division'] == 'Secondary']
    classes = sorted(secondary_df['Class'].unique())
    
    # Overall secondary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Secondary Students", f"{secondary_df['Count'].sum():,}")
    with col2:
        pass_rate = ((secondary_df[secondary_df['Grade'] != 'U']['Count'].sum() / secondary_df['Count'].sum()) * 100)
        st.metric("Pass Rate", f"{pass_rate:.1f}%")
    with col3:
        st.metric("Number of Classes", len(classes))
    
    st.markdown("---")
    
    # Chart type selector
    chart_type = st.radio("Select Chart Type:", ['Bar Chart', 'Pie Chart'], horizontal=True)
    chart_type_value = 'bar' if chart_type == 'Bar Chart' else 'pie'
    
    # Individual class charts
    st.subheader("Individual Class Performance")
    cols_per_row = 2
    rows = [classes[i:i+cols_per_row] for i in range(0, len(classes), cols_per_row)]
    
    for row in rows:
        cols = st.columns(len(row))
        for idx, class_name in enumerate(row):
            with cols[idx]:
                class_data = secondary_df[secondary_df['Class'] == class_name]
                fig = create_distribution_chart(class_data, f"{class_name} Grade Distribution", chart_type_value)
                st.plotly_chart(fig, use_container_width=True)
    
    # Stacked comparison
    st.markdown("---")
    st.subheader("📊 Comparative Analysis - All Secondary Classes")
    fig_stacked = create_stacked_comparison(secondary_df, classes)
    st.plotly_chart(fig_stacked, use_container_width=True)

# Data format information
with st.sidebar.expander("ℹ️ Data Format Guide"):
    st.markdown("""
    **Required CSV columns:**
    - `Division`: 'Primary' or 'Secondary'
    - `Class`: Class name (e.g., 'Class 1', 'Class 2')
    - `Grade`: A*, A, B, C, D, E, or U
    - `Count`: Number of students
    
    **Example:**
    ```
    Division,Class,Grade,Count
    Primary,Class 1,A*,5
    Primary,Class 1,A,8
    Secondary,Class 4,B,12
    ```
    """)
