import requests
import pandas as pd
import streamlit as st


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Support Ticket Assistant",
    page_icon="🤖",
    layout="wide"
)


# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown(
    """
    <style>

    /* =================================================
       MAIN PAGE
       ================================================= */

    .main {
        background-color: #f7f9fc;
    }


    /* =================================================
       HERO SECTION
       ================================================= */

    .hero {
        padding: 32px;
        border-radius: 18px;
        margin-bottom: 28px;
        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );
        color: white;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }

    .hero h1 {
        margin: 0 0 10px 0;
        font-size: 34px;
        font-weight: 700;
        color: white;
    }

    .hero p {
        margin: 0;
        font-size: 16px;
        color: #d1d5db;
        line-height: 1.6;
    }


    /* =================================================
       SECTION TITLES
       ================================================= */

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin-top: 18px;
        margin-bottom: 12px;
    }


    /* =================================================
       FOOTER
       ================================================= */

    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 13px;
        padding: 20px 0 10px 0;
    }


    /* =================================================
       SIDEBAR
       ================================================= */

    [data-testid="stSidebar"] h2 {
        font-size: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# CONFIGURATION
# =====================================================

API_URL = "http://127.0.0.1:8000"


# =====================================================
# SESSION STATE
# =====================================================

if "question" not in st.session_state:
    st.session_state["question"] = ""


# =====================================================
# HERO HEADER
# =====================================================

st.html(
    """
    <div class="hero">
        <h1>🤖 AI Support Ticket Assistant</h1>

        <p>
            Ask natural-language questions about support tickets,
            performance, customer ratings, and anomalies.
        </p>
    </div>
    """
)


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("Example Questions")

    example_questions = [
        "How many tickets are currently open?",
        "Which agent resolved the most tickets this month?",
        "What is the average customer rating for Technical tickets?",
        "Show me all Critical tickets not resolved within 12 hours.",
        "Are there any anomalies in resolution times this week?"
    ]

    for example in example_questions:

        if st.button(
            example,
            width="stretch"
        ):
            st.session_state["question"] = example


# =====================================================
# API HEALTH CHECK
# =====================================================

try:

    health_response = requests.get(
        f"{API_URL}/health",
        timeout=5
    )

    if health_response.status_code == 200:

        st.sidebar.success(
            "API Connected"
        )

    else:

        st.sidebar.warning(
            "API returned an unexpected status."
        )

except requests.RequestException:

    st.sidebar.error(
        "API is not reachable."
    )


# =====================================================
# QUESTION INPUT
# =====================================================

st.markdown(
    '<div class="section-title">Ask the AI Assistant</div>',
    unsafe_allow_html=True
)

question = st.text_input(
    "Question",
    key="question",
    placeholder="Example: How many tickets are currently open?",
    label_visibility="collapsed"
)


# =====================================================
# ASK AI BUTTON
# =====================================================

ask_button = st.button(
    "Ask AI",
    type="primary",
    width="stretch"
)


# =====================================================
# PROCESS QUESTION
# =====================================================

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Analyzing your question..."
        ):

            try:

                # =================================================
                # CALL FASTAPI
                # =================================================

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question
                    },
                    timeout=90
                )

                response.raise_for_status()

                data = response.json()

                result = data.get(
                    "result"
                )

                query_plan = data.get(
                    "query_plan",
                    {}
                )

                operation = query_plan.get(
                    "operation"
                )

                time_period = query_plan.get(
                    "time_period",
                    "all_time"
                )

                filters = query_plan.get(
                    "filters",
                    {}
                )


                # =================================================
                # RESULT: ANOMALY DETECTION
                # =================================================

                if operation == "anomaly_resolution_time":

                    st.markdown(
                        '<div class="section-title">'
                        '🔎 Anomaly Detection Results'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    if isinstance(result, dict):

                        anomaly_count = result.get(
                            "anomaly_count",
                            0
                        )

                        upper_bound = result.get(
                            "upper_bound_hrs"
                        )

                        period_start = result.get(
                            "period_start"
                        )

                        period_end = result.get(
                            "period_end"
                        )

                        q1 = result.get(
                            "q1"
                        )

                        q3 = result.get(
                            "q3"
                        )


                        # -----------------------------------------
                        # METRICS
                        # -----------------------------------------

                        col1, col2, col3 = st.columns(3)

                        with col1:

                            st.metric(
                                "Anomalies Detected",
                                anomaly_count
                            )


                        with col2:

                            if upper_bound is not None:

                                st.metric(
                                    "IQR Upper Bound",
                                    f"{upper_bound} hrs"
                                )

                            else:

                                st.metric(
                                    "IQR Upper Bound",
                                    "N/A"
                                )


                        with col3:

                            st.metric(
                                "Detection Method",
                                "IQR"
                            )


                        # -----------------------------------------
                        # ANALYSIS PERIOD
                        # -----------------------------------------

                        if period_start and period_end:

                            st.info(
                                f"📅 Analysis period: "
                                f"{period_start} → {period_end}"
                            )


                        # -----------------------------------------
                        # IQR INFORMATION
                        # -----------------------------------------

                        if (
                            q1 is not None
                            and q3 is not None
                        ):

                            st.caption(
                                f"IQR statistics: "
                                f"Q1 = {q1} hrs | "
                                f"Q3 = {q3} hrs"
                            )


                        # -----------------------------------------
                        # ANOMALY TABLE
                        # -----------------------------------------

                        anomalies = result.get(
                            "anomalies",
                            []
                        )

                        if anomalies:

                            st.markdown(
                                '<div class="section-title">'
                                'Detected Anomalies'
                                '</div>',
                                unsafe_allow_html=True
                            )

                            anomaly_df = pd.DataFrame(
                                anomalies
                            )


                            display_columns = [
                                "ticket_id",
                                "created_at",
                                "category",
                                "priority",
                                "status",
                                "resolution_time_hrs",
                                "agent_id",
                                "issue_summary"
                            ]


                            anomaly_df = anomaly_df[
                                [
                                    column
                                    for column in display_columns
                                    if column in anomaly_df.columns
                                ]
                            ]


                            anomaly_df = anomaly_df.rename(
                                columns={
                                    "ticket_id": "Ticket ID",
                                    "created_at": "Created At",
                                    "category": "Category",
                                    "priority": "Priority",
                                    "status": "Status",
                                    "resolution_time_hrs": "Resolution Time (hrs)",
                                    "agent_id": "Agent",
                                    "issue_summary": "Issue"
                                }
                            )


                            st.dataframe(
                                anomaly_df,
                                width="stretch",
                                hide_index=True
                            )

                        else:

                            st.success(
                                "No resolution-time anomalies "
                                "were detected in the analysis period."
                            )


                # =================================================
                # RESULT: CRITICAL UNRESOLVED
                # =================================================

                elif operation == "critical_unresolved":

                    st.markdown(
                        '<div class="section-title">'
                        '🚨 Critical Tickets Requiring Attention'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    if isinstance(result, list):

                        st.metric(
                            "Tickets Found",
                            len(result)
                        )

                        if result:

                            critical_df = pd.DataFrame(
                                result
                            )


                            critical_df = critical_df.rename(
                                columns={
                                    "ticket_id": "Ticket ID",
                                    "created_at": "Created At",
                                    "priority": "Priority",
                                    "status": "Status",
                                    "resolution_time_hrs": "Resolution Time (hrs)",
                                    "agent_id": "Agent",
                                    "issue_summary": "Issue"
                                }
                            )


                            if "Resolution Time (hrs)" in critical_df.columns:

                                critical_df[
                                    "Resolution Time (hrs)"
                                ] = critical_df[
                                    "Resolution Time (hrs)"
                                ].fillna(
                                    "Not Resolved"
                                )


                            st.dataframe(
                                critical_df,
                                width="stretch",
                                hide_index=True
                            )

                        else:

                            st.success(
                                "No critical tickets exceeded "
                                "the 12-hour resolution rule."
                            )


                # =================================================
                # RESULT: AGENT PERFORMANCE
                # =================================================

                elif operation == "resolved_by_agent":

                    st.markdown(
                        '<div class="section-title">'
                        '👥 Resolved Tickets by Agent'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    if isinstance(result, dict):

                        agent_df = pd.DataFrame(
                            list(result.items()),
                            columns=[
                                "Agent",
                                "Resolved Tickets"
                            ]
                        )


                        agent_df = agent_df.sort_values(
                            "Resolved Tickets",
                            ascending=False
                        ).reset_index(
                            drop=True
                        )


                        # -----------------------------------------
                        # TOP AGENT INFORMATION
                        # -----------------------------------------

                        if not agent_df.empty:

                            top_agent = agent_df.iloc[0]

                            st.info(
                                f"Highest resolved-ticket count "
                                f"in the returned results: "
                                f"{top_agent['Agent']} "
                                f"({top_agent['Resolved Tickets']} tickets)"
                            )


                        st.dataframe(
                            agent_df,
                            width="stretch",
                            hide_index=True
                        )


                # =================================================
                # RESULT: RATING BY CATEGORY
                # =================================================

                elif operation == "rating_by_category":

                    st.markdown(
                        '<div class="section-title">'
                        '⭐ Average Customer Rating by Category'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    if isinstance(result, dict):

                        rating_df = pd.DataFrame(
                            list(result.items()),
                            columns=[
                                "Category",
                                "Average Rating"
                            ]
                        )


                        rating_df = rating_df.sort_values(
                            "Average Rating",
                            ascending=False
                        ).reset_index(
                            drop=True
                        )


                        st.dataframe(
                            rating_df,
                            width="stretch",
                            hide_index=True
                        )


                # =================================================
                # RESULT: SUMMARY
                # =================================================

                elif operation == "summary":

                    st.markdown(
                        '<div class="section-title">'
                        '📊 Support Ticket Overview'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    if isinstance(result, dict):

                        total_tickets = result.get(
                            "total_tickets",
                            0
                        )

                        resolved = result.get(
                            "resolved",
                            0
                        )

                        open_tickets = result.get(
                            "open",
                            0
                        )

                        escalated = result.get(
                            "escalated",
                            0
                        )

                        avg_response = result.get(
                            "average_response_time_hrs"
                        )

                        avg_resolution = result.get(
                            "average_resolution_time_hrs"
                        )

                        avg_rating = result.get(
                            "average_customer_rating"
                        )


                        # -----------------------------------------
                        # TICKET COUNTS
                        # -----------------------------------------

                        col1, col2, col3, col4 = st.columns(4)


                        with col1:

                            st.metric(
                                "Total Tickets",
                                total_tickets
                            )


                        with col2:

                            st.metric(
                                "Resolved",
                                resolved
                            )


                        with col3:

                            st.metric(
                                "Open",
                                open_tickets
                            )


                        with col4:

                            st.metric(
                                "Escalated",
                                escalated
                            )


                        # -----------------------------------------
                        # PERFORMANCE METRICS
                        # -----------------------------------------

                        st.markdown(
                            '<div class="section-title">'
                            'Performance Metrics'
                            '</div>',
                            unsafe_allow_html=True
                        )


                        col1, col2, col3 = st.columns(3)


                        with col1:

                            st.metric(
                                "Avg Response Time",
                                f"{avg_response} hrs"
                                if avg_response is not None
                                else "N/A"
                            )


                        with col2:

                            st.metric(
                                "Avg Resolution Time",
                                f"{avg_resolution} hrs"
                                if avg_resolution is not None
                                else "N/A"
                            )


                        with col3:

                            st.metric(
                                "Avg Customer Rating",
                                avg_rating
                                if avg_rating is not None
                                else "N/A"
                            )


                # =================================================
                # RESULT: STANDARD NUMERIC
                # =================================================

                elif isinstance(
                    result,
                    (int, float)
                ):

                    st.markdown(
                        '<div class="section-title">'
                        '📌 AI Result'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.metric(
                        "Result",
                        result
                    )


                # =================================================
                # RESULT: STANDARD DICTIONARY
                # =================================================

                elif isinstance(
                    result,
                    dict
                ):

                    st.markdown(
                        '<div class="section-title">'
                        '📌 AI Result'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.json(
                        result
                    )


                # =================================================
                # RESULT: STANDARD LIST
                # =================================================

                elif isinstance(
                    result,
                    list
                ):

                    st.markdown(
                        '<div class="section-title">'
                        '📋 AI Result'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    if result:

                        result_df = pd.DataFrame(
                            result
                        )


                        st.dataframe(
                            result_df,
                            width="stretch",
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No matching records found."
                        )


                # =================================================
                # QUERY DETAILS
                # =================================================

                st.markdown("---")

                with st.expander(
                    "🔍 Query Details"
                ):

                    st.write(
                        "**Operation:**",
                        operation
                    )

                    st.write(
                        "**Time Period:**",
                        time_period
                    )


                    active_filters = {
                        key: value
                        for key, value in filters.items()
                        if value is not None
                    }


                    if active_filters:

                        st.write(
                            "**Filters:**",
                            active_filters
                        )

                    else:

                        st.write(
                            "**Filters:** None"
                        )


            # =================================================
            # HTTP ERROR
            # =================================================

            except requests.HTTPError as error:

                st.error(
                    f"API request failed: {error}"
                )

                try:

                    error_details = response.json()

                    st.code(
                        str(error_details)
                    )

                except Exception:

                    pass


            # =================================================
            # CONNECTION ERROR
            # =================================================

            except requests.RequestException as error:

                st.error(
                    f"Could not connect to the API: {error}"
                )


            # =================================================
            # GENERAL ERROR
            # =================================================

            except Exception as error:

                st.error(
                    f"An unexpected error occurred: {error}"
                )


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    """
    <hr>

    <div class="footer">
        AI Support Ticket Assistant
        · FastAPI
        · Streamlit
        · Pandas
        · Local LLM
    </div>
    """,
    unsafe_allow_html=True
)