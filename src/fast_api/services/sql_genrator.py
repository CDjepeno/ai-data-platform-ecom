def generate_sql(question: str) -> str:

    question = question.lower()

    if "monthly revenue" in question:
        return """
        SELECT *
        FROM mart.revenue_by_month
        """

    if "top customers" in question:
        return """
        SELECT *
        FROM mart.top_customer
        """

    return "SELECT 1"