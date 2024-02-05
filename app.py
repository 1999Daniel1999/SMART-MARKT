import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import requests  # Importieren Sie das requests Modul
import base64
import qrcode
from PIL import Image
import io

# API-Schlüssel
GOOGLE_MAPS_API_KEY = "AIzaSyDkEDHUfypXBTuCtTzo47IpalCsqp9eyVQ" # Ersetzen Sie dies mit Ihrem API-Schlüssel
st.set_page_config(layout="wide")
# Funktion, um eine Adresse in Koordinaten umzuwandeln
def geocode_address(address):
    # Adresszeichenfolge URL-kodieren
    address = requests.utils.quote(address)
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(geocode_url)
    #print("Geocode response:", response.json())  # Debug-Ausgabe direkt nach der Anfrage
    
    if response.status_code == 200:
        results = response.json()['results']
        if results:
            location = results[0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None
    response = requests.get(geocode_url)

# Pfad zur Excel-Datei
excel_path = "app/Sortiment_vereinfacht_10.xlsx"

# Definiere die Überkategorien und die zugehörigen Unterkategorien
categories = {
    'Frühstück': [
        'Bananen', 'Erdbeeren', 'Himbeeren', 'Avocado', 'Orangen', 'Heidelbeeren',
        'Tiefkühl-Brötchen', 'Haferflocken', 'Müsli', 'Bacon', 'Haferdrink',
        'Baguette', 'Croissant', 'Brötchen', 'Eier', 'Honig',
        'Vollmilch', 'Magermilch', 'Joghurt', 'Quark', 'Marmelade',
        'Multivitaminsaft', 'Orangensaft', 'Kaffeepulver', 'Kaffeebohnen',
        'Kakaopulver', 'Erdnussbutter', 'Nutella'
        # Füge hier alle weiteren Elemente hinzu
    ],
    'Lunch': [
        'Tomaten', 'Karotten', 'Brokkoli', 'Spinat', 'Zucchini', 'Paprika',
        'Blumenkohl', 'Gurken', 'Auberginen', 'Kartoffeln', 'Salat',                           
        'Knoblauch', 'Erbsen', 'Pilze', 'Lauch', 'Rosenkohl', 'Pizza', 'Lasagne',
        'Pommes', 'Chicken Nuggets', 'Fischstäbchen', 'Rindersteak', 'Reis',
        'Schnitzel', 'Bratwurst', 'Couscous', 'Chicken Wings', 'Burger-Buns',
        'Tofu', 'Hähnchenkeule', 'Spaghetti', 'Penne', 'Fusilli', 'Forelle',
        'Kabeljau', 'Gnocchi', 'Spätzle', 'Veganes Chicken', 'Falafel', 'Hackfleisch', 'Veganes Hack'
        # Füge hier alle weiteren Elemente hinzu
    ],
    'Dinner': [
        'Salami', 'Mortadella', 'Schinken', 'Leberwurst', 'Weißbrot', 'Vollkornbrot',
        'Knäckebrot', 'Frischkäse', 'Gouda', 'Emmentaler', 'Camembert',
        'Veganer Aufschnitt', 'Hummus', 'Hühnersuppe', 'Tomatensuppe',
        'Gemüsesuppe', 'Linsensuppe', 'Bratkartoffeln'
        # Füge hier alle weiteren Elemente hinzu
    ],
    'Snacks': [
        'Äpfel', 'Trauben', 'Kirschen', 'Eiscreme', 'Kekse', 'Chips', 'Erdnüsse', 
        'Cashews', 'Müsliriegel', 'Salzstangen', 'Nachos', 'Reiswaffeln', 'Flips', 
        'Schokolade', 'Gummibären', 'Bonbons', 'Donuts', 'Schokoriegel', 'Waffeln', 
        'Schokolinsen', 'Muffins', 'Pralinen'
        # Füge hier alle weiteren Elemente hinzu
    ],
    'Sonstige': [
        'Birnen', 'Zitronen', 'Wassermelone',  'Mais', 'Ingwer', 
        'Oliven', 'Gemüsemischung', 'Ravioli',  'Eintopf', 
        'Tiefkühl-Lachsfilets', 'Lammfilet', 'Frikadellen', 'Thunfisch', 
        'Hering', 'Sardinen', 'Garnelen', 'Krabben', 'Muscheln', 'Meeresfrüchte-Mix', 
        'Quinoa', 'Milchreis', 'Linsen', 'Fladenbrot', 'Ciabatta', 'Tortellini', 
        'Schupfnudeln', 'Buttermilch', 'Sahne', 'Mozzarella', 'Creme fraiche', 
        'Schmand', 'Stilles Wasser', 'Mineralwasser', 'Cola', 'Eistee', 'Sprite', 'Apfelsaft', 
        'Energy-Drinks', 'Alkoholfreies Bier', 'Kaffeefilter', 'Kamillentee', 'Pfefferminztee', 
        'Grüner Tee', 'Schwarzer Tee', 'Basilikum-Pesto', 'Pesto-Rosso', 'Barbecue-Sauce', 
        'Sojasauce', 'Tomatensauce', 'Ketchup', 'Mayo', 'Senf', 'Sweet Chilli Sauce', 
        'Instant Nudeln', 'Rapsöl', 'Olivenöl', 'Butter', 'Margarine', 
        'Butterschmalz', 'Kokosöl', 'Bier', 'Rotwein', 'Wodka', 'Whisky', 'Rum', 'Tequila', 
        'Gin', 'Sekt', 'Weißwein', 'Jägermeister', 'Rosé', 'Salz', 'Pfeffer', 'Oregano', 
        'Zucker',  'Zimt', 'Zwiebeln'
        # Füge hier alle weiteren Elemente hinzu
    ]
}

# Funktion zum Erstellen eines QR-Codes für den Warenkorb eines bestimmten Supermarktes
def create_qr_code(supermarket, cart):
    # Erstelle einen String mit den Warenkorbdaten
    cart_content = "\n".join(f"{item['QUANTITY']}x {item['Produktname']} | {item['PRICE']}€" for item in cart)
    data = f"Warenkorb für {supermarket}:\n{cart_content}"
    
    # Erstelle einen QR-Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Konvertiere PIL Image in ein Streamlit-kompatibles Format
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    byte_im = buf.getvalue()
    
    return byte_im

# Funktion zum Laden der Daten für einen bestimmten Supermarkt
def load_data(sheet_name):
    data = pd.read_excel(excel_path, sheet_name=sheet_name)
    if 'Menge' not in data.columns or 'Einheit' not in data.columns:
        raise ValueError('Die Spalten "Menge" und "Einheit" müssen in der Excel-Datei vorhanden sein.')
    return data

# Formatierung Menge
def format_menge(menge):
    try:
        return str(int(float(menge)))  # Versuche, Menge als Zahl zu interpretieren und zu formatieren
    except ValueError:
        return menge  # Wenn Menge keine Zahl ist, gib sie unverändert zurück

# Funktion zum Hinzufügen von Produkten zum Warenkorb
def add_to_cart(product_category, sheet_names):
    for sheet_name in sheet_names:
        data = load_data(sheet_name)
        # Suche nach Produkten in der spezifischen Kategorie
        product_data = data[data['Radermacherkategorie'] == product_category]
        if not product_data.empty:
            min_price_row = product_data.loc[product_data['PRICE'].idxmin()]
            cart = st.session_state.shopping_carts[sheet_name]
            
            # Überprüfe, ob das Produkt bereits im Warenkorb ist
            existing_item = next((item for item in cart if item['Produktname'] == min_price_row['Produktname']), None)
            if existing_item:
                # Erhöhe die Anzahl des Produkts im Warenkorb
                existing_item['QUANTITY'] += 1
            else:
                # Füge das Produkt zum Warenkorb hinzu, wenn es noch nicht vorhanden ist
                cart.append({
                    'Produktname': min_price_row['Produktname'],
                    'PRICE': min_price_row['PRICE'],
                    'QUANTITY': 1,
                    'Menge': min_price_row['Menge'], 
                    'Einheit': min_price_row['Einheit'],
                    'Radermacherkategorie': product_category,
                    #'Preis2': min_price_row['Preis2'],
                    'Preis2': "{:.2f}".format(float(min_price_row['Preis2'])),
                    'Einheit2': min_price_row['Einheit2']
                })

# Funktion zum Entfernen von Produkten aus dem Warenkorb
def remove_from_cart(product_category, sheet_names):
    for sheet_name in sheet_names:
        cart = st.session_state.shopping_carts[sheet_name]
        
        # Überprüfe, ob das Produkt bereits im Warenkorb ist
        existing_item = next((item for item in cart if item['Radermacherkategorie'] == product_category), None)
        if existing_item:
            existing_item['QUANTITY'] -= 1  # Reduziere die Anzahl um 1

            # Entferne das Produkt aus dem Warenkorb, wenn die Anzahl 0 erreicht
            if existing_item['QUANTITY'] <= 0:
                cart.remove(existing_item)
                    
# Ändere die Funktion display_alternatives(supermarket, item, cart) wie folgt:
def display_alternatives(supermarket, item, cart):
    data = load_data(supermarket)
    # Hole die Radermacherkategorie des Produkts im Warenkorb
    cart_radermacherkategorie = item.get('Radermacherkategorie', '')  # Leerer String,  wenn nicht vorhanden
    # Wenn die Radermacherkategorie im Warenkorb nicht gesetzt ist, setze sie auf die des ausgewählten Produkts
    if not cart_radermacherkategorie:
        cart_radermacherkategorie = data[data['Produktname'] == item['Produktname']]['Radermacherkategorie'].values[0]
    # Filtere die Daten, um nur Produkte mit derselben Radermacherkategorie wie im Warenkorb anzuzeigen
    alternatives = data[(data['Radermacherkategorie'] == cart_radermacherkategorie) & (data['Produktname'] != item['Produktname'])]
    # Sortiere die Alternativen nach Preis
    alternatives = alternatives.sort_values('PRICE')
    
    # Erzeuge eine Liste von Produktnamen für das Dropdown-Menü
    options = [f"{row['Produktname']} | {format_menge(row['Menge'])} {row['Einheit']} | {row['PRICE']}€ | {'{:.2f}'.format(float(row['Preis2']))}€ pro {row['Einheit2']}" for _, row in alternatives.iterrows()]
    
    # Wenn keine Optionen vorhanden sind, beende die Funktion
    if not options:
        st.write("Keine Alternativen verfügbar.")
        return

    # Erzeuge das Dropdown-Menü
    selected_option = st.selectbox("Wähle ein alternatives Produkt", options, key=f"select_{supermarket}_{item['Produktname']}")
    
    # Splitte die ausgewählte Option und erhalte die Werte in einer Liste
    selected_option_values = selected_option.split(' | ')
    
    # Überprüfe, ob die Liste mindestens 3 Werte enthält (Produktname, Preis, Menge und Einheit)
    if len(selected_option_values) >= 3:
        selected_product_name = selected_option_values[0]
        selected_product = alternatives[alternatives['Produktname'] == selected_product_name].iloc[0]

        # Ersetze das Produkt im Warenkorb durch das ausgewählte Produkt
        if selected_product_name != item['Produktname']:
            cart.remove(item)
            cart.append({
                'Produktname': selected_product['Produktname'],
                'PRICE': selected_product['PRICE'],
                'QUANTITY': item['QUANTITY'],
                'Menge': format_menge(selected_product['Menge']), 
                'Einheit': selected_product['Einheit'],
                'Radermacherkategorie': selected_product['Radermacherkategorie'],
                #'Preis2': selected_product['Preis2'],
                'Preis2': "{:.2f}".format(float(selected_product['Preis2'])),
                'Einheit2': selected_product['Einheit2']
            })

# Funktion zum Anzeigen von Warenkörben
def display_carts(shopping_carts, show_all, user_lat, user_lng):
    cart_totals = {}
    cart_updated = False  # Statusvariable, um zu überwachen, ob eine Änderung stattgefunden hat

    # Zugriff auf die Informationen über die nächstgelegenen Supermärkte
    nearest_supermarkets = st.session_state.nearest_supermarkets
    
    # Filtere die Supermärkte, die sich im ausgewählten Radius befinden
    in_radius_supermarkets = {k: v for k, v in nearest_supermarkets.items() if v[2] != float('inf')}
    
    # Berechne die Gesamtsumme für jeden Warenkorb der Supermärkte im Radius
    for supermarket, items in shopping_carts.items():
        if supermarket in in_radius_supermarkets:
            cart_totals[supermarket] = sum(item['PRICE'] * item['QUANTITY'] for item in items)
    
    # Erzeuge eine Liste von Tupeln (Supermarktname, Gesamtsumme)
    sorted_carts = sorted(cart_totals.items(), key=lambda x: x[1])

    # Finde den Warenkorb mit der niedrigsten Gesamtsumme unter den angezeigten Supermärkten
    lowest_total = min(cart_totals.values(), default=float('inf'))
    lowest_cart = min(cart_totals, key=cart_totals.get, default=None)
    
    # Zeige die Warenkörbe und deren Gesamtsummen an
    for supermarket, _ in sorted_carts:
        if supermarket == lowest_cart or (show_all and supermarket in in_radius_supermarkets):
            items = shopping_carts[supermarket]
            distance = in_radius_supermarkets[supermarket][2]
            name, address, _ = in_radius_supermarkets[supermarket]

            distance_display = f"{int(distance)}m"

            # Erstelle die URL für die Google Maps-Wegbeschreibung
            dest_lat, dest_lng = in_radius_supermarkets[supermarket][:2]
            directions_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lng}&destination={dest_lat},{dest_lng}&travelmode=walking"
            
            address_display = f"<a href='{directions_url}' target='_blank'>{address}</a>"
          
            col1, mid = st.columns([2,3] ,gap="small")
            if supermarket == "ALDI SÜD":
                col1.image("app/static/P5 Aldi.png",width= 150)
            elif supermarket == "Lidl":
                col1.image("app/static/p4 Lidl.png",width= 140)
            elif supermarket == "Penny":
                col1.image("app/static/P3 Penny.png",width= 150)
            elif supermarket == "Rewe":
                col1.image("app/static/P2 REWE.png",width= 135)
            elif supermarket == "Netto":
                col1.image("app/static/P6 Netto.png",width= 150)
            elif supermarket == "Edeka":
                col1.image("app/static/P1 (EDEKA).png",width= 150)
            mid.markdown(f"<h6 style='text-align: right; margin-top: 10px; margin-right: 10px;'>ist zu Fuß {distance_display} entfernt</h6>", unsafe_allow_html=True)

          
            address_display = f"<a href='{directions_url}' target='_blank' style='color: gray; font-size: 14px; margin-top: -10px; display: block;'>{address}</a>"
            st.markdown(address_display, unsafe_allow_html=True)
            for item in items:
                col1, col2, col3, col4, col5 = st.columns([6, 0.5, 0.7, 1, 1])
                formatted_menge = format_menge(item['Menge'])
                formatted_price2 = "{:.2f}".format(float(item['Preis2']))
                product_info = f"<strong>{item['QUANTITY']}x</strong> {item['Produktname']} | {item['PRICE']}€"
                product_info1 = f" {formatted_menge} {item['Einheit']} | {formatted_price2}€ pro {item['Einheit2']}"
                col1.markdown(f"<p >{product_info}<Br>{product_info1}<p/>",unsafe_allow_html=True)
               
            
                
                
                if col3.button("➕", key=f"add_{supermarket}_{item['Produktname']}"):
                    item['QUANTITY'] += 1
                    cart_updated = True

                if col4.button("➖", key=f"remove_{supermarket}_{item['Produktname']}"):
                    if item['QUANTITY'] > 1:
                        item['QUANTITY'] -= 1
                        cart_updated = True
                    else:
                        items.remove(item)
                        cart_updated = True

                if col5.button("⬇️", key=f"dropdown_{supermarket}_{item['Produktname']}"):
                    display_alternatives(supermarket, item, items)

            # Container für Gesamtsumme und QR-Code Expander
            total_container = st.container()
            with total_container:
                # Spalten für Gesamtsumme und den Expander-Button
                col1, col2 = st.columns([5, 1.2])
                
                # Zeige die Gesamtsumme in der ersten Spalte
                with col1:
                    total = cart_totals[supermarket]
                    # Hier fügen wir einen oberen Rand hinzu, indem wir die CSS-Klasse "total-margin" verwenden
                    st.markdown(f"<div class='total-margin'><strong>Gesamtsumme: {total:.2f}€<strong></div>", unsafe_allow_html=True)

                # Custom CSS hinzufügen, um den oberen Rand zu definieren
                st.markdown("""
                    <style>
                    .total-margin {
                        margin-top: 11px; /* Passen Sie diesen Wert an, um den gewünschten Abstand zu erhalten */
                        font-size: 1.2em; /* Erhöht die Schriftgröße */
                    }
                    /* Weitere CSS-Regeln können hier eingefügt werden */
                    </style>
                    """, unsafe_allow_html=True)

                # Zeige den Expander in der zweiten Spalte
                with col2:
                    # Titel des Expanders
                    expander_title = 'QR-Code'
                    expander = st.expander(expander_title)
                    if expander:
                        if expander:
                            # Generiere den QR-Code für den aktuellen Warenkorb
                            # Dies wird jedes Mal neu generiert, wenn die Funktion aufgerufen wird,
                            # was bei jeder Änderung im Warenkorb geschieht
                            qr_code_image = create_qr_code(supermarket, items)
                            


                            # Zeige den QR-Code an
                            expander.image(qr_code_image, width=80)  # Passen Sie die Breite nach Bedarf an
                                
            # Zeige Differenzen nur für den billigsten Warenkorb und nur zwischen Warenkörben, die im Radius sind
            if supermarket == lowest_cart:
                diff_cols = st.columns(len(in_radius_supermarkets) - 1,gap  = "medium" )
                index = 0
                for other_supermarket, other_total in sorted(cart_totals.items(), key=lambda x: x[1]):
                    if other_supermarket != lowest_cart:
                        difference = other_total - lowest_total
                        diff_cols[index].markdown(
                            f"<span style='color: red; margin-top: -20px; display: block;'>{other_supermarket} = {difference:.2f}€</span>", 
                            unsafe_allow_html=True
                        )
                        index += 1
                # Überprüfen Sie, ob es Unterschiede in den Produktanzahlen gibt
                if check_product_quantities(shopping_carts):
                    st.markdown("""
                        <div style='margin-left: 60px;'>
                            <span style='color: red; margin-top: -15px; display: block; margin-bottom: 10px;'>
                                Achtung! Unterschiedliche Anzahl an Produkten in den Warenkörben!
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

            #st.write("---")
            st.markdown(f"""
            <hr style='border-top: 1.5px solid #000000; margin-top: 0rem; margin-bottom: 1.8rem;'/>
            """, unsafe_allow_html=True)
    
    # Aktualisiere die Session State Variable und die Anzeige nur, wenn eine Änderung stattgefunden hat
    if cart_updated:
        for supermarket in shopping_carts:
            st.session_state.shopping_carts[supermarket] = shopping_carts[supermarket]
        st.experimental_rerun()

# Funktion zum Hinzufügen von Produkten zur Einkaufsliste
def add_to_shopping_list(product_category):
    # In der Einkaufsliste wird nur die Kategorie gespeichert, nicht der spezifische Produktname
    shopping_list = st.session_state.shopping_list
    existing_item = next((item for item in shopping_list if item['Kategorie'] == product_category), None)
 
    if existing_item:

        existing_item['Anzahl'] += 1
    else:
        shopping_list.append({
            'Kategorie': product_category,
            'Anzahl': 1
        })

# Funktion zum Aktualisieren der Produktanzahl in allen Warenkörben
def update_quantity_in_carts(product_category, increase=True):
    for sheet_name, cart in st.session_state.shopping_carts.items():
        for item in cart:
            if item['Radermacherkategorie'] == product_category:
                item['QUANTITY'] += 1 if increase else -1
                if item['QUANTITY'] <= 0:
                    cart.remove(item)
                    
# Funktion zum Anzeigen der Einkaufsliste
def display_shopping_list():
    if 'shopping_list' not in st.session_state:
        st.session_state.shopping_list = []

    shopping_list_container = st.container()
    with shopping_list_container:
        shopping_list_container.subheader("Meine Einkaufsliste")
        for item in st.session_state.shopping_list:
            col1, col2, col3 = shopping_list_container.columns([7, 0.7, 2.15])
            product_info = f"<strong>{item['Anzahl']}x</strong> {item['Kategorie']}"
            col1.markdown(f"{product_info}", unsafe_allow_html=True)

            # Innerhalb der Schleife
            if col2.button("➕", key=f"add_{item['Kategorie']}"):
                item['Anzahl'] += 1
                update_quantity_in_carts(item['Kategorie'], increase=True)
                st.experimental_rerun()
            
            if col3.button("➖", key=f"remove_{item['Kategorie']}"):
                item['Anzahl'] -= 1
                update_quantity_in_carts(item['Kategorie'], increase=False)
                if item['Anzahl'] <= 0:
                    st.session_state.shopping_list.remove(item)
                st.experimental_rerun()

            # Aktualisiere die shopping_list in der Session State
            st.session_state.shopping_list = [item for item in st.session_state.shopping_list if item['Anzahl'] > 0]

        col11, col22, col33 = st.columns([0.17, 0.81, 0.385])
        # Reset-Button
        if col11.button("Reset"):
            reset_shopping()
        
        # Fertig-Button
        if col33.button("Fertig!"):
            st.session_state.show_carts = True
            st.session_state.show_all_carts = False  # Nur der billigste Warenkorb wird beim ersten Klick angezeigt

        # Warenkörbe anzeigen/ausblenden Button
        if col22.button("Anzeigen"):
            st.session_state.show_all_carts = not st.session_state.show_all_carts  # Status umschalten
        
        # Füge einen kleinen Abstand nach den Buttons hinzu
        #st.markdown("<br>", unsafe_allow_html=True)  # Fügt einen Zeilenumbruch als Abstand hinzu
        st.markdown(f"""
        <hr style='border-top: 3px solid #000000; margin-top: 1rem; margin-bottom: 1.8rem;'/>
        """, unsafe_allow_html=True)

# Hier die reset_shopping Funktion einfügen
def reset_shopping():
    # Leere die Einkaufsliste
    st.session_state.shopping_list = []

    # Leere alle Warenkörbe
    for key in st.session_state.shopping_carts:
        st.session_state.shopping_carts[key] = []

    # Setze den Status der Anzeige der Warenkörbe zurück
    st.session_state.show_carts = False

    # Aktualisiere die Seite, um die Änderungen anzuzeigen
    st.experimental_rerun()

# Funktion zum Überprüfen der Produktanzahlen in den Warenkörben
def check_product_quantities(shopping_carts):
    category_quantities = {}
    for cart in shopping_carts.values():
        for item in cart:
            category = item['Radermacherkategorie']
            quantity = item['QUANTITY']
            if category not in category_quantities:
                category_quantities[category] = set()
            category_quantities[category].add(quantity)

    # Überprüfe, ob es Kategorien mit unterschiedlichen Anzahlen gibt
    for quantities in category_quantities.values():
        if len(quantities) > 1:
            return True
    return False

# Funktion, um die Entfernung zwischen zwei Koordinatenpunkten zu berechnen
def get_walking_distance(origin_lat, origin_lng, dest_lat, dest_lng):
    origins = f"{origin_lat},{origin_lng}"
    destinations = f"{dest_lat},{dest_lng}"
    distance_matrix_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origins}&destinations={destinations}&mode=walking&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(distance_matrix_url)
    if response.status_code == 200:
        results = response.json()
        if results['status'] == 'OK':
            distance_info = results['rows'][0]['elements'][0]
            if distance_info['status'] == 'OK':
                distance = distance_info['distance']['value']  # Distanz in Metern
                return distance
    return float('inf')  # Unendlich, wenn keine Distanz gefunden wird
    response = requests.get(distance_matrix_url)
    #print("Distance Matrix response:", response.json())  # Debug-Ausgabe

# Funktion, um die nächstgelegenen Supermärkte einer bestimmten Marke zu finden
def find_nearest_supermarket_brand(user_address, brands, radius):
    user_lat, user_lng = geocode_address(user_address)
    #print(f"Searching for supermarkets near: {user_lat}, {user_lng}")  # Debug-Ausgabe
    nearest_supermarkets = {brand: ("Nicht gefunden", "Nicht gefunden", float('inf')) for brand in brands}  # Initialisiere mit Standardwerten
    
    # Spezialbehandlung für bestimmte Marken
    additional_queries = {
        "Netto": ["Netto Marken-Discount"],
        "Edeka": ["Scheck-In-Center", "Edeka", "E Center"]
    }

    for brand in brands:
        # Standardabfrage für die Marke
        brand_queries = additional_queries.get(brand, []) + [brand]

        for brand_query in brand_queries:
            brand_query = brand_query.replace(' ', '+')
            places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={user_lat},{user_lng}&radius={radius*1000}&type=supermarket&keyword={brand_query}&key={GOOGLE_MAPS_API_KEY}"
            process_places_url(places_url, user_lat, user_lng, nearest_supermarkets, brand)

    return nearest_supermarkets

def process_places_url(places_url, user_lat, user_lng, nearest_supermarkets, brand):
    response = requests.get(places_url)
    #print(f"Places API response for brand {brand}: {response.json()}")  # Debug-Ausgabe
    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            for result in results:
                name = result.get('name')
                address = result.get('vicinity')
                dest_lat = result['geometry']['location']['lat']
                dest_lng = result['geometry']['location']['lng']
                distance = get_walking_distance(user_lat, user_lng, dest_lat, dest_lng)

                # Prüfe, ob der Name des Supermarkts den Markennamen enthält
                # und ob dieser Supermarkt näher ist als der aktuell gespeicherte
                if brand.lower() in name.lower() and distance < nearest_supermarkets[brand][2]:
                    nearest_supermarkets[brand] = (name, address, distance)
    else:
        print(f"Fehler bei der Anfrage an Google Places API: {response.status_code}")

@st.cache_data 
def get_image_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

left_right_image = get_image_as_base64("app/static/Background Picture 1.png")
centered_image = get_image_as_base64("app/static/Background Picture 2.png")
def changeButtonWidth():
            htmlstr = f"""
            <script>
            var elements = window.parent.document.querySelectorAll('button');
            for(var i = 5 ; i <= 11; i++) 
            {{
                    
                    if (elements[i].innerText == 'Frühstück' || elements[i].innerText == 'Lunch' || elements[i].innerText == 'Dinner' || elements[i].innerText == 'Snacks' || elements[i].innerText == 'Sonstige'  ) {{
                            elements[i].style.width = '8VW'
                            elements[i].style.height = '8vh'
                    }}
                            
                             
                           
            }}
            </script>
            """
            components.html(f"{htmlstr}", height=0, width=0)

# Streamlit-App-Funktion
def app():

    # Custom CSS
    st.markdown(f"""
    <style>
        /* Vorhandene CSS-Regeln für die Buttons und andere Elemente */
        div[data-testid = 'tooltipHoverTarget'] button {{
            white-space: nowrap; 
            background-color: #D3D3D3;
            width: 8VW;
            height: 8vh;
        }} 
        div[data-testid = 'tooltipHoverTarget'] button p {{
            font-size: 13px;
        }} 
        [class ="st-emotion-cache-12w0qpk e1f1d6gn3"] {{
            background-image: url("data:image/png;base64,{left_right_image}");
            background-size: 400px 400px;
        }}
        [class = "st-emotion-cache-keje6w e1f1d6gn3"] {{
            background-image: url("data:image/png;base64,{centered_image}");
            background-size: 400px 400px;
        }}
        div[class = 'st-emotion-cache-1bhc2nc e1f1d6gn2'] button {{
            background-color: #D3D3D3;
            width: 8VW;
            height: 8vh;
        }}
        /* Weitere CSS-Regeln für + und - Buttons und andere Elemente, falls vorhanden */
        span[style] {{
            white-space: nowrap;
        }}

        /* Hinzugefügte CSS-Regel für die Überschrift SMART MARKT */
        .smart-markt-header {{
        color: #3A84D6; /* RGB Farbe für die Überschrift */
        font-family: 'Impact', sans-serif; /* Schriftart auf Impact setzen */
        font-size: 3.5em; /* Erhöht die Schriftgröße auf das 4-fache der Standardtextgröße */
        transform: skewX(-18deg); /* Text rechtsschief machen */
        text-decoration: underline; /* Fügt eine Unterstreichung hinzu */
        text-decoration-color: #3A84D6; /* Farbe der Unterstreichung */
        text-decoration-thickness: 9.2px; /* Dicke der Unterstreichung */
        }}
        /* Stil für das Wort 'SMART' */
        .smart-markt-header .smart {{
            display: block; /* Setzt 'SMART' auf eine neue Zeile */
            margin-left: 0em; /* Setzt den Einzug für 'MARKT' */
        }}
        /* Stil für das Wort 'MARKT', Einrückung um den gewünschten Abstand */
        .smart-markt-header .markt {{
            margin-left: 1.4em; /* Setzt den Einzug für 'MARKT' */ 
        }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2,col3 = st.columns([1,2,1])   
  

       
        
    with col2:
       
    
        col2_1, col2_2, col2_3 = col2.columns([0.5,1.2,2])
        col2_2.image("app/static/LOGO.png",width=180)
        col2_3.markdown('<h1 class="smart-markt-header"><span class="smart">SMART</span><span class="markt">MARKT</span></h1>', unsafe_allow_html=True)

        # Lade die Namen der Arbeitsmappen
        xl = pd.ExcelFile(excel_path)
        sheet_names = xl.sheet_names  # Namen der Arbeitsmappen

        # Initialisiere den Status für die Anzeige aller Warenkörbe
        if 'show_all_carts' not in st.session_state:
            st.session_state.show_all_carts = False
        
        # Initialisiere die Einkaufsliste und andere notwendige Session State Variablen
        if 'shopping_list' not in st.session_state:
            st.session_state.shopping_list = []
        
        # Initialisiere die Warenkörbe und andere notwendige Session State Variablen
        if 'shopping_carts' not in st.session_state:
            st.session_state.shopping_carts = {name: [] for name in sheet_names}

        # Benutzereingabe für Adresse und Radius
        col2.subheader("Gib bitte deine Adresse ein")
        street_input = col2.text_input("Straße")
        house_number_input = col2.text_input("Hausnummer")
        postal_code_input = col2.text_input("Postleitzahl")
        address_input = f"{street_input} {house_number_input}, {postal_code_input}"
        radius_input = col2.number_input("Radius in Kilometern", value=5)
    
        # In der Funktion app, nachdem Sie die nächstgelegenen Supermärkte gefunden haben:
        if col2.button("Suche Supermärkte"):
            # Benutzeradresse in Koordinaten umwandeln
            user_lat, user_lng = geocode_address(address_input) 
            
            # Überprüfen, ob die Koordinaten erfolgreich abgerufen wurden
            if user_lat is not None and user_lng is not None:
                # Koordinaten im Session State speichern
                st.session_state.user_lat = user_lat
                st.session_state.user_lng = user_lng

            # Suche die nächstgelegenen Supermärkte basierend auf den Koordinaten
                brands = ["Rewe", "Edeka", "ALDI SÜD", "Lidl", "Penny", "Netto"]
                nearest_supermarkets = find_nearest_supermarket_brand(address_input, brands, radius_input)
                st.session_state.nearest_supermarkets = nearest_supermarkets
                for brand, supermarket_info in nearest_supermarkets.items():
                    name, address, distance = supermarket_info
                    # Hier können Sie Informationen zu jedem Supermarkt ausgeben, wenn Sie möchten
            else:
                st.error("Adresse konnte nicht geocodiert werden. Bitte überprüfen Sie die Adresse und versuchen Sie es erneut.")
        
        # Einen kleinen Abstand nach dem Button einfügen
        col2.markdown("<br>", unsafe_allow_html=True)
        
        # Container für Überkategorien
          
        def ChangeButtonColour(widget_label, buttonState):
            btn_bg_colour = "#FF0000"
            htmlstr = f"""
                <script>
                    var elements = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < elements.length; ++i) {{ 
                        
                        if (elements[i].innerText == '{widget_label}' && '{buttonState}' == 'clicked' ) {{ 
                            elements[i].style.background = '{btn_bg_colour}'
                            elements[i].style.color = 'white'
                        }} else {{
                            console.log("nono");
                            elements[i].style.background = ''
                            elements[i].style.color = 'black'
                        }} 

                    }}
                </script>
                """
            components.html(f"{htmlstr}", height=0, width=0)
        
        cols = col2.columns(len(categories) )
        for idx, (category_name, subcategories) in enumerate(categories.items()):
            
            # Hervorhebung der ausgewählten Kategorie in Rot
            if st.session_state.get('selected_category') == category_name:
                #cols[idx].markdown(f"<h2 style='text-align: center; width : 200px; '>{category_name}</h2>", unsafe_allow_html=True)
                # Toggle für die Auswahl
                
                if cols[idx].button(category_name):
                    print("unclicked")
                    print(category_name)
                    ChangeButtonColour(category_name,"notclicked")
                    st.session_state.selected_category = None
                
            else:
                if cols[idx].button(category_name):

                    print("clicked")
                    print(category_name)
                    ChangeButtonColour(category_name,"clicked")
                   
                    st.session_state.selected_category = category_name
                    st.session_state.subcategories = sorted(subcategories) 
        changeButtonWidth()
        # Abstand zwischen Über- und Unterkategorien
        #col2.markdown("###")  # Erhöht den Abstand
        container = col2.container(border=True)
        # Zeige die Unterkategorien der ausgewählten Überkategorie
        if st.session_state.get('selected_category'):
            # Sortierung und Anzeige in Gruppen von 5
            subcategories = st.session_state.subcategories
            no_of_columns = 5
            for i in range(0, len(subcategories), no_of_columns):
                row = container.columns(no_of_columns)

                # Beim Hinzufügen von Produkten zum Warenkorb und zur Einkaufsliste
                for j, subcategory in enumerate(subcategories[i:i+no_of_columns]):
                    
      
      
      
                 if row[j].button(subcategory, help = "Auswählen"):
                        
                        # Hinzufügen von Produkten zum Warenkorb für jede Arbeitsmappe
                        add_to_cart(subcategory, sheet_names)
                        # Hinzufügen der Kategorie zur Einkaufsliste
                        add_to_shopping_list(subcategory)
                    
        # Initialisiere den Status für die Anzeige der Warenkörbe
        if 'show_carts' not in st.session_state:
            st.session_state.show_carts = False
    
        # Zeige die Einkaufsliste an, oberhalb der Warenkörbe
        display_shopping_list()

        # Wenn Sie die Warenkörbe anzeigen möchten, überprüfen Sie zuerst, ob die Benutzerkoordinaten vorhanden sind
        if 'user_lat' in st.session_state and 'user_lng' in st.session_state:
            if st.session_state.show_carts:
                # Übergeben Sie die Koordinaten des Benutzers an die display_carts Funktion
                display_carts(
                    st.session_state.shopping_carts, 
                    st.session_state.show_all_carts, 
                    st.session_state.user_lat,  # Übergeben Sie user_lat an display_carts
                    st.session_state.user_lng   # Übergeben Sie user_lng an display_carts
                )
        else:
            st.error("Benutzerkoordinaten sind nicht verfügbar. Bitte gebe Deine Adresse ein und suche nach Supermärkten.")

if __name__ == '__main__':
    app()
 