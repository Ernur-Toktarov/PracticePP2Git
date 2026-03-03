import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()


#Extract all prices from the receipt
price_list = re.findall(r'\d+\s?\d*,\d{2}', text)

prices = []
for p in price_list:
    value = p.replace(" ", "").replace(",", ".")
    prices.append(float(value))


#Find all product names
products = re.findall(r'\n\d+\.\s*\n([^\n]+)', text)


#Calculate total amount
total_match = re.search(r'ИТОГО:\s*\n([\d\s]+,\d{2})', text)

if total_match:
    total_amount = total_match.group(1)
    total_amount = float(total_amount.replace(" ", "").replace(",", "."))
else:
    total_amount = None


#Extract date and time information
datetime_match = re.search(r'\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}', text)

if datetime_match:
    datetime_value = datetime_match.group(0)
else:
    datetime_value = None


#Find payment method
if "Банковская карта" in text:
    payment_method = "Банковская карта"
elif "Наличные" in text:
    payment_method = "Наличные"
else:
    payment_method = None


#Create a structured output (JSON or formatted text)
data = {
    "products": products,
    "prices": prices,
    "total": total_amount,
    "datetime": datetime_value,
    "payment_method": payment_method
}

print(json.dumps(data, ensure_ascii=False, indent=4))