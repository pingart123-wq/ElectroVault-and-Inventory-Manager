import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any

# --- CONFIGURATION & SETUP ---

# 1. Page Configuration (Equivalent to HTML <head> and initial body style)
st.set_page_config(
    page_title="ElectroVault | Inventory Manager",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# 2. Define Theme and Custom CSS (Mimics the CSS styles)
CUSTOM_CSS = """
:root {
    --bg-dark: #0a0b10;
    --panel-bg: #13141c;
    --accent-cyan: #00f3ff;
    --accent-purple: #bc13fe;
    --text-main: #e0e6ed;
    --text-muted: #94a3b8;
    --danger: #ff2a6d;
    --success: #05d5fa;
}

/* Background & Body Styles */
html, body {
    color: var(--text-main);
    font-family: 'Rajdhani', sans-serif;
}
.stApp {
    background-color: var(--bg-dark);
    /* Mimic the subtle background gradient */
    background-image: radial-gradient(circle at 10% 20%, rgba(188, 19, 254, 0.1) 0%, transparent 20%), 
                      radial-gradient(circle at 90% 80%, rgba(0, 243, 255, 0.1) 0%, transparent 20%);
}

/* Sidebar Custom Styling (Streamlit overwrites often) */
.css-hxt7ge { /* Targets the sidebar container */
    background: var(--panel-bg) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
/* Streamlit's default header elements for better contrast */
h1, h2, h3, .st-bh, .st-b5, .st-cc {
    font-family: 'Orbitron', sans-serif !important;
    color: white !important;
}

/* Custom Component Styles (to match original CSS) */

/* Logo - Replaced by st.sidebar.title */

/* Navigation/Sidebar Item Active State - Streamlit handles this better with radio/selectbox */

/* Stats Cards (st.metric container) */
div[data-testid="stMetric"], .stat-card-custom {
    background: rgba(255, 255, 255, 0.03); 
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 20px; 
    border-radius: 15px; 
    overflow: hidden;
    margin-bottom: 20px;
    position: relative;
    border-left: 4px solid var(--accent-cyan);
}
/* Custom left border colors for the other two cards */
.purple-border { border-left-color: var(--accent-purple) !important; }
.danger-border { border-left-color: var(--danger) !important; }

/* Item Card Grid Container */
.inventory-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

/* Item Card (st.container) */
.item-card {
    background: var(--panel-bg); 
    border-radius: 16px; 
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.05); 
    transition: 0.3s;
    /* Streamlit doesn't easily allow hover effects on container itself, 
       but we can style the contents */
}
.item-icon { 
    width: 50px; height: 50px; 
    background: rgba(0, 243, 255, 0.1); 
    border-radius: 12px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    color: var(--accent-cyan); 
    font-size: 1.5rem; 
    margin-bottom:10px; 
}

/* Analytics Bar Chart Fill */
.bar-bg { 
    background: rgba(255,255,255,0.1); 
    height: 10px; 
    border-radius: 10px; 
    overflow: hidden; 
}
.bar-fill { 
    height: 100%; 
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
    transition: width 1s ease; 
}
.low-stock { color: var(--danger) !important; font-weight: 700; }

/* Settings Buttons */
.btn-export { background: rgba(0, 243, 255, 0.1); color: var(--accent-cyan); border: 1px solid var(--accent-cyan); padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; }
.btn-danger { background: rgba(255, 42, 109, 0.1); color: var(--danger); border: 1px solid var(--danger); padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; }
"""

# Apply the custom CSS
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# 3. Data Storage Path and Defaults
DATA_PATH = Path("electrovault_inventory.json")

DEFAULT_INVENTORY = [
    {'id': 1, 'name': "GeForce RTX 4090", 'category': "GPU", 'price': 1599.99, 'qty': 3},
    {'id': 2, 'name': "MacBook Pro M2", 'category': "Laptop", 'price': 2499.00, 'qty': 8},
    {'id': 3, 'name': "Samsung S24 Ultra", 'category': "Mobile", 'price': 1199.50, 'qty': 12},
    {'id': 4, 'name': "Sony WH-1000XM5", 'category': "Accessory", 'price': 348.00, 'qty': 25},
]

CATEGORY_ICONS = {
    'GPU': '🧠', 'CPU': '💻', 'Mobile': '📱',
    'Laptop': '🖥️', 'Accessory': '🎧', 'Other': '📦'
}

# --- DATA MANAGEMENT FUNCTIONS ---

@st.cache_data(show_spinner=False)
def load_data():
    """Loads inventory from JSON file or uses defaults."""
    if DATA_PATH.exists():
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    return DEFAULT_INVENTORY

def save_data(data: List[Dict[str, Any]]):
    """Saves inventory to JSON file."""
    with open(DATA_PATH, 'w') as f:
        json.dump(data, f, indent=4)
    # Clear cache so next load gets fresh data
    load_data.clear()

def initialize_session_state():
    """Initializes Streamlit session state for data and navigation."""
    if 'inventory' not in st.session_state:
        st.session_state['inventory'] = load_data()
    if 'current_view' not in st.session_state:
        st.session_state['current_view'] = 'Inventory'

# --- UI COMPONENTS (Inventory View) ---

def render_inventory_view():
    st.markdown("## Inventory Management")
    
    # Header/Search/Add Button
    col1, col2 = st.columns([3, 1])
    with col1:
        # Search Box (replaces the JS filter)
        search_term = st.text_input("Search components...", placeholder="Search name or category...", label_visibility="collapsed")
    with col2:
        # Add Item Button (replaces the HTML button and openModal JS)
        if st.button("➕ ADD ITEM", use_container_width=True, help="Add a new component to the vault"):
            st.session_state['show_modal'] = True
    
    # Filtering Logic
    inventory_data = st.session_state['inventory']
    if search_term:
        term = search_term.lower()
        filtered_inventory = [
            item for item in inventory_data 
            if term in item['name'].lower() or term in item['category'].lower()
        ]
    else:
        filtered_inventory = inventory_data

    # Calculate Stats
    total_items = sum(item['qty'] for item in inventory_data)
    total_value = sum(item['price'] * item['qty'] for item in inventory_data)
    low_stock_count = len([item for item in inventory_data if item['qty'] < 5])

    # Stats Cards (Replaces the .stats-container)
    st.markdown("---")
    scol1, scol2, scol3 = st.columns(3)
    
    with scol1:
        st.markdown('<div class="stat-card-custom">', unsafe_allow_html=True)
        st.metric("Total Items", f"{total_items}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with scol2:
        st.markdown('<div class="stat-card-custom purple-border">', unsafe_allow_html=True)
        st.metric("Inventory Value", f"${total_value:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with scol3:
        st.markdown('<div class="stat-card-custom danger-border">', unsafe_allow_html=True)
        st.metric("Low Stock Alerts", f"{low_stock_count}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Inventory Grid (Replaces the .inventory-grid and renderInventory JS)
    st.markdown('<div class="inventory-grid">', unsafe_allow_html=True)
    
    if not filtered_inventory:
        st.markdown(
            '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 50px;">'
            'No items found matching the search criteria or the vault is empty.'
            '</div>', 
            unsafe_allow_html=True
        )
    else:
        # Use Streamlit columns to create the grid layout
        grid_cols = st.columns(3) # Use three columns for a clean grid on wide screens
        
        for i, item in enumerate(filtered_inventory):
            col = grid_cols[i % 3]
            
            with col:
                stock_class = 'low-stock' if item['qty'] < 5 else ''
                icon = CATEGORY_ICONS.get(item['category'], '📦')
                
                # Using st.container and markdown to simulate the .item-card
                st.markdown(f"""
                <div class="item-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="item-icon">{icon}</div>
                        <span style="color:var(--accent-purple); font-size:0.8rem; font-weight:700;">{item['category']}</span>
                    </div>
                    <h3 class="item-name" style="margin: 0; padding-bottom: 5px;">{item['name']}</h3>
                    <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin: 15px 0;">
                        <div><small style="color:#94a3b8">Price</small><br>**${item['price']:,.2f}**</div>
                        <div style="text-align:right"><small style="color:#94a3b8">Stock</small><br><span class="{stock_class}">{item['qty']}</span></div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn-action btn-delete" 
                                onclick="Streamlit.setComponentValue({{ type: 'delete', id: {item['id']} }})" 
                                style="width: 100%; border: none; padding: 8px; border-radius: 6px; cursor: pointer; font-weight: 600;">
                            DELETE
                        </button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # NOTE: Streamlit buttons cannot directly run Python functions inside markdown,
                # so the JS delete functionality is replaced by a standard Streamlit button 
                # placed outside the markdown block, and given a unique key.
                if st.button("DELETE", key=f"delete_{item['id']}", use_container_width=True, 
                             type="secondary", help=f"Permanently delete {item['name']}"):
                    delete_item(item['id'])
                    # Re-run the app to reflect changes
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # Close inventory-grid


# --- UI COMPONENTS (Analytics View) ---

def render_analytics_view():
    st.markdown("<h1 style='font-family: Orbitron; margin-bottom: 20px; color: white;'>System Diagnostics</h1>", unsafe_allow_html=True)
    st.markdown("---")

    inventory_data = st.session_state['inventory']

    if not inventory_data:
        st.info("No items in the vault to generate analytics.")
        return

    df = pd.DataFrame(inventory_data)
    df['total_value'] = df['price'] * df['qty']
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Inventory Value Distribution")
        
        category_stats = df.groupby('category')['total_value'].sum().sort_values(ascending=False)
        total_val = category_stats.sum()
        
        # Bar Chart Visualization (Mimics the CSS bar chart)
        category_chart_html = ""
        for cat, val in category_stats.items():
            percent = (val / total_val) * 100 if total_val > 0 else 0
            category_chart_html += f"""
                <div class="chart-bar-group">
                    <div class="bar-label">
                        <span>{cat}</span>
                        <span>${val:,.2f} ({percent:.1f}%)</span>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width: {percent}%;"></div>
                    </div>
                </div>
            """
        st.markdown(category_chart_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Most Expensive Assets")
        
        # Top 5 most expensive items
        sorted_items = df.sort_values(by='price', ascending=False).head(5)
        
        expensive_list_html = ""
        for index, item in sorted_items.iterrows():
            expensive_list_html += f"""
                <div class="top-list-item">
                    <div style="font-weight:bold">{item['name']}</div>
                    <div style="color:var(--accent-cyan)">${item['price']:,.2f}</div>
                </div>
            """
        st.markdown(expensive_list_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- UI COMPONENTS (Settings View) ---

def render_settings_view():
    st.markdown("<h1 style='font-family: Orbitron; margin-bottom: 20px; color: white;'>System Configuration</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Export Database
    st.markdown('<div class="setting-card">', unsafe_allow_html=True)
    st.subheader("Export Database")
    st.markdown("Download your current inventory as a JSON file.")
    if st.button("⬇️ EXPORT DATA", key="btn_export", help="Download a JSON backup", use_container_width=True):
        export_data()
    st.markdown('</div>', unsafe_allow_html=True)

    # System Purge
    st.markdown(f'<div class="setting-card" style="border-color: rgba(255, 42, 109, 0.3);">', unsafe_allow_html=True)
    st.markdown(f'<h3 style="color: var(--danger); font-family: Orbitron;">System Purge</h3>', unsafe_allow_html=True)
    st.markdown("Permanently delete all inventory records.")
    if st.button("🗑️ PURGE ALL", key="btn_purge", type="primary", help="Permanently delete ALL records", use_container_width=True):
        if st.warning("Are you sure you want to PERMANENTLY delete ALL inventory data? This cannot be undone.", icon="⚠️"):
             if st.button("CONFIRM PURGE", key="confirm_purge"):
                clear_data()
                st.success("System Purged. Memory cleared.")
                st.rerun() # Refresh app after purge
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; color: var(--text-muted); margin-top: 30px;">'
                '<small>ElectroVault System v1.0.4 <br> Secure Connection Established</small>'
                '</div>', unsafe_allow_html=True)

# --- MODAL/FORM LOGIC ---

def add_item_form():
    """Handles the Add Item Modal logic."""
    if 'show_modal' in st.session_state and st.session_state['show_modal']:
        # This replaces the modal overlay with a Streamlit form/popover in a fixed position
        # For simplicity and Streamlit best practices, we'll use st.form
        st.sidebar.markdown("---")
        with st.sidebar.form("add_item_form", clear_on_submit=True):
            st.subheader("New Component")
            
            # Form Inputs (Replaces the <input> and <select> fields)
            name = st.text_input("Item Name", placeholder="e.g. RTX 4090", key="itemName")
            category = st.selectbox("Category", options=list(CATEGORY_ICONS.keys()), key="itemCategory")
            
            col_price, col_qty = st.columns(2)
            with col_price:
                price = st.number_input("Price ($)", min_value=0.01, step=0.01, format="%.2f", key="itemPrice")
            with col_qty:
                qty = st.number_input("Quantity", min_value=1, step=1, key="itemQty")
            
            submitted = st.form_submit_button("ADD TO VAULT", type="primary")

            if submitted:
                # Add item logic (replaces addItem JS function)
                if name and price and qty:
                    new_id = max([item['id'] for item in st.session_state['inventory']]) + 1 if st.session_state['inventory'] else 1
                    
                    new_item = {
                        'id': new_id,
                        'name': name,
                        'category': category,
                        'price': price,
                        'qty': qty
                    }
                    st.session_state['inventory'].insert(0, new_item)
                    save_data(st.session_state['inventory'])
                    st.session_state['show_modal'] = False
                    st.success(f"Added {name} to the vault!")
                    st.rerun() # Re-run to refresh the inventory view
                else:
                    st.error("Please fill out all fields.")

# --- DATA MANIPULATION FUNCTIONS (REACTIVE) ---

def delete_item(item_id: int):
    """Deletes an item and updates storage."""
    st.session_state['inventory'] = [item for item in st.session_state['inventory'] if item['id'] != item_id]
    save_data(st.session_state['inventory'])
    st.success(f"Item ID {item_id} successfully purged.")
    load_data.clear()

def export_data():
    """Exports data as JSON file (replaces the JS exportData function)"""
    data_to_export = json.dumps(st.session_state['inventory'], indent=4)
    st.download_button(
        label="Download Inventory JSON",
        data=data_to_export,
        file_name="electrovault_inventory.json",
        mime="application/json"
    )

def clear_data():
    """Clears all data (replaces the JS clearData function)"""
    st.session_state['inventory'] = []
    save_data(st.session_state['inventory'])

# --- MAIN APPLICATION LOGIC ---

def main():
    initialize_session_state()

    # --- Sidebar (Navigation and Logo) ---
    with st.sidebar:
        # Logo (Replaces the .logo HTML div)
        st.markdown(f"""
            <div style="font-family: 'Orbitron', sans-serif; font-size: 1.5rem; color: var(--accent-cyan); 
                        margin-bottom: 3rem; text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);">
                <i class="fa-solid fa-microchip"></i> ELECTRO<b>VAULT</b>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation (Replaces the .nav-item divs and switchView JS)
        view_options = ['Inventory', 'Analytics', 'Settings']
        st.session_state['current_view'] = st.radio(
            "Navigation", 
            options=view_options, 
            index=view_options.index(st.session_state['current_view']),
            label_visibility="collapsed"
        )
        
        # The Add Item Modal is shown in the sidebar if triggered
        add_item_form()

    # --- Main Content Renderer (Replaces the .main-content and .view-section divs) ---
    
    if st.session_state['current_view'] == 'Inventory':
        render_inventory_view()
    elif st.session_state['current_view'] == 'Analytics':
        render_analytics_view()
    elif st.session_state['current_view'] == 'Settings':
        render_settings_view()

if __name__ == '__main__':
    # Ensure all Font Awesome icons are available for the markdown elements
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
    
    # Run the main application
    main()