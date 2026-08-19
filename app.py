from __future__ import annotations

from datetime import date, datetime, time
from io import BytesIO
from pathlib import Path
from typing import Iterable

import altair as alt
import openpyxl
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Tennis Booking Analysis",
    page_icon="🎾",
    layout="wide",
)


COLUMN_ALIASES = {
    "Court": ["court", "court name", "court number", "resource", "facility"],
    "Category": [
        "booking category",
        "category",
        "booking type",
        "type",
        "activity",
    ],
    "Date": ["booking date", "date", "start date", "booking day"],
    "Start time": [
        "start time",
        "time of booking",
        "from",
        "time from",
        "booking start",
    ],
    "End time": ["end time", "to", "time to", "booking end"],
    "Duration": ["duration", "duration minutes", "minutes", "length"],
    "Booking type": ["booking type", "recurrence", "repeat type"],
    "Membership status": ["membership status", "member status", "membership"],
}

DEFAULT_WORKBOOK = Path(__file__).with_name("2026 Booking Info.xlsx")
LOGO_PATH = Path(__file__).parent / "assets" / "milfordlogo.png"
ALLOWED_BOOKING_COLUMNS = {
    "date",
    "court(s)",
    "booking category",
    "duration",
    "time of booking",
    "booking type",
    "membership status",
}
COURT_FILTERS = {
    "Court 1": "Court 1 - Astro",
    "Court 2": "Court 2 - Astro",
    "Court 3": "Court 3 - Astro",
    "Court 4": "Court 4 - Clay",
    "Court 5": "Court 5 - Astro",
    "Court 6": "Court 6 - Astro",
    "Court 7": "Court 7 - Clay",
    "Ball Machine": "Ball Machine",
    "Table Tennis": "Table Tennis Table",
}


def apply_portal_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --club-blue: #2f6fae;
            --club-blue-dark: #1f4f7d;
            --club-blue-soft: #eaf2f9;
            --club-ink: #17324a;
        }

        .stApp {
            background: #f6f9fc;
        }

        [data-testid="stHeader"] {
            background: rgba(246, 249, 252, 0.92);
        }

        [data-testid="stSidebar"] {
            background: #eaf2f9;
            border-right: 1px solid #c8daea;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        .portal-hero {
            background: linear-gradient(125deg, #1f4f7d 0%, #2f6fae 58%, #4b88bf 100%);
            border-radius: 18px;
            color: white;
            margin-bottom: 1.25rem;
            padding: 1.6rem 1.9rem;
            box-shadow: 0 10px 28px rgba(31, 79, 125, 0.18);
        }

        .portal-kicker {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin: 0 0 0.35rem;
            opacity: 0.82;
            text-transform: uppercase;
        }

        .portal-hero h1 {
            color: white;
            font-size: clamp(1.8rem, 4vw, 2.65rem);
            line-height: 1.1;
            margin: 0;
        }

        .portal-hero p:last-child {
            font-size: 1rem;
            margin: 0.6rem 0 0;
            opacity: 0.9;
        }

        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #d8e4ef;
            border-radius: 14px;
            min-height: 116px;
            padding: 1rem 1.1rem;
            box-shadow: 0 4px 14px rgba(31, 79, 125, 0.07);
        }

        [data-testid="stMetricValue"] {
            color: var(--club-blue-dark);
        }

        [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        [data-baseweb="tab"] {
            background: #eaf2f9;
            border-radius: 10px 10px 0 0;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }

        [aria-selected="true"][data-baseweb="tab"] {
            background: #d6e7f5;
            color: var(--club-blue-dark);
            font-weight: 700;
        }

        h2, h3 {
            color: var(--club-ink);
        }

        .stButton > button, .stDownloadButton > button {
            background: var(--club-blue);
            border-color: var(--club-blue);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalise_name(value: object) -> str:
    return " ".join(str(value).strip().lower().replace("_", " ").split())


def guess_column(columns: Iterable[object], logical_name: str) -> str | None:
    normalised = {normalise_name(column): str(column) for column in columns}
    for alias in COLUMN_ALIASES[logical_name]:
        if alias in normalised:
            return normalised[alias]
    for alias in COLUMN_ALIASES[logical_name]:
        for cleaned, original in normalised.items():
            if alias in cleaned:
                return original
    return None


@st.cache_data(show_spinner=False)
def workbook_sheets(file_bytes: bytes) -> list[str]:
    """Use openpyxl in read-only mode; never save or modify the uploaded workbook."""
    workbook = openpyxl.load_workbook(
        BytesIO(file_bytes), read_only=True, data_only=True
    )
    try:
        return workbook.sheetnames
    finally:
        workbook.close()


@st.cache_data(show_spinner=False)
def read_sheet(file_bytes: bytes, sheet_name: str, header_row: int) -> pd.DataFrame:
    frame = pd.read_excel(
        BytesIO(file_bytes),
        sheet_name=sheet_name,
        header=header_row - 1,
        engine="openpyxl",
    )
    frame = frame.dropna(how="all").copy()
    frame.columns = [str(column).strip() for column in frame.columns]
    visible_columns = [
        column
        for column in frame.columns
        if normalise_name(column) in ALLOWED_BOOKING_COLUMNS
    ]
    frame = frame.loc[:, visible_columns].copy()
    return frame


def to_date_series(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, errors="coerce").dt.normalize()


def parse_time_value(value: object) -> time | None:
    if pd.isna(value):
        return None
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, (int, float)) and 0 <= float(value) < 1:
        seconds = round(float(value) * 24 * 60 * 60)
        return time((seconds // 3600) % 24, (seconds % 3600) // 60)
    parsed = pd.to_datetime(str(value).strip(), errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.time().replace(second=0, microsecond=0)


def minutes_since_midnight(value: time | None) -> float:
    if value is None or pd.isna(value):
        return float("nan")
    return value.hour * 60 + value.minute


def duration_minutes(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    if isinstance(value, pd.Timedelta):
        return value.total_seconds() / 60
    if isinstance(value, time):
        return value.hour * 60 + value.minute + value.second / 60
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        parsed = pd.to_timedelta(str(value), errors="coerce")
        return parsed.total_seconds() / 60 if not pd.isna(parsed) else float("nan")
    return numeric * 24 * 60 if 0 <= numeric < 1 else numeric


def safe_options(series: pd.Series) -> list[str]:
    return sorted(series.dropna().astype(str).unique().tolist(), key=str.casefold)


def bookings_by_court(
    frame: pd.DataFrame, court_column: str, court_labels: list[str]
) -> pd.Series:
    court_values = frame[court_column].fillna("").astype(str)
    counts = {
        label: int(
            court_values.str.contains(
                COURT_FILTERS[label], case=False, regex=False
            ).sum()
        )
        for label in court_labels
    }
    return pd.Series(counts, name="Bookings", dtype="int64")


def render_booking_chart(values: pd.Series, category_title: str) -> None:
    chart_data = values.rename_axis(category_title).reset_index(name="Bookings")
    x_encoding = alt.X(
        f"{category_title}:N",
        sort=None,
        title=None,
        axis=alt.Axis(
            values=chart_data[category_title].tolist(),
            labelAngle=-35,
            labelLimit=180,
            labelOverlap=False,
        ),
    )
    y_encoding = alt.Y(
        "Bookings:Q",
        title="Bookings",
        scale=alt.Scale(domainMin=0, zero=True, nice=True),
        axis=alt.Axis(minExtent=42),
    )
    base = alt.Chart(chart_data).encode(x=x_encoding, y=y_encoding)
    shadow = base.mark_bar(
        color="#2f618d",
        opacity=0.28,
        xOffset=4,
        yOffset=4,
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6,
    )
    raised_bars = base.mark_bar(
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="#4f8fc6", offset=0),
                alt.GradientStop(color="#78b4df", offset=0.55),
                alt.GradientStop(color="#9bcdef", offset=1),
            ],
            x1=0,
            x2=0,
            y1=1,
            y2=0,
        ),
        stroke="#d8ecfb",
        strokeWidth=1.2,
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6,
    ).encode(
        tooltip=[
                alt.Tooltip(f"{category_title}:N", title=category_title),
                alt.Tooltip("Bookings:Q", format=",d"),
        ]
    )
    chart = (
        (shadow + raised_bars)
        .properties(height=320)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


def main() -> None:
    apply_portal_styles()

    if LOGO_PATH.is_file():
        st.sidebar.image(str(LOGO_PATH), width=118)
    st.sidebar.markdown("### Booking analysis")
    st.sidebar.caption("Milford Tennis & Squash Club")

    logo_column, title_column = st.columns([1, 7], vertical_alignment="center")
    with logo_column:
        if LOGO_PATH.is_file():
            st.image(str(LOGO_PATH), width=112)
    with title_column:
        st.markdown(
            """
            <section class="portal-hero">
                <p class="portal-kicker">Milford Tennis &amp; Squash Club</p>
                <h1>Booking Analytics Portal</h1>
                <p>Explore court demand, booking categories and weekly usage patterns.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )

    if not DEFAULT_WORKBOOK.is_file():
        st.error("The booking workbook is unavailable. Contact the portal administrator.")
        return

    file_bytes = DEFAULT_WORKBOOK.read_bytes()
    try:
        sheets = workbook_sheets(file_bytes)
    except Exception as exc:
        st.error(f"The workbook could not be opened: {exc}")
        return

    sheet_name = sheets[0]
    header_row = 1

    try:
        raw = read_sheet(file_bytes, sheet_name, int(header_row))
    except Exception as exc:
        st.error(f"The worksheet could not be read: {exc}")
        return

    if raw.empty:
        st.warning("This worksheet contains no booking rows.")
        return

    columns = raw.columns.tolist()
    mappings = {
        logical_name: guess_column(columns, logical_name)
        for logical_name in COLUMN_ALIASES
    }

    court_column = mappings["Court"]
    category_column = mappings["Category"]
    date_column = mappings["Date"]
    start_column = mappings["Start time"]
    end_column = mappings["End time"]
    duration_column = mappings["Duration"]
    booking_type_column = mappings["Booking type"]
    membership_status_column = mappings["Membership status"]

    if date_column is None:
        st.warning("A Date column was not found, so date analysis is unavailable.")

    working = raw.copy()
    working["__date"] = (
        to_date_series(working[date_column])
        if date_column
        else pd.Series(pd.NaT, index=working.index)
    )
    working["__weekday"] = working["__date"].dt.day_name()
    working["__start_time"] = (
        working[start_column].map(parse_time_value)
        if start_column
        else pd.Series(None, index=working.index)
    )
    working["__end_time"] = (
        working[end_column].map(parse_time_value)
        if end_column
        else pd.Series(None, index=working.index)
    )
    working["__start_minutes"] = working["__start_time"].map(minutes_since_midnight)
    working["__end_minutes"] = working["__end_time"].map(minutes_since_midnight)
    if end_column is None and start_column and duration_column:
        working["__duration_minutes"] = working[duration_column].map(duration_minutes)
        working["__end_minutes"] = (
            working["__start_minutes"] + working["__duration_minutes"]
        )

    st.sidebar.divider()
    st.sidebar.header("Main Filters")
    filtered = working.copy()

    selected_courts: list[str] = []
    if court_column:
        with st.sidebar.popover(
            "Court", icon=":material/sports_tennis:", width="stretch"
        ):
            chosen_courts = st.pills(
                "Choose courts",
                ["All courts", *COURT_FILTERS],
                selection_mode="multi",
                default=["All courts"],
                width="stretch",
            )
        selected_courts = [
            choice for choice in (chosen_courts or []) if choice != "All courts"
        ]
        if selected_courts:
            court_values = filtered[court_column].fillna("").astype(str)
            court_matches = pd.Series(False, index=filtered.index)
            for choice in selected_courts:
                court_matches |= court_values.str.contains(
                    COURT_FILTERS[choice], case=False, regex=False
                )
            filtered = filtered[court_matches]

    if category_column:
        category_options = safe_options(working[category_column])
        chosen_categories = st.sidebar.multiselect(
            "Booking category",
            ["All categories", *category_options],
            default=["All categories"],
        )
        selected_categories = [
            choice for choice in chosen_categories if choice != "All categories"
        ]
        if selected_categories:
            filtered = filtered[
                filtered[category_column].astype(str).isin(selected_categories)
            ]

    valid_dates = working["__date"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        start_date = st.sidebar.date_input(
            "Start date", value=min_date, min_value=min_date, max_value=max_date
        )
        end_date = st.sidebar.date_input(
            "End date", value=max_date, min_value=min_date, max_value=max_date
        )
        if start_date > end_date:
            st.sidebar.error("Start date must be on or before end date.")
            filtered = filtered.iloc[0:0]
        else:
            filtered = filtered[
                filtered["__date"].between(
                    pd.Timestamp(start_date), pd.Timestamp(end_date), inclusive="both"
                )
            ]

        weekday_order = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ]
        available_days = [day for day in weekday_order if day in working["__weekday"].values]
        chosen_days = st.sidebar.multiselect(
            "Day of week",
            ["All days", *available_days],
            default=["All days"],
        )
        selected_days = [choice for choice in chosen_days if choice != "All days"]
        if selected_days:
            filtered = filtered[filtered["__weekday"].isin(selected_days)]

    st.sidebar.divider()
    st.sidebar.header("Secondary Filters")

    has_start_times = working["__start_time"].notna().any()
    chosen_periods = st.sidebar.multiselect(
        "Time of day",
        ["All time periods", "Morning", "Afternoon", "Evening"],
        default=["All time periods"],
        disabled=not has_start_times,
        help=(
            "Morning: before 12:00. Afternoon: 12:00–17:00. "
            "Evening: after 17:00."
        ),
    )
    selected_periods = [
        choice for choice in chosen_periods if choice != "All time periods"
    ]
    if selected_periods and has_start_times:
        period_matches = pd.Series(False, index=filtered.index)
        if "Morning" in selected_periods:
            period_matches |= filtered["__start_minutes"] < 12 * 60
        if "Afternoon" in selected_periods:
            period_matches |= filtered["__start_minutes"].between(
                12 * 60, 17 * 60, inclusive="both"
            )
        if "Evening" in selected_periods:
            period_matches |= filtered["__start_minutes"] > 17 * 60
        filtered = filtered[period_matches]
    elif not has_start_times:
        st.sidebar.caption("Map a Start time column to enable time-of-day filtering.")

    has_booking_type = booking_type_column is not None
    chosen_booking_types = st.sidebar.multiselect(
        "Booking type",
        ["All booking types", "Individual", "Recurring"],
        default=["All booking types"],
        disabled=not has_booking_type,
    )
    selected_booking_types = [
        choice for choice in chosen_booking_types if choice != "All booking types"
    ]
    if selected_booking_types and booking_type_column:
        filtered = filtered[
            filtered[booking_type_column]
            .fillna("")
            .astype(str)
            .str.casefold()
            .isin([choice.casefold() for choice in selected_booking_types])
        ]
    elif not has_booking_type:
        st.sidebar.caption("Map a Booking type column to enable this filter.")

    has_membership_status = membership_status_column is not None
    chosen_membership_statuses = st.sidebar.multiselect(
        "Membership status",
        [
            "All membership statuses",
            "Active Member",
            "Lapsed Member",
            "Non Member",
        ],
        default=["All membership statuses"],
        disabled=not has_membership_status,
    )
    selected_membership_statuses = [
        choice
        for choice in chosen_membership_statuses
        if choice != "All membership statuses"
    ]
    if selected_membership_statuses and membership_status_column:
        filtered = filtered[
            filtered[membership_status_column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.casefold()
            .isin([choice.casefold() for choice in selected_membership_statuses])
        ]
    elif not has_membership_status:
        st.sidebar.caption(
            "Map a Membership status column to enable this filter."
        )

    court_counts = (
        bookings_by_court(
            filtered,
            court_column,
            selected_courts or list(COURT_FILTERS),
        )
        if court_column
        else pd.Series(dtype="int64")
    )

    dashboard_tab, bookings_tab = st.tabs(["Dashboard", "Bookings"])
    with dashboard_tab:
        metric_one, metric_two, metric_three = st.columns(3)
        metric_one.metric("Total bookings", f"{len(filtered):,}")
        metric_two.metric(
            "Courts in view",
            int(court_counts.gt(0).sum()) if court_column else "—",
        )
        metric_three.metric(
            "Categories in view",
            filtered[category_column].nunique() if category_column else "—",
        )

        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.subheader("Bookings by court")
            if court_column and not filtered.empty and not court_counts.empty:
                render_booking_chart(court_counts, "Court")
            else:
                st.caption("No court data is available for the current selection.")
        with chart_right:
            st.subheader("Bookings by category")
            if category_column and not filtered.empty:
                render_booking_chart(
                    filtered[category_column].astype(str).value_counts(),
                    "Category",
                )
            else:
                st.caption("No category data is available for the current selection.")

        st.subheader("Bookings by weekday")
        if filtered["__weekday"].notna().any():
            weekday_counts = (
                filtered["__weekday"]
                .value_counts()
                .reindex(
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    fill_value=0,
                )
            )
            render_booking_chart(weekday_counts, "Weekday")
        else:
            st.caption("No valid booking dates are available for weekday analysis.")

    with bookings_tab:
        st.subheader("Booking details")
        st.caption(f"Showing {len(filtered):,} of {len(raw):,} bookings")
        display = filtered[raw.columns].copy()
        st.dataframe(display, width="stretch", hide_index=True, height=560)


if __name__ == "__main__":
    main()
