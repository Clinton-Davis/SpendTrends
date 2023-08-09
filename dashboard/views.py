import decimal
from http.client import HTTPResponse
from django.views import View
from django.shortcuts import render, redirect
import csv
import io
import pandas as pd

# from dashboard.category_keyword_mapping import CATEGORY_KEYWORD_MAPPING
from dashboard.models import Category, Transaction, Account
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict
from dashboard.category_keyword_mapping import CATEGORY_KEYWORD_MAPPING
from collections import OrderedDict, defaultdict


def get_category_for_vendor(vendor):
    for category, keywords in CATEGORY_KEYWORD_MAPPING.items():
        for keyword in keywords:
            if keyword in vendor:
                # Once matched, get or create the category object
                category_obj, created = Category.objects.get_or_create(
                    name=category,
                    defaults={"description": "Automatically created category"},
                )
                return category_obj

    # If no category matched, return a 'Sundries' Category object
    category_obj, created = Category.objects.get_or_create(
        name="Sundries", defaults={"description": "Default sundries category"}
    )
    return category_obj


def dashView(request):
    # Querying Credit transactions
    credit_totals = (
        Transaction.objects.filter(trans_type="Credit")
        .annotate(month=TruncMonth("date"))
        .values("month", "category__name")
        .annotate(total_amount=Sum("amount"))
        .order_by("month", "category__name")
    )

    # Querying Debit transactions
    debit_totals = (
        Transaction.objects.filter(trans_type="Debit")
        .annotate(month=TruncMonth("date"))
        .values("month", "category__name")
        .annotate(total_amount=Sum("amount"))
        .order_by("month", "category__name")
    )

    results = defaultdict(
        lambda: {"credit": [], "debit": [], "credit_total": 0, "debit_total": 0}
    )

    # Storing Credit transactions and their totals
    for month in credit_totals:
        results[month["month"]]["credit"].append(
            {"category": month["category__name"], "total_amount": month["total_amount"]}
        )
        results[month["month"]]["credit_total"] += month["total_amount"]

    # Storing Debit transactions and their totals
    for month in debit_totals:
        results[month["month"]]["debit"].append(
            {"category": month["category__name"], "total_amount": month["total_amount"]}
        )
        results[month["month"]]["debit_total"] += month["total_amount"]

    ordered_results = OrderedDict(sorted(results.items()))

    context = {"monthly_data": dict(ordered_results)}

    return render(request, "dashboards/index.html", context)


import io


class UploadView(View):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("uploaded_file")

        if not csv_file:
            print(request, "NO FILE!")
            return redirect("upload_view")

        if not csv_file.name.endswith(".csv"):
            print(request, "This file format is not supported!")
            return redirect("upload_view")

        # Reading the CSV directly into a DataFrame
        data_set = csv_file.read().decode("UTF-8")
        df = pd.read_csv(io.StringIO(data_set))
        df.columns = df.columns.str.strip()
        # Iterating through each row of the DataFrame
        for _, row in df.iterrows():
            trans_type = row["Transaction Type"]

            if row["Transaction Type"] == "Credit":
                amount = str(row["Credit Amount"]).replace(",", "")
                if pd.isna(amount):
                    continue
            else:
                amount = str(row["Debit Amount"]).replace(",", "")
                if pd.isna(amount):
                    continue

            try:
                amount_decimal = Decimal(amount)
                account_number = row["Posted Account"]
                date_str = row["Posted Transactions Date"]
                vendor = row["Description"].strip('"')
            except Exception as e:
                print(f"Failed to process row: {row}. Error: {e}")
                continue

            try:
                account = Account.objects.get(account_number=account_number)
            except Account.DoesNotExist:
                print(f"Account {account_number} does not exist. Skipping.")
                continue

            category = get_category_for_vendor(vendor)
            date_obj = datetime.strptime(date_str, "%d/%m/%y").date()

            existing_transaction = Transaction.objects.filter(
                account=account,
                date=date_obj,
                amount=amount_decimal,
                vendor=vendor,
            ).first()

            if not existing_transaction:
                transaction = Transaction(
                    account=account,
                    date=date_obj,
                    vendor=vendor,
                    amount=amount_decimal,
                    category=category,
                    trans_type=trans_type,
                )
                transaction.save()
            else:
                print(f"Skipped duplicate transaction for {vendor} on {date_obj}")

        print(request, "File uploaded and processed successfully!")
        return redirect("dashView")

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, "dashboards/upload.html", context)
