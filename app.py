import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.database.mongo_operations import MongoDBClient
from src.api.openai_client import NutritionAPI
from utils.food_parser import extract_portion_info
from config import DEFAULT_CALORIE_GOAL
import pandas as pd
import calendar


def date_selection_ui():
    """Enhanced date selection UI with better UX and visual feedback"""
    st.sidebar.header("Date Selection")

    # Tab-based date selection for better UX
    date_tab, month_tab = st.sidebar.tabs(["Daily View", "Monthly View"])

    with date_tab:
        # Calendar-based date picker with default to today
        selected_date = st.date_input(
            "Select Date", datetime.now(), key="daily_date_picker"
        )
        # Show selected date in user-friendly format
        st.caption(f"Viewing data for: {selected_date.strftime('%A, %B %d, %Y')}")

    with month_tab:
        # More intuitive month selection
        current_year = datetime.now().year
        col1, col2 = st.columns(2)

        with col1:
            selected_month = st.selectbox(
                "Month",
                range(1, 13),
                index=datetime.now().month - 1,
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                key="month_select",
            )

        with col2:
            selected_year = st.selectbox(
                "Year",
                range(current_year - 2, current_year + 1),
                index=2,
                key="year_select",
            )

        # Display calendar for selected month
        cal = calendar.monthcalendar(selected_year, selected_month)
        st.caption(
            f"Viewing data for: {datetime(selected_year, selected_month, 1).strftime('%B %Y')}"
        )

        # Simple calendar visualization
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        st.markdown("### Calendar")
        cols = st.columns(7)
        for i, day in enumerate(days):
            cols[i].markdown(f"**{day}**")

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    cols[i].markdown(f"{day}")
                else:
                    cols[i].markdown("")

    return selected_date, selected_month, selected_year


def create_macronutrient_chart(daily_entries):
    """Create an improved macronutrient distribution chart"""
    total_protein = sum(e["nutrition"].get("protein", 0) for e in daily_entries)
    total_carbs = sum(e["nutrition"].get("carbs", 0) for e in daily_entries)
    total_fat = sum(e["nutrition"].get("fat", 0) for e in daily_entries)

    # Calculate caloric values
    protein_cals = total_protein * 4
    carbs_cals = total_carbs * 4
    fat_cals = total_fat * 9
    total_cals = protein_cals + carbs_cals + fat_cals

    # Create percentages for better visualization
    if total_cals > 0:
        protein_pct = round((protein_cals / total_cals) * 100)
        carbs_pct = round((carbs_cals / total_cals) * 100)
        fat_pct = round((fat_cals / total_cals) * 100)
    else:
        protein_pct, carbs_pct, fat_pct = 0, 0, 0

    fig = px.pie(
        names=["Protein", "Carbs", "Fat"],
        values=[protein_cals, carbs_cals, fat_cals],
        title="Macronutrient Distribution",
        hole=0.4,
        color_discrete_sequence=["#2dd4bf", "#f59e42", "#ef4444"],  # Teal, Amber, Red
    )

    # Add text annotations
    fig.update_traces(
        textinfo="percent+label",
        textposition="inside",
        hovertemplate="<b>%{label}</b><br>%{value:.0f} calories<br>%{percent}<extra></extra>",
    )

    # Add nutrient values in grams
    fig.add_annotation(
        text=f"Protein: {total_protein:.1f}g<br>Carbs: {total_carbs:.1f}g<br>Fat: {total_fat:.1f}g<br>Total: {total_cals:.0f} cal",
        x=0.5,
        y=0.5,
        font_size=12,
        showarrow=False,
    )

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.1),
        margin=dict(t=50, b=20, l=20, r=20),
    )

    return fig


def create_calorie_timeline(daily_entries):
    """Create an improved calorie intake timeline"""
    if not daily_entries:
        return None

    # Sort entries by timestamp
    sorted_entries = sorted(daily_entries, key=lambda x: x["timestamp"])

    timeline_data = []
    cumulative_calories = 0

    for e in sorted_entries:
        meal_calories = e["nutrition"].get("calories", 0)
        cumulative_calories += meal_calories

        timeline_data.append(
            {
                "Time": e["timestamp"].strftime("%H:%M"),
                "Calories": meal_calories,
                "Cumulative": cumulative_calories,
                "Meal": e["food_item"],
            }
        )

    # Create dual-axis chart: bar for individual meals, line for cumulative
    fig = go.Figure()

    # Add individual meal bars
    fig.add_trace(
        go.Bar(
            x=[d["Time"] for d in timeline_data],
            y=[d["Calories"] for d in timeline_data],
            text=[d["Meal"] for d in timeline_data],
            name="Meal Calories",
            marker_color="rgb(55, 83, 109)",
            hovertemplate="<b>%{text}</b><br>%{y:.0f} calories<br>%{x}<extra></extra>",
        )
    )

    # Add cumulative line
    fig.add_trace(
        go.Scatter(
            x=[d["Time"] for d in timeline_data],
            y=[d["Cumulative"] for d in timeline_data],
            mode="lines+markers",
            name="Cumulative Intake",
            line=dict(color="firebrick", width=3),
            marker=dict(size=8),
            hovertemplate="<b>Total calories</b><br>%{y:.0f} calories<br>as of %{x}<extra></extra>",
        )
    )

    # Add goal line
    fig.add_shape(
        type="line",
        x0=timeline_data[0]["Time"],
        y0=DEFAULT_CALORIE_GOAL,
        x1=timeline_data[-1]["Time"],
        y1=DEFAULT_CALORIE_GOAL,
        line=dict(
            color="green",
            width=2,
            dash="dash",
        ),
        name="Daily Goal",
    )

    # Add goal annotation
    fig.add_annotation(
        x=timeline_data[-1]["Time"],
        y=DEFAULT_CALORIE_GOAL,
        text=f"Daily Goal ({DEFAULT_CALORIE_GOAL} cal)",
        showarrow=False,
        yshift=10,
        font=dict(color="green"),
    )

    fig.update_layout(
        title="Calorie Intake Timeline",
        xaxis_title="Time",
        yaxis_title="Calories",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        hovermode="x unified",
        margin=dict(t=50, b=70),
    )

    return fig


def create_monthly_trend_chart(monthly_data):
    """Create an improved monthly trend chart"""
    if not monthly_data:
        return None

    df = pd.DataFrame(
        [
            {
                "Date": entry["_id"],
                "Calories": entry["total_calories"],
                "Protein": entry["total_protein"],
                "Carbs": entry["total_carbs"],
                "Fat": entry["total_fat"],
            }
            for entry in monthly_data
        ]
    )

    # Sort by date
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    fig = px.line(
        df, x="Date", y="Calories", title="Daily Calorie Intake", markers=True
    )

    # Add goal line
    fig.add_shape(
        type="line",
        x0=df["Date"].min(),
        y0=DEFAULT_CALORIE_GOAL,
        x1=df["Date"].max(),
        y1=DEFAULT_CALORIE_GOAL,
        line=dict(
            color="green",
            width=2,
            dash="dash",
        ),
    )

    # Add goal annotation
    fig.add_annotation(
        x=df["Date"].max(),
        y=DEFAULT_CALORIE_GOAL,
        text=f"Daily Goal ({DEFAULT_CALORIE_GOAL} cal)",
        showarrow=False,
        yshift=10,
        font=dict(color="green"),
    )

    # Calculate 7-day moving average
    if len(df) >= 7:
        df["MA7"] = df["Calories"].rolling(window=7).mean()

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df["MA7"],
                mode="lines",
                name="7-day Average",
                line=dict(color="purple", width=2),
            )
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Calories",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=50, b=70, l=40, r=40),
    )

    return fig


def display_food_log(daily_entries):
    """Display an enhanced food log with better formatting"""
    if not daily_entries:
        st.info("No food entries for today")
        return

    display_data = [
        {
            "Time": e["timestamp"].strftime("%H:%M"),
            "Food": e["food_item"],
            "Quantity": f"{e['quantity']} {e.get('unit', '')}",
            "Calories": int(e["nutrition"].get("calories", 0)),
            "Protein": f"{e['nutrition'].get('protein', 0):.1f}g",
            "Carbs": f"{e['nutrition'].get('carbs', 0):.1f}g",
            "Fat": f"{e['nutrition'].get('fat', 0):.1f}g",
        }
        for e in daily_entries
    ]

    # Sort by time
    display_data = sorted(display_data, key=lambda x: x["Time"])

    # Calculate totals for the day
    total_calories = sum(e["nutrition"].get("calories", 0) for e in daily_entries)
    total_protein = sum(e["nutrition"].get("protein", 0) for e in daily_entries)
    total_carbs = sum(e["nutrition"].get("carbs", 0) for e in daily_entries)
    total_fat = sum(e["nutrition"].get("fat", 0) for e in daily_entries)

    # Show dataframe with better styling
    st.dataframe(display_data, use_container_width=True, hide_index=True)

    # Show totals in a visually distinct way
    st.markdown("### Daily Totals")
    totals_col1, totals_col2, totals_col3, totals_col4 = st.columns(4)

    with totals_col1:
        st.metric("Total Calories", f"{int(total_calories)}")
    with totals_col2:
        st.metric("Total Protein", f"{total_protein:.1f}g")
    with totals_col3:
        st.metric("Total Carbs", f"{total_carbs:.1f}g")
    with totals_col4:
        st.metric("Total Fat", f"{total_fat:.1f}g")


def main():
    st.set_page_config(
        page_title="NutriTrack AI", layout="wide", initial_sidebar_state="expanded"
    )

    # Load custom CSS for better styling
    st.markdown(
        """
<style>
.main-header {
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
.subheader {
    font-size: 1.5rem;
    margin-top: 2rem;
}
.metric-container {
    padding: 1rem;
    border-radius: 0.5rem;
}
.stMetric {
    padding: 0.5rem;
    border-radius: 0.25rem;
}
</style>
""",
        unsafe_allow_html=True,
    )

    mongo = MongoDBClient()
    nutrition_service = NutritionAPI()

    # Initialize session state for user identification
    if "user_id" not in st.session_state:
        st.session_state.user_id = "demo_user"

    # Sidebar controls
    with st.sidebar:
        st.header("Log Food Entry")
        food_input = st.text_input(
            "Describe your meal:", placeholder="e.g., 2 cups of oatmeal with berries"
        )

        # Add meal type selection for better categorization
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

        if st.button("Log Meal", type="primary"):
            if food_input:
                with st.spinner("Analyzing nutrition data..."):
                    # Parse food input to extract name, quantity, and unit
                    food_name, quantity, unit = extract_portion_info(food_input)

                    # Get nutrition info from the NutritionAPI
                    nutrition_data = nutrition_service.get_nutrition_info(food_input)

                    if nutrition_data:
                        # Construct the entry with nutrition data
                        entry = {
                            "user_id": st.session_state.user_id,
                            "food_item": food_name,
                            "quantity": quantity or 1,
                            "unit": unit or "portion",
                            "meal_type": meal_type,
                            "nutrition": {
                                "calories": nutrition_data.get("calories", 0),
                                "protein": nutrition_data.get("protein", 0),
                                "carbs": nutrition_data.get("carbohydrates", 0),
                                "fat": nutrition_data.get("fat", 0),
                                "fiber": nutrition_data.get("fiber", 0),
                                "sugar": nutrition_data.get("sugar", 0),
                            },
                            "timestamp": datetime.now(),
                        }

                        if mongo.insert_food_entry(st.session_state.user_id, entry):
                            st.success("Meal logged successfully!")
                        else:
                            st.error("Failed to save meal entry")
                    else:
                        st.error("Could not estimate nutrition data")

        # Add date selection UI to sidebar
        selected_date, selected_month, selected_year = date_selection_ui()

    # Main dashboard content
    st.markdown(
        '<h1 class="main-header">NutriTrack AI Dashboard</h1>', unsafe_allow_html=True
    )

    # Daily metrics
    daily_entries = mongo.get_daily_entries(st.session_state.user_id, selected_date)

    # Display daily progress with improved metrics
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.subheader("Daily Nutrition Progress")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        # Create calorie progress bar
        consumed_calories = sum(e["nutrition"]["calories"] for e in daily_entries)
        remaining_calories = DEFAULT_CALORIE_GOAL - consumed_calories
        progress_percentage = min(
            100, int((consumed_calories / DEFAULT_CALORIE_GOAL) * 100)
        )

        st.markdown(f"### Calorie Progress: {progress_percentage}%")
        st.progress(progress_percentage / 100)

        calorie_col1, calorie_col2, calorie_col3 = st.columns(3)
        with calorie_col1:
            st.metric("Goal", DEFAULT_CALORIE_GOAL)
        with calorie_col2:
            st.metric("Consumed", int(consumed_calories))
        with calorie_col3:
            st.metric("Remaining", int(remaining_calories), delta_color="inverse")

    with col3:
        # Macronutrient metrics
        protein = sum(e["nutrition"]["protein"] for e in daily_entries)
        carbs = sum(e["nutrition"]["carbs"] for e in daily_entries)
        fat = sum(e["nutrition"]["fat"] for e in daily_entries)

        macro_col1, macro_col2, macro_col3 = st.columns(3)
        with macro_col1:
            st.metric("Protein", f"{protein:.1f}g", f"{(protein * 4):.0f} cal")
        with macro_col2:
            st.metric("Carbs", f"{carbs:.1f}g", f"{(carbs * 4):.0f} cal")
        with macro_col3:
            st.metric("Fat", f"{fat:.1f}g", f"{(fat * 9):.0f} cal")

    st.markdown("</div>", unsafe_allow_html=True)

    # Create tabs for different views
    daily_tab, monthly_tab = st.tabs(["Daily View", "Monthly View"])

    with daily_tab:
        if daily_entries:
            # Create two columns for charts
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.markdown(
                    '<h3 class="subheader">Macronutrient Distribution</h3>',
                    unsafe_allow_html=True,
                )
                macro_fig = create_macronutrient_chart(daily_entries)
                st.plotly_chart(macro_fig, use_container_width=True)

            with chart_col2:
                st.markdown(
                    '<h3 class="subheader">Calorie Intake Timeline</h3>',
                    unsafe_allow_html=True,
                )
                timeline_fig = create_calorie_timeline(daily_entries)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    st.info("No timeline data available")

            # Display food log
            st.markdown(
                '<h3 class="subheader">Today\'s Food Log</h3>', unsafe_allow_html=True
            )
            display_food_log(daily_entries)
        else:
            st.info(f"No food entries for {selected_date.strftime('%A, %B %d')}")
            st.markdown("""
            #### Tips for getting started:
            1. Use the sidebar to log your meals
            2. Be as specific as possible with portion sizes
            3. Track all your meals and snacks for accurate reporting
            """)

    with monthly_tab:
        st.markdown(
            f'<h3 class="subheader">Monthly Analysis: {datetime(selected_year, selected_month, 1).strftime("%B %Y")}</h3>',
            unsafe_allow_html=True,
        )

        monthly_data = mongo.get_monthly_summary(
            st.session_state.user_id, selected_year, selected_month
        )

        if monthly_data:
            # Create monthly trend chart
            monthly_fig = create_monthly_trend_chart(monthly_data)
            if monthly_fig:
                st.plotly_chart(monthly_fig, use_container_width=True)

            # Calculate monthly averages
            df = pd.DataFrame(
                [
                    {
                        "Date": entry["_id"],
                        "Calories": entry["total_calories"],
                        "Protein": entry["total_protein"],
                        "Carbs": entry["total_carbs"],
                        "Fat": entry["total_fat"],
                    }
                    for entry in monthly_data
                ]
            )

            # Monthly statistics
            st.markdown(
                '<h3 class="subheader">Monthly Statistics</h3>', unsafe_allow_html=True
            )
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:
                st.metric("Avg. Daily Calories", f"{df['Calories'].mean():.0f}")
            with stat_col2:
                st.metric("Avg. Daily Protein", f"{df['Protein'].mean():.1f}g")
            with stat_col3:
                st.metric("Avg. Daily Carbs", f"{df['Carbs'].mean():.1f}g")
            with stat_col4:
                st.metric("Avg. Daily Fat", f"{df['Fat'].mean():.1f}g")

            # Provide additional insights
            days_over_goal = len(df[df["Calories"] > DEFAULT_CALORIE_GOAL])
            days_under_goal = len(df[df["Calories"] <= DEFAULT_CALORIE_GOAL])

            st.markdown(f"""
            ### Monthly Insights
            - You tracked nutrition for **{len(df)}** days this month
            - You were under your calorie goal on **{days_under_goal}** days
            - You were over your calorie goal on **{days_over_goal}** days
            - Your highest calorie day was **{df["Calories"].max():.0f}** calories
            - Your lowest calorie day was **{df["Calories"].min():.0f}** calories
            """)

            # Display monthly data table
            with st.expander("View Monthly Data Table"):
                st.dataframe(
                    df.sort_values("Date"), use_container_width=True, hide_index=True
                )
        else:
            st.info(
                f"No data available for {datetime(selected_year, selected_month, 1).strftime('%B %Y')}"
            )


if __name__ == "__main__":
    main()
