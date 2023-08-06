import decimal
from http.client import HTTPResponse
from django.views import View
from django.shortcuts import render, redirect
import csv
import io

# from dashboard.category_keyword_mapping import CATEGORY_KEYWORD_MAPPING
from dashboard.models import Category, Transaction, Account
from datetime import datetime
from decimal import Decimal

CATEGORY_KEYWORD_MAPPING = {
    "Groceries": ["SUPERVALU", "TESCO"],
    "Fees": ["FEE", "INTEREST CHARGED"],
    "Pharmacy": ["PHARM"],
    "Doctors": ["MED", "VDC-CHURCHTOWN"],
    "Car Insurance": ["AXA"],
    "Life Insurance": ["AVIVA"],
    "Amazon Prime": ["AMZNPRIME"],
    "Entertainment": ["DISNEY", "*YouTub", "discovery+", "VDP-DISNEY PLUS"],
    "Loan": ["LOAN"],
    "ChatGPT": ["CHATGPT"],
    "Revolut": ["Revolut"],
    "Internet": ["THREE IRELAND"],
    "Petrol": [
        "FUEL",
        "VDC-FAIRVIEW SERVI",
        "VDP-MAXOL",
    ],
    "Converge": ["CONVERGE"],
    "Lotto": ["LOTTER"],
    "Web Hosting": ["HEROKU"],
    "Electric": ["VDP-PREPAYPOWER"],
    "Phone": ["VDP-VODAFONE"],
    "Audible": ["VDP-Audible UK"],
    "Savings": ["SAVINGS"],
    "Credit Card": ["CLICK VISA"],
}


def get_category_for_vendor(vendor):
    for category, keywords in CATEGORY_KEYWORD_MAPPING.items():
        for keyword in keywords:
            if keyword in vendor:
                # Once matched, get or create the category object
                category_obj, created = Category.objects.get_or_create(name=category)
                return category_obj
    return None  # if no category matched


def dashView(request):
    context = {"transitions": Transaction.objects.all()}
    return render(request, "dashboards/index.html", context)


class UploadView(View):
    pass

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("uploaded_file")

        if csv_file is None:
            # Handle the error: return an error response or set a flag for the template to display an error message
            print(request, "NO FILE!")
            return redirect("upload_view")

        if not csv_file.name.endswith(".csv"):
            # Handle the case where the uploaded file isn't a CSV
            # messages.error(request, "This file format is not supported!")
            print(request, "This file format is not supported!")
            return redirect("upload_view")

        data_set = csv_file.read().decode("UTF-8")
        io_string = io.StringIO(data_set)

        # Assuming the CSV has a header row, we'll skip the first row.
        next(io_string)

        for row in csv.reader(io_string, delimiter=",", quotechar="|"):
            # Parsing data from the CSV row
            account_number = row[0]
            date_str = row[1]
            vendor = row[2].strip('"')  # removing surrounding quotes
            trans_type = row[-1]
            amount = row[3].strip()
            amount = amount.replace(",", "")
            try:
                amount_decimal = Decimal(amount)
            except decimal.InvalidOperation:
                print(f"Failed to convert '{amount}' from row: {row}")
                continue  # skip this row and continue with the next

            # Assuming account exists, otherwise you might want to create it or handle accordingly.
            account = Account.objects.get(account_number=account_number)
            category = get_category_for_vendor(
                vendor
            )  # get the category object using the helper function

            # Convert date string into a date object
            date_obj = datetime.strptime(date_str, "%d/%m/%y").date()

            # Create a new transaction
            transaction = Transaction(
                account=account,
                date=date_obj,
                vendor=vendor,
                amount=amount_decimal,
                category=category,
                trans_type=trans_type,
            )
            transaction.save()

        print(request, "File uploaded and processed successfully!")

        return redirect("dashView")

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, "dashboards/upload.html", context)
