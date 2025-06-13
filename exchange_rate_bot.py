import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
BANKS = {
    "Banco Popular": "https://www.infodolar.com.do/precio-dolar-entidad-banco-popular.aspx",
    "Banreservas": "https://www.infodolar.com.do/precio-dolar-entidad-banreservas.aspx",
    "Banco BHD León": "https://www.infodolar.com.do/precio-dolar-entidad-banco-bhd.aspx",
}

YAHOO_EMAIL = os.environ.get("YAHOO_EMAIL")
YAHOO_APP_PASSWORD = os.environ.get("YAHOO_APP_PASSWORD")

SPANISH_MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

GSHEET_CREDENTIALS = "usd-dop-bot-1d6231b8312c.json"
GSHEET_NAME = "Tasas USD-DOP Newsletter (Responses)(Mail)"
GSHEET_TAB = "Form Responses 1"
GSHEET_EMAIL_COLUMN = 2  # Column B (1-indexed)

# --- FUNCTIONS ---
def get_recipients_from_gsheet():
    """Fetch the list of subscriber emails from the Google Sheet."""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GSHEET_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GSHEET_NAME).worksheet(GSHEET_TAB)
    data = sheet.get_all_values()
    # Skip header, get all non-empty emails from column B
    recipients = [row[GSHEET_EMAIL_COLUMN-1].strip() for row in data[1:] if len(row) > GSHEET_EMAIL_COLUMN-1 and '@' in row[GSHEET_EMAIL_COLUMN-1]]
    return recipients

def extract_first_amount(cell_text):
    """Extract only the first amount (e.g., $57.50 from "$57.50= $0.00")."""
    return cell_text.split('=')[0].strip()

def get_rates(url):
    """Scrape the USD/DOP buy and sell rates from the given InfoDolar URL."""
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table')
    if not table:
        return None, None
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            compra = extract_first_amount(cols[1].get_text(strip=True))
            venta = extract_first_amount(cols[2].get_text(strip=True))
            return compra, venta
    return None, None

def build_html_email(rates):
    """Build the HTML content for the email newsletter."""
    now = datetime.now()
    day = now.day
    month = SPANISH_MONTHS[now.month - 1]
    year = now.year
    date_str = f"{day} de {month} de {year}"
    html = f'''
    <html>
      <body>
        <h2>🇺🇸💵 Tasas USD/DOP hoy ({date_str}):</h2>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
          <tr>
            <th>🏦 Banco</th>
            <th>Compra</th>
            <th>Venta</th>
          </tr>
          <tr>
            <td><b>{rates[0][0]}</b></td>
            <td>{rates[0][1]}</td>
            <td>{rates[0][2]}</td>
          </tr>
          <tr>
            <td><b>{rates[1][0]}</b></td>
            <td>{rates[1][1]}</td>
            <td>{rates[1][2]}</td>
          </tr>
          <tr>
            <td><b>{rates[2][0]}</b></td>
            <td>{rates[2][1]}</td>
            <td>{rates[2][2]}</td>
          </tr>
        </table>
        <p style="font-size:small;color:gray;">Enviado automáticamente por tu bot de tasas USD/DOP.<br>Para dejar de recibir este correo, responde con UNSUBSCRIBE.</p>
      </body>
    </html>
    '''
    return html

def send_email(subject, html_body, sender, password, recipients):
    """Send the HTML email to all recipients."""
    msg = MIMEText(html_body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    try:
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        print(f"Email sent successfully to {len(recipients)} recipients!")
    except Exception as e:
        print(f"Error sending email: {e}")

# --- MAIN WORKFLOW ---
def main():
    # Scrape rates from all banks
    rates = []
    for bank, url in BANKS.items():
        compra, venta = get_rates(url)
        if compra and venta:
            rates.append((bank, compra, venta))
        else:
            rates.append((bank, "No disponible", "No disponible"))
    # Build HTML email
    html_body = build_html_email(rates)
    # Save preview for manual checking
    with open("preview.html", "w", encoding="utf-8") as f:
        f.write(html_body)
    # Get recipients from Google Sheet
    recipients = get_recipients_from_gsheet()
    if recipients:
        send_email(
            subject="Tasas USD/DOP hoy",
            html_body=html_body,
            sender=YAHOO_EMAIL,
            password=YAHOO_APP_PASSWORD,
            recipients=recipients
        )
    else:
        print("No recipients found in Google Sheet.")

if __name__ == "__main__":
    main() 