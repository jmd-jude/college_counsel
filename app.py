import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import fetch_school_data, SAMPLE_SCHOOLS

def format_currency(amount):
    if amount is None or amount == 0:
        return "N/A"
    return f"${amount:,.2f}"

def format_percentage(decimal):
    if decimal is None:
        return "N/A"
    return f"{decimal * 100:.1f}%"

def create_demographic_chart(demographics):
    """Create a pie chart for demographic data"""
    labels = []
    values = []
    
    for category, value in demographics.items():
        if value is not None and value > 0:
            labels.append(category)
            values.append(value * 100)
    
    if values:
        fig = px.pie(
            values=values,
            names=labels,
            title="Student Demographics"
        )
        return fig
    return None

def get_school_metrics(school_data):
    latest = school_data.get('latest', {})
    school = school_data.get('school', {})
    
    return {
        "Institution Overview": {
            "Name": school.get('name'),
            "Location": f"{school.get('city', 'N/A')}, {school.get('state', 'N/A')}",
            "Address": school.get('address', 'N/A'),
            "Website": f"https://{school.get('school_url')}" if school.get('school_url') else "N/A",
            "Type": "Public" if school.get('ownership') == 1 else "Private",
            "Carnegie Classification": school.get('carnegie_basic'),
            "Accreditor": school.get('accreditor'),
            "Religious Affiliation": school.get('religious_affiliation', 'None')
        },
        
        "Enrollment & Faculty": {
            "Student Body": {
                "Undergraduate Enrollment": latest.get('student', {}).get('enrollment', {}).get('undergrad_12_month', 'N/A'),
                "Graduate Enrollment": latest.get('student', {}).get('enrollment', {}).get('grad_12_month', 'N/A'),
                "Part-time Share": format_percentage(latest.get('student', {}).get('part_time_share'))
            },
            "Faculty": {
                "Student-Faculty Ratio": f"{latest.get('student', {}).get('demographics', {}).get('student_faculty_ratio')}:1",
                "Full-time Faculty Rate": format_percentage(school.get('ft_faculty_rate')),
                "Faculty Salary": format_currency(school.get('faculty_salary'))
            }
        },
        
        "Demographics": {
            "Gender": {
                "Men": format_percentage(latest.get('student', {}).get('demographics', {}).get('men')),
                "Women": format_percentage(latest.get('student', {}).get('demographics', {}).get('women'))
            },
            "Student Background": {
                "First Generation": format_percentage(latest.get('student', {}).get('share_firstgeneration')),
                "Age 25 or Older": format_percentage(latest.get('student', {}).get('share_25_older')),
                "Average Age at Entry": latest.get('student', {}).get('demographics', {}).get('age_entry'),
                "Median Family Income": format_currency(latest.get('student', {}).get('demographics', {}).get('median_family_income'))
            }
        },
        
        "Cost & Financial Aid": {
            "Direct Costs": {
                "In-State Tuition": format_currency(latest.get('cost', {}).get('tuition', {}).get('in_state')),
                "Out-of-State Tuition": format_currency(latest.get('cost', {}).get('tuition', {}).get('out_of_state')),
                "Room and Board": format_currency(latest.get('cost', {}).get('roomboard', {}).get('oncampus')),
                "Books and Supplies": format_currency(latest.get('cost', {}).get('booksupply'))
            },
            "Net Price": {
                "Average": format_currency(latest.get('cost', {}).get('avg_net_price', {}).get('overall')),
                "Low Income (0-30k)": format_currency(latest.get('cost', {}).get('net_price', {}).get('public', {}).get('by_income_level', {}).get('0-30000')),
                "High Income (75k+)": format_currency(latest.get('cost', {}).get('net_price', {}).get('public', {}).get('by_income_level', {}).get('75000-plus'))
            },
            "Aid & Debt": {
                "Pell Grant Recipients": format_percentage(latest.get('student', {}).get('students_with_pell_grant')),
                "Federal Loan Recipients": format_percentage(latest.get('aid', {}).get('federal_loan_rate')),
                "Median Debt": format_currency(latest.get('aid', {}).get('median_debt', {}).get('completers', {}).get('overall'))
            }
        },
        
        "Student Success": {
            "Retention": {
                "First-year Full-time": format_percentage(latest.get('student', {}).get('retention_rate', {}).get('overall', {}).get('full_time')),
                "First-year Part-time": format_percentage(latest.get('student', {}).get('retention_rate', {}).get('overall', {}).get('part_time'))
            },
            "Graduation": {
                "4-year rate": format_percentage(latest.get('completion', {}).get('completion_rate_4yr_150nt')),
                "6-year rate": format_percentage(latest.get('completion', {}).get('completion_rate_4yr_150nt')),
                "Transfer-out rate": format_percentage(latest.get('completion', {}).get('transfer_rate', {}).get('4yr', {}).get('full_time'))
            }
        },
        
        "Career Outcomes": {
            "Median Earnings": {
                "6 years after entry": format_currency(latest.get('earnings', {}).get('6_yrs_after_entry', {}).get('median')),
                "8 years after entry": format_currency(latest.get('earnings', {}).get('8_yrs_after_entry', {}).get('median_earnings')),
                "10 years after entry": format_currency(latest.get('earnings', {}).get('10_yrs_after_entry', {}).get('median'))
            },
            "Employment": {
                "Earning over $25k/year": format_percentage(latest.get('earnings', {}).get('6_yrs_after_entry', {}).get('percent_greater_than_25000'))
            },
            "Loan Repayment": {
                "1-year rate": format_percentage(latest.get('repayment', {}).get('1_yr', {}).get('rate_suppressed', {}).get('overall')),
                "3-year rate": format_percentage(latest.get('repayment', {}).get('3_yr', {}).get('rate_suppressed', {}).get('overall'))
            }
        }
    }

def main():
    st.set_page_config(page_title="College Metrics Explorer", layout="wide")
    
    # Get cached school data
    schools_data = fetch_school_data()
    
    # Sidebar
    with st.sidebar:
        st.title("College Explorer")
        selected_school = st.selectbox("Select a School", SAMPLE_SCHOOLS)
        st.divider()
        
        # Get data for quick stats
        school_data = schools_data[selected_school]['raw_data']
        latest = school_data.get('latest', {})
        
        st.markdown("### Quick Stats")
        st.metric("Acceptance Rate", 
            format_percentage(latest.get('admissions', {}).get('admission_rate', {}).get('overall')))
        st.metric("Total Enrollment",
            f"{latest.get('student', {}).get('size'):,}")
        st.metric("Median Earnings (10yr)",
            format_currency(latest.get('earnings', {}).get('10_yrs_after_entry', {}).get('median')))
        st.metric("Graduation Rate",
            format_percentage(latest.get('completion', {}).get('completion_rate_4yr_150nt')))
    
    # Get organized metrics
    metrics = get_school_metrics(school_data)
    
    # Main content
    st.title(metrics["Institution Overview"]["Name"])
    st.write(f"_{metrics['Institution Overview']['Location']} • {metrics['Institution Overview']['Type']}_")
    
    # Overview Tab
    overview_tab, costs_tab, outcomes_tab = st.tabs(["Overview", "Costs & Aid", "Outcomes"])
    
    with overview_tab:
        # Basic Info
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Institution Profile")
            for key, value in metrics["Institution Overview"].items():
                if key != "Name":  # Skip name since it's in the title
                    st.write(f"**{key}:** {value}")
            
            st.header("Enrollment")
            enroll = metrics["Enrollment & Faculty"]["Student Body"]
            st.metric("Total Enrollment", 
                     f"{int(enroll['Undergraduate Enrollment']) + int(enroll['Graduate Enrollment']):,}")
            st.write(f"**Undergraduate:** {int(enroll['Undergraduate Enrollment']):,}")
            st.write(f"**Graduate:** {int(enroll['Graduate Enrollment']):,}")
            st.write(f"**Part-time Share:** {enroll['Part-time Share']}")
        
        with col2:
            st.header("Student Demographics")
            demo = metrics["Demographics"]
            
            # Gender distribution pie chart
            gender_data = {
                'Category': ['Men', 'Women'],
                'Percentage': [
                    float(demo['Gender']['Men'].rstrip('%')),
                    float(demo['Gender']['Women'].rstrip('%'))
                ]
            }
            fig = px.pie(gender_data, values='Percentage', names='Category', title='Gender Distribution')
            st.plotly_chart(fig)
            
            st.write("**Student Background**")
            bg = demo["Student Background"]
            st.write(f"First Generation: {bg['First Generation']}")
            st.write(f"Age 25 or Older: {bg['Age 25 or Older']}")
            st.write(f"Average Age at Entry: {bg['Average Age at Entry']}")
            st.write(f"Median Family Income: {bg['Median Family Income']}")
    
    with costs_tab:
        cost_col1, cost_col2 = st.columns(2)
        
        with cost_col1:
            st.header("Annual Costs")
            for category, amount in metrics["Cost & Financial Aid"]["Direct Costs"].items():
                st.metric(category, amount)
        
        with cost_col2:
            st.header("Financial Aid")
            aid = metrics["Cost & Financial Aid"]["Aid & Debt"]
            st.metric("Pell Grant Recipients", aid["Pell Grant Recipients"])
            st.metric("Federal Loan Recipients", aid["Federal Loan Recipients"])
            
            st.subheader("Net Price by Income")
            net = metrics["Cost & Financial Aid"]["Net Price"]
            st.write(f"**Low Income (0-30k):** {net['Low Income (0-30k)']}")
            st.write(f"**High Income (75k+):** {net['High Income (75k+)']}")
    
    with outcomes_tab:
        outcome_col1, outcome_col2 = st.columns(2)
        
        with outcome_col1:
            st.header("Student Success")
            success = metrics["Student Success"]
            st.metric("Retention Rate", success["Retention"]["First-year Full-time"])
            st.metric("4-year Graduation Rate", success["Graduation"]["4-year rate"])
            st.metric("6-year Graduation Rate", success["Graduation"]["6-year rate"])
        
        with outcome_col2:
            st.header("Career Outcomes")
            earnings = metrics["Career Outcomes"]["Median Earnings"]
            
            # Create earnings progression chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[6, 8, 10],
                y=[float(earnings['6 years after entry'].replace('$','').replace(',','')), 
                   float(earnings['8 years after entry'].replace('$','').replace(',','')),
                   float(earnings['10 years after entry'].replace('$','').replace(',',''))],
                mode='lines+markers'
            ))
            fig.update_layout(
                title="Earnings Progression",
                xaxis_title="Years after entry",
                yaxis_title="Median Earnings ($)"
            )
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()