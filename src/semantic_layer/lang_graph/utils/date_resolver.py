from datetime import datetime, timedelta


def resolve_relative_period(
    period: str | None,
    n_days: int | None = None,
) -> tuple[str | None, str | None]:
    
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')

    if not period or period == "all_time":
        return None, None

    match period:
        case "last_7_days":
            return (today - timedelta(days=7)).strftime('%Y-%m-%d'), today_str

        case "last_30_days":
            return (today - timedelta(days=30)).strftime('%Y-%m-%d'), today_str

        case "last_90_days":
            return (today - timedelta(days=90)).strftime('%Y-%m-%d'), today_str

        case "this_month":
            return today.replace(day=1).strftime('%Y-%m-%d'), today_str

        case "last_month":
            first_this_month = today.replace(day=1)
            last_month_end = first_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d')

        case "this_year":
            return f"{today.year}-01-01", today_str

        case "last_year":
            return f"{today.year - 1}-01-01", f"{today.year - 1}-12-31"

        case "ytd":
            return f"{today.year}-01-01", today_str

        case "custom_days":
            if not n_days or n_days <= 0:
                return (today - timedelta(days=30)).strftime('%Y-%m-%d'), today_str
            return (today - timedelta(days=n_days)).strftime('%Y-%m-%d'), today_str

        case _:
            # Fallback → current month
            return today.replace(day=1).strftime('%Y-%m-%d'), today_str