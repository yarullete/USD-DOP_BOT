import webbrowser
from datetime import datetime

# Example rates (replace with your real data if needed)
rates = [
    ("Banco Popular", "$57.50", "$60.50"),
    ("Banreservas", "$58.40", "$60.25"),
    ("Banco BHD León", "$57.60", "$60.25"),
]

today = datetime.now().strftime('%d de %B de %Y')

html_content = f'''
<html>
  <body>
    <h2>🇺🇸💵 Tasas USD/DOP hoy ({today}):</h2>
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
    <p style="font-size:small;color:gray;">Enviado automáticamente por tu bot de tasas USD/DOP.</p>
  </body>
</html>
'''

with open("preview.html", "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open("preview.html") 