from site import makepath
import streamlit as st
import datetime
import pandas as pd
import os
import geocoder
import random
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Dark Theme CSS with Improved Readability ---
st.markdown("""
    <style>
        body, .stApp {
            background-color: #1e1e2f;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #12131a;
        }
        .block-container {
            background-color: #1e1e2f;
        }
        h1, h2, h3, h4, h5 {
            color: #4DD0E1;
        }
        .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div div div {
            background-color: #2c2f4a;
            color: white;
            border: 1px solid #4DD0E1;
            border-radius: 6px;
        }
        .stButton>button {
            background-color: #4DD0E1;
            color: #000;
            font-weight: bold;
            border-radius: 10px;
            transition: 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #00bcd4 !important;
            transform: scale(1.03);
        }
        .stFileUploader, .stDataFrame {
            background-color: #2c2f4a !important;
            color: white;
        }
         .popup {
            animation: slide 1s ease-in-out;
            background: #00BCD4;
            color: #000;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 0 15px #00BCD4;
        }
        @keyframes slide {
            from {transform: translateY(-100px); opacity: 0;}
            to {transform: translateY(0); opacity: 1;} }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("🛠 Smart C&D Waste Tracker")
section = st.sidebar.radio("🧭 Navigate to:", [
    "🏠 Dashboard", 
    "🗃 Log Waste",
    "♻ Reuse Requests",
    "♻ Recycling Station", 
    "♻ Recycle Inventory",
    "📊 Analytics", 
    "🔐 Admin Panel"
])

# --- Section: Dashboard--- 
SENDER_EMAIL= "anujshrivastav9540@gmail.com"
SENDER_PASSWORD="vllksvkldfkntccg"
if section == "🏠 Dashboard":
    st.markdown("""
        <div class="popup">🎯 Welcome to DMRC’s Intelligent C&D Waste Tracker</div>
        <div style='background-color:#2c2f4a;padding:25px;border-radius:15px;text-align:center; margin-top: 15px;'>
            <h1>🚧 Smart C&D Waste Tracker - DMRC</h1>
            <p>Empowering Delhi Metro with intelligent & sustainable construction waste management.</p>
            <hr style='border:1px solid #00BCD4;'>
            <p>🚇 <b>Goal:</b> Ensure zero-waste sites and promote maximum reuse/recycle potential.</p>

        </div>
    """, unsafe_allow_html=True)

# --- Section: Log Waste ---
      
elif section == "🗃 Log Waste":
    st.subheader("📝 Log New C&D Waste Entry 🧱🚧")

    st.markdown("### 🏗 Who's Generating the Waste?")
    generators = st.multiselect("👷‍♂ Select Generator(s)", ["🏢 DMRC", "🏛 PWD", "🏗 NBCC", "🚜 L&T", "♻ Recycle Station"])

    st.markdown("### ♻ What's in the Waste?")
    waste_types = st.multiselect("🔍 Select Material Type(s)", ["Concrete", "Steel", "Wood", "Soil", "Sand", "Rubber", "Mixed"])

    other_waste = ""
    if "🎲 Mixed" in waste_types:
        other_waste = st.text_input("🆕 Got something else? Specify it here:")

    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("📍 Where was it generated?", placeholder="e.g., DMRC Hauz Khas Metro Site")
    with col2:
        entry_date = st.date_input("📅 Date of Generation", value=datetime.date.today())

    # 🌐 Auto location
    g = geocoder.ip('me')
    latitude, longitude = g.latlng if g.latlng else (None, None)
    locality = g.city if g.city else "UNKNOWN"

    st.success(f"📡 Auto-location Detected: {locality}")
    st.caption(f"🌍 Coordinates: {latitude}, {longitude}")

    # 🔐 Auto Waste ID
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    locality_tag = locality[:3].upper() if locality != "UNKNOWN" else "LOC"
    waste_id = f"CNDW-{date_str}-{locality_tag}-{random.randint(1000, 9999)}"
    st.text_input("🆔 Waste Entry ID", value=waste_id, disabled=True)

    contactor_name = st.text_input("🧑‍🔧 Contractor / Supervisor", placeholder="e.g., Mr. Anuj Shrivastav 👷‍♂")
    email = st.text_input("📧 Contractor Email", placeholder="e.g., anujshrivastav@example.com")
    phone = st.text_input("📱 Contractor Phone Number", placeholder="+91xxxxxxxxxx")

    # 📸 Multiple Image Upload
    uploaded_images = st.file_uploader("Upload Waste Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    image_paths = []

    if uploaded_images:
        if not os.path.exists("images"):
            os.makedirs("images")

        for img in uploaded_images:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            ext = img.name.split('.')[-1]
            safe_name = f"{waste_id}_{random.randint(100,999)}.{ext}"
            path = os.path.join("images", safe_name)

            with open(path, "wb") as f:
                f.write(img.getbuffer())

            image_paths.append(path)

        st.success(f"✅ {len(uploaded_images)} image(s) uploaded successfully!")

    # ⚖ Waste Quantity Inputs
    st.markdown("### ⚖ Let's Weigh the Waste!")
    quantities = {}
    for wt in waste_types:
        label = other_waste if wt == "🎲 Mixed" and other_waste.strip() else wt.replace("🪨 ", "").replace("🔩 ", "").replace("🪵 ", "").replace("🟫 ", "").replace("🏖 ", "").replace("🛞 ", "").replace("🎲 ", "")
        qty = st.number_input(f"{label} (kg)", min_value=0, step=1, key=label)
        quantities[label] = qty

    total_qty_kg = sum(quantities.values())
    total_qty_ton = total_qty_kg / 1000
    st.info(f"📦 Estimated Quantity: {total_qty_kg} kg / {total_qty_ton:.2f} tons")

    if total_qty_kg > 500:
        st.warning("🚨 That’s a lot of waste! Coordinate with ♻ Recycle Station A/B immediately!")

    # 💸 Market Value Calculation
    type_based_value = {
      "Concrete": 2.5,     # average of 1.6–3.3
      "Steel": 50,         # average of 45–55
      "Steel scrap": 25,   # average of 23–28 (if scrap)
      "Bricks": 0.1,       # based on 8–12 paise/kg approximation
      "Wood": 40,          # rough market-grade estimate
      "Soil": 2,           # assumed low-grade
      "Sand": 2.5,         # same as concrete aggregate
      "Rubber": 5,  
      "Mixed": 3
    }
    estimated_market_value = 0
    for wt_name, wt_qty in quantities.items():
        rate = type_based_value.get(wt_name, 3)
        estimated_market_value += wt_qty * rate

    # 🚀 Submission
    if st.button("🚀 Blast Off! Submit Waste Entry"):
        if waste_types and location:
            row = {
                "Waste ID": waste_id,
                "Date": entry_date.strftime("%Y-%m-%d"),
                "Location": location,
                "Locality": locality,
                "Latitude": latitude,
                "Longitude": longitude,
                "Contractor": contactor_name,
                "Generators": ", ".join(generators),
                "Waste Types": ", ".join(waste_types),
                "Other Waste": other_waste,
                "Total Quantity (kg)": total_qty_kg,
                "Total Quantity (tons)": total_qty_ton,
                "Email": email,
                "Phone": phone,
                "Status": "Pending",
                "Remarks": "-",
                "Image": ";".join(image_paths)
            }
            row.update(quantities)
            row["Market Value"] = estimated_market_value

            try:
                old_df = pd.read_csv("waste_log.csv")
                df = pd.concat([old_df, pd.DataFrame([row])], ignore_index=True)
            except FileNotFoundError:
                df = pd.DataFrame([row])

            df.to_csv("waste_log.csv", index=False)
            st.markdown("<div class='popup'>🎉 Entry Logged Successfully!</div>", unsafe_allow_html=True)
            #st.balloons()


            # ✅ Notifications
            try:
                from notifications import send_email, send_sms  # Ensure this module exists

                if email:
                    send_email(
                        to_email=email,
                        subject="✅ Waste Log Submitted",
                        content=f"""
Hi {contactor_name},

Your waste entry has been successfully logged.

🆔 Waste ID: {waste_id}
📍 Location: {location}
📦 Quantity: {total_qty_kg} kg

You can track status from the portal.

Thanks,  
DMRC C&D Tracker Team
"""
                    )

                if phone:
                    send_sms(
                        to_number=phone,
                        body_text=f"✅ C&D Entry {waste_id} submitted. Qty: {total_qty_kg}kg @ {location}."
                    )

            except Exception as e:
                st.error(f"📤 Notification failed: {e}")

        else:
            st.markdown("<div class='popup' style='background-color:#ff5722;'>❌ Waste Type & Location Required!</div>", unsafe_allow_html=True)



# --- Section: Reuse Requests ---
elif section == "♻ Reuse Requests":
    st.subheader("♻ Reuse Market – Place Your Bids on Approved Waste")

    try:
        df = pd.read_csv("waste_log.csv")
        approved_df = df[df["Status"] == "Approved"]

        # Create reuse_bids.csv if it doesn't exist
        if not os.path.exists("reuse_bids.csv"):
            bids_df = pd.DataFrame(columns=["Waste ID", "Bidder", "Email", "Contact", "Bid Price", "Message", "Timestamp", "Status"])
            bids_df.to_csv("reuse_bids.csv", index=False)

        bids_df = pd.read_csv("reuse_bids.csv")

        if approved_df.empty:
            st.info("🚫 No approved waste entries available for reuse.")
        else:
            for index, row in approved_df.iterrows():
                with st.expander(f"🧱 Waste ID: {row['Waste ID']} | Location: {row['Location']} | Qty: {row['Total Quantity (kg)']} kg"):
                    st.write(f"📅 Date: {row['Date']}")
                    st.write(f"📦 Materials: {row['Waste Types']}")
                    st.write(f"📍 Locality: {row['Locality']}")

                    # 🔍 Show all images (if present)
                    if "Image" in row and pd.notna(row["Image"]):
                        image_paths = row["Image"].split(";")
                        for img_path in image_paths:
                            img_path = img_path.strip()
                            if os.path.exists(img_path):
                                st.image(img_path, caption="📷 Waste Image", width=250)

                    st.markdown("### 💰 Submit Your Bid")
                    with st.form(f"bid_form_{index}"):
                        bidder = st.text_input("👤 Your Name", key=f"name_{index}")
                        email = st.text_input("📧 Your Email", key=f"email_{index}")
                        contact = st.text_input("📞 Contact Number", key=f"contact_{index}")
                        bid_rate = st.number_input("💸 Rate You Offer (₹ per kg)", min_value=1.0, step=0.5, key=f"rate_{index}")
                        try:
                            total_qty =float(row["Total Quantity (kg)"])
                        except:
                            total_qty=0.0

                        bid_price= bid_rate*total_qty
                        st.info(f"🧮 Total Bid Amount: ₹{bid_price:.2f}")
                        message = st.text_area("✉ Message (Optional)", key=f"msg_{index}")
                        submit_bid = st.form_submit_button("📤 Submit Bid")

                        if submit_bid and bidder and contact and email and bid_price:
                            new_bid = {
                                "Waste ID": row["Waste ID"],
                                "Bidder": bidder,
                                "Email": email,
                                "Contact": contact,
                                "Bid Price": bid_price,
                                "Bid Rate (₹/kg)": bid_rate,
                                "Message": message,
                                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Status": "Pending"
                            }

                            bids_df = pd.concat([bids_df, pd.DataFrame([new_bid])], ignore_index=True)
                            bids_df.to_csv("reuse_bids.csv", index=False)
                            st.success("✅ Your bid has been submitted!")

                            # 🔔 Optional Email Notification
                            try:
                                from notifications import send_email

                                send_email(
                                    to_email=email,
                                    subject="✅ Reuse Bid Submitted Successfully",
                                    content=f"""
Hi {bidder},

Thank you for submitting your bid for the following C&D waste:

🆔 Waste ID: {row['Waste ID']}
📍 Location: {row['Location']}
📦 Quantity: {row['Total Quantity (kg)']} kg
💰 Your Bid: ₹{bid_price}

Our team will review your bid and contact you upon approval.

Thanks,  
DMRC C&D Reuse Team
"""
                                )
                            except Exception as e:
                                st.warning(f"📤 Email notification failed: {e}")

                    # Show all bids for this Waste ID
                    st.markdown("### 📋 All Bids for This Waste")
                    waste_bids = bids_df[bids_df["Waste ID"] == row["Waste ID"]]
                    if not waste_bids.empty:
                        highest = waste_bids.loc[waste_bids["Bid Price"].idxmax()]
                        st.success(f"🔝 Highest Bid: ₹{highest['Bid Price']} by {highest['Bidder']}")
                        st.dataframe(waste_bids.sort_values("Bid Price", ascending=False))
                    else:
                        st.info("🕐 No bids yet for this item.")

    except Exception as e:
        st.error(f"❌ Error loading reuse section: {e}")

elif section == "♻ Recycling Station":
    st.header("♻ Auto-Recycled Waste Inventory")
    st.caption("This section shows all waste entries that were auto-diverted to the recycling station.")

    try:
        recycle_df = pd.read_csv("recycling_station.csv")

        if recycle_df.empty:
            st.info("No items currently in the recycling station.")
        else:
           
            filtered_df = recycle_df 

            st.markdown(f"### ♻ {len(filtered_df)} items found")
            for index, row in filtered_df.iterrows():
                with st.container(border=True):
                    st.markdown(f"🆔 Waste ID: {row['Waste ID']}")
                    st.markdown(f"📍 Location: {row['Location']} | 🗓 **Date: {row['Date']}")
                    st.markdown(f"📦 Waste Types: {row['Waste Types']}")
                    st.markdown(f"⚖ Quantity: {row['Total Quantity (kg)']} kg / {row['Total Quantity (tons)']} tons")
                   # st.markdown(f"💰 Market Value: ₹{row['Market Value']}")
                    st.markdown(f"📝 Remarks: {row['Remarks']}")
                    st.markdown(f"♻ Recycled On: {row['Recycled On']}")

                    # Show image if available
                    if "Image" in row and pd.notna(row["Image"]):
                        img_paths = row["Image"].split(";")
                        for img_path in img_paths:
                            if os.path.exists(img_path.strip()):
                                st.image(img_path.strip(), width=300)
    except FileNotFoundError:
        st.warning("⚠ No recycling data available yet.")
    except Exception as e:
        st.error(f"❌ Error loading recycling data: {e}")




elif section == "♻ Recycle Inventory":
    st.markdown("## ♻ Recycle Inventory Dashboard")
    st.markdown("Welcome to the Recycle Inventory Portal. Here, admins can upload recycled items 📤 and users can browse available materials 🛍 for reuse.")
    st.markdown("---")

    tabs = st.tabs(["🛠 Admin Upload", "🛍 Browse & Request"])

    with tabs[0]:
        st.markdown("### 📅 Upload Recycled Material (Admin Only)")
        st.info("Admins can upload items that are available for reuse after recycling. Fill all fields and attach a photo.")

        category_options = ["🧱 Concrete", "⚙ Steel", "🩵 Wood", "🪨 Soil", "♻ Others"]

        item_id = st.text_input("🆔 Enter Item ID")
        item_name = st.text_input("📦 Item Name")
        category = st.selectbox("📂 Category", category_options)
        quantity = st.number_input("📏 Quantity (kg)", min_value=1)
        location = st.text_input("📍 Location (Depot / Yard / Site)")
        condition = st.selectbox("🔧 Condition", ["✅ Good", "⚠ Fair"])
        image_file = st.file_uploader("🖼 Upload Image", type=["png", "jpg", "jpeg"])

        if st.button("➕ Add to Inventory"):
            if item_id and item_name and image_file:
                os.makedirs("uploaded_images", exist_ok=True)
                image_path = f"uploaded_images/{item_id}_{image_file.name}"
                with open(image_path, "wb") as f:
                    f.write(image_file.getbuffer())

                new_entry = {
                    "Item ID": item_id,
                    "Item Name": item_name,
                    "Category": category,
                    "Quantity (kg)": quantity,
                    "Location": location,
                    "Condition": condition,
                    "Image": image_path,
                    "Date Added": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "Status": "Available"
                }

                df = pd.DataFrame([new_entry])
                if os.path.exists("recycle_inventory.csv"):
                    df.to_csv("recycle_inventory.csv", mode="a", header=False, index=False)
                else:
                    df.to_csv("recycle_inventory.csv", index=False)

                st.success("✅ Item successfully added to recycle inventory!")
            else:
                st.warning("⚠ Please fill all fields and upload an image!")

        st.markdown("---")
        st.markdown("### 💰 Manage Bids and Sell to Highest Bidder")

        try:
            bid_df = pd.read_csv("recycle_requests.csv")

            if bid_df.empty:
                st.info("📬 No bids submitted yet.")
            else:
                unique_items = bid_df[bid_df["Status"] != "Accepted"]["Item ID"].unique()
                selected_item = st.selectbox("📦 Select Item ID to Review Bids", unique_items)

                item_bids = bid_df[(bid_df["Item ID"] == selected_item) & (bid_df["Status"] == "Pending")]
                item_bids = item_bids.sort_values(by="Offered Price", ascending=False).reset_index(drop=True)

                st.dataframe(item_bids[["Name", "Email", "Requested Quantity", "Offered Price", "Purpose", "Status"]])

                if not item_bids.empty:
                    top_bid = item_bids.iloc[0]
                    st.success(f"🏆 Highest Bidder: {top_bid['Name']} offering ₹{top_bid['Offered Price']}")

                    if st.button("✅ Sell to Highest Bidder"):
                        try:
                            bid_df.loc[(bid_df["Item ID"] == selected_item) & (bid_df["Email"] == top_bid["Email"]), "Status"] = "Accepted"
                            bid_df.loc[(bid_df["Item ID"] == selected_item) & (bid_df["Email"] != top_bid["Email"]), "Status"] = "Rejected"
                            bid_df.to_csv("recycle_requests.csv", index=False)

                            try:
                                inv_df = pd.read_csv("recycle_inventory.csv")
                                inv_df.loc[inv_df["Item ID"] == selected_item, "Status"] = "Sold"
                                inv_df.to_csv("recycle_inventory.csv", index=False)
                            except Exception as e:
                                st.warning(f"⚠ Couldn't update inventory status: {e}")

                            receiver_email = top_bid["Email"]
                            subject = f"🎉 Bid Accepted: {top_bid['Item Name']}"
                            body = f"""Dear {top_bid['Name']},

Congratulations! Your bid of ₹{top_bid['Offered Price']} for item {top_bid['Item Name']} (ID: {selected_item}) has been accepted.

We'll contact you shortly for next steps.

Thank you for contributing to circular construction! 🌱

— Team DMRC"""

                            message = MIMEMultipart()
                            message["From"] = SENDER_EMAIL
                            message["To"] = receiver_email
                            message["Subject"] = subject
                            message.attach(MIMEText(body, "plain"))

                            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                server.starttls()
                                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                                server.send_message(message)

                            st.success("✅ Sale confirmed! Highest bidder notified by email.")

                        except Exception as e:
                            st.error(f"❌ Error: {e}")

        except FileNotFoundError:
            st.warning("⚠ No recycle_requests.csv found.")
        except Exception as e:
            st.error(f"❌ Error reading bid data: {e}")

    with tabs[1]:
        st.markdown("### 🛍 Browse Available Recycled Materials")
        st.info("You can explore and request reused items for eco-friendly construction 🌱")

        try:
            inv_df = pd.read_csv("recycle_inventory.csv")

            filter_category = st.selectbox("🔍 Filter by Category", ["All"] + category_options)
            filter_location = st.selectbox("📍 Filter by Location", ["All"] + sorted(inv_df["Location"].unique()))

            filtered_df = inv_df.copy()
            if filter_category != "All":
                filtered_df = filtered_df[filtered_df["Category"] == filter_category]
            if filter_location != "All":
                filtered_df = filtered_df[filtered_df["Location"] == filter_location]

            if filtered_df.empty:
                st.warning("🛜 No items found for selected filters.")
            else:
                st.markdown("#### 🗰 Matching Items")
                for idx, row in filtered_df.iterrows():
                    with st.container(border=True):
                        with st.expander(f"📦 {row['Item Name']} (ID: {row['Item ID']})", expanded=False):
                            cols = st.columns([2, 3])
                            with cols[0]:
                                if os.path.exists(row["Image"]):
                                    st.image(row["Image"], use_container_width=True)
                                else:
                                    st.warning("❌ Image not found.")
                            with cols[1]:
                                st.markdown(f"📂 Category: {row['Category']}")
                                st.markdown(f"📏 Quantity: {row['Quantity (kg)']} kg")
                                st.markdown(f"📍 Location: {row['Location']}")
                                st.markdown(f"🔧 Condition: {row['Condition']}")

                                status = row.get("Status", "Available")
                                if status == "Sold":
                                    st.error("🔴 SOLD OUT")
                                else:
                                    with st.form(key=f"form_{idx}"):
                                        name = st.text_input("👤 Your Name", key=f"name_{idx}")
                                        email = st.text_input("📧 Email", key=f"email_{idx}")
                                        phone = st.text_input("📞 Phone", key=f"phone_{idx}")
                                        req_qty = st.number_input("📦 Requested Quantity (kg)", 1, int(row["Quantity (kg)"]), key=f"qty_{idx}")
                                        offer_price = st.number_input("💵 Offered Price (₹)", min_value=0, key=f"price_{idx}")
                                        reason = st.text_area("✍ Purpose / Notes", key=f"reason_{idx}")

                                        submitted = st.form_submit_button("🚚 Submit Request")
                                        if submitted:
                                            request_data = {
                                                "Timestamp": datetime.datetime.now(),
                                                "Item ID": row["Item ID"],
                                                "Item Name": row["Item Name"],
                                                "Requested Quantity": req_qty,
                                                "Offered Price": offer_price,
                                                "Name": name,
                                                "Email": email,
                                                "Phone": phone,
                                                "Purpose": reason,
                                                "Status": "Pending"
                                            }

                                            req_df = pd.DataFrame([request_data])
                                            if os.path.exists("recycle_requests.csv"):
                                                req_df.to_csv("recycle_requests.csv", mode="a", header=False, index=False)
                                            else:
                                                req_df.to_csv("recycle_requests.csv", index=False)

                                            st.success("✅ Request submitted!")

        except Exception as e:
            st.error(f"❌ Error loading inventory: {e}")

# 📊 ANALYTICS SECTION  
elif section == "📊 Analytics":
    st.header("📊 Waste Analytics Dashboard")

    # Create 3 tabs
    tab1, tab2, tab3 = st.tabs(["🧾 Waste Log", "🌱 CO₂ Savings", "💰 Cost Savings"])

    with tab1:
        st.subheader("📊 Waste Submission Records")
        try:
            df = pd.read_csv("waste_log.csv")
            filtered_df = df[df["Status"].isin(["Approved", "Sold", "Recycled"])]
            st.success("✅ Waste log loaded successfully.")

            st.markdown("### 📈 Summary Stats")
            total_records = len(filtered_df)
            total_qty_kg = filtered_df['Total Quantity (kg)'].sum() if 'Total Quantity (kg)' in filtered_df.columns else 0
            total_qty_ton = filtered_df['Total Quantity (tons)'].sum() if 'Total Quantity (tons)' in filtered_df.columns else 0
            unique_locations = filtered_df['Location'].nunique() if 'Location' in filtered_df.columns else 0

            col1, col2 = st.columns(2)
            with col1:
                st.metric("📁 Total Records", total_records)
                st.metric("📈 Total Waste in Tons", f"{total_qty_ton:.2f} tons")
            with col2:
                st.metric("🚚 Total Waste Logged in kg", f"{total_qty_kg} kg")
                st.metric("📍 Active Locations", unique_locations)

        except Exception as e:
            st.error(f"⚠ Data Load Failed: {e}")

        else:
            with st.expander("🔍 View Full Waste Log Table"):
                st.dataframe(filtered_df)

            st.markdown("---")
            st.subheader("♻ Total Landfill Diversion")
            st.caption("This shows the quantity of waste that was diverted from landfills through reuse or recycling efforts.")
            full_df = pd.read_csv("waste_log.csv")
            reuse_df = full_df[full_df["Status"] == "Sold"]
            recycle_df = full_df[full_df["Status"] == "Recycled"]
            landfill_diverted = reuse_df['Total Quantity (kg)'].sum() + recycle_df['Total Quantity (kg)'].sum()
            st.metric("♻ Total Diverted from Landfill", f"{landfill_diverted:.2f} kg")

            st.markdown("---")
            st.subheader("📅 Monthly Waste Breakdown")

            filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
            filtered_df["Month"] = filtered_df["Date"].dt.strftime('%b %Y')

            waste_types = ["Concrete", "Steel", "Wood", "Soil", "Sand", "Rubber"]
            for wt in waste_types:
                filtered_df[wt] = filtered_df.get(wt, 0).fillna(0)

            monthly_breakdown = filtered_df.groupby("Month")[waste_types].sum().reset_index().sort_values("Month")
            total_df = filtered_df.groupby("Month")["Total Quantity (kg)"].sum().reset_index(name="Total Quantity")

            col1, col2 = st.columns(2)
            with col1:
                st.write("### 📈 Category Breakdown")
                st.plotly_chart(px.bar(monthly_breakdown, x="Month", y=waste_types,
                    title="Waste by Category", barmode="group",
                    color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)

            with col2:
                st.write("### 📦 Total Waste Submitted")
                fig2 = px.bar(total_df, x="Month", y="Total Quantity", title="Total Waste",
                    text="Total Quantity", color_discrete_sequence=["#0984e3"])
                fig2.update_traces(textposition="outside")
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("---")
            st.write("### 🥧 Overall Waste Distribution")
            total_by_type = filtered_df[waste_types].sum().reset_index()
            total_by_type.columns = ["Waste Type", "Quantity"]
            st.plotly_chart(px.pie(total_by_type, names="Waste Type", values="Quantity",
                title="Total Waste Proportion",
                color_discrete_sequence=px.colors.sequential.RdBu), use_container_width=True)

            st.markdown("---")
            st.subheader("♻ Reuse vs Recycle Monthly Contribution")
            full_df["Date"] = pd.to_datetime(full_df["Date"], errors='coerce')
            full_df["Month"] = full_df["Date"].dt.strftime('%b %Y')

            reuse_monthly = full_df[full_df["Status"] == "Sold"].groupby("Month")["Total Quantity (kg)"].sum().reset_index(name="Reuse")
            recycle_monthly = full_df[full_df["Status"] == "Recycled"].groupby("Month")["Total Quantity (kg)"].sum().reset_index(name="Recycle")

            contribution_df = pd.merge(reuse_monthly, recycle_monthly, on="Month", how="outer").fillna(0)
            contribution_df["Total"] = contribution_df["Reuse"] + contribution_df["Recycle"]

            pie_data = contribution_df.melt(id_vars="Month", value_vars=["Reuse", "Recycle"], var_name="Type", value_name="Quantity")
            st.plotly_chart(px.pie(pie_data, names="Type", values="Quantity", title="Reuse vs Recycle Contribution",
                                color_discrete_sequence=px.colors.qualitative.Set2), use_container_width=True)

    with tab2:
        st.subheader("🌍 Estimated Carbon Footprint Reduction")
        st.caption("These estimates are based on the type and quantity of waste reused or recycled, using standard CO₂ saving factors.")

        reuse_factors = {"Concrete": 0.07, "Steel": 2.0, "Wood": 1.1, "Soil": 0.0, "Sand": 0.01, "Rubber": 1.0}
        recycle_factors = {"Concrete": 0.02, "Steel": 1.5, "Wood": 0.4, "Soil": 0.0, "Sand": 0.005, "Rubber": 0.6}

        def compute_co2(df, factors):
            co2 = 0
            for mat in factors:
                qty = df.get(mat, 0).sum()
                co2 += qty * factors[mat]
            return co2

        reuse_co2 = compute_co2(reuse_df, reuse_factors)
        recycle_co2 = compute_co2(recycle_df, recycle_factors)
        total_co2 = reuse_co2 + recycle_co2

        co2_col1, co2_col2 = st.columns(2)
        with co2_col1:
            st.metric("✅ Reuse CO₂ Saved", f"{reuse_co2:.2f} kg")
        with co2_col2:
            st.metric("🔁 Recycle CO₂ Saved", f"{recycle_co2:.2f} kg")

        st.metric("🌱 Total CO₂ Saved", f"{total_co2:.2f} kg")

        st.markdown("### 🌡 CO₂ Reduction Progress")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_co2,
            number={'suffix': " kg"},
            title={'text': "Total CO₂ Saved"},
            gauge={
                'axis': {'visible': False},
                'bar': {'color': "#00cc88"},
                'bgcolor': "#1c1c1c",
                'borderwidth': 2,
                'bordercolor': "gray"
            }
        ))
        fig.update_layout(
            height=300,
            margin=dict(t=40, b=20, l=10, r=10),
            paper_bgcolor="#0f1117",
            font=dict(color="white", size=14)
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("💰 Cost Savings")
        st.info("This section will showcase how the system contributes to financial savings for generators, consumers, and recycling agencies.")
        st.write("Thank you for holding your patience. 📈Charts coming soon!")


    #ADMIN PANEL
elif section == "🔐 Admin Panel":
    st.subheader("🔐 Admin Control Panel")
    st.warning("This section is for authorised use only.")

    try:
        df = pd.read_csv("waste_log.csv")
        if "Status" not in df.columns:
            df["Status"] = "Pending"
        else:
            df["Status"] = df["Status"].fillna("Pending")
            df["Status"] = df["Status"].astype(str).replace(["", "None", "nan", "NaN"], "Pending")

        if "Action Timestamp" not in df.columns:
            df["Action Timestamp"] = ""
        if "Edit Timestamp" not in df.columns:
            df["Edit Timestamp"] = ""

        st.info("Here you can review, approve, reject, edit, or delete any log.")

        pending_df = df[df["Status"] == "Pending"]
        if not pending_df.empty:
            st.write("⏳ Pending Logs")
            for index, row in pending_df.iterrows():
                with st.expander(f"📄 Entry #{index + 1} | {row['Location']} | {row['Date']}"):
                    st.write(f"Location: {row['Location']}")
                    st.write("Quantities:")
                    for mat in ["Concrete", "Steel", "Wood", "Sand", "Soil", "Rubber"]:
                        if mat in row:
                            st.write(f"🔹 {mat}: {row[mat]} kg")
                    st.write(f"Date: {row['Date']}")
                    st.write(f"Remarks: {row.get('Remarks', '-')}")
                    if "Image" in row and pd.notna(row["Image"]):
                        image_paths = row["Image"].split(";")
                        for img_path in image_paths:
                            img_path = img_path.strip()
                            if os.path.exists(img_path):
                                st.image(img_path, caption="📷 Uploaded Image", width=250)

                    col1, col2, col3 = st.columns(3)

                    if col1.button(f"✅ Approve #{index}", key=f"approve_{index}"):
                        df.at[index, "Status"] = "Approved"
                        df.at[index, "Action Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.success(f"✅ Log #{index + 1} approved.")

                        try:
                            reuse_df = pd.read_csv("reuse_requests.csv")
                        except FileNotFoundError:
                            reuse_df = pd.DataFrame(columns=[
                                "Request ID", "Buyer Name", "Buyer Email", "Buyer Phone", "Waste ID",
                                "Requested Waste Type", "Requested Quantity (kg)", "Proposed Price (INR)",
                                "Agreed Amount (INR)", "Status", "Remarks", "Request Date"
                            ])

                        try:
                            bids_df = pd.read_csv("reuse_bids.csv")
                            waste_id = row.get("Waste ID", f"AUTO-{index}")
                            related_bids = bids_df[bids_df["Waste ID"] == waste_id]
                            if not related_bids.empty:
                                highest_bid_price = float(related_bids["Bid Price"].max())
                            else:
                                highest_bid_price = ""
                        except:
                            highest_bid_price = ""

                        new_request = {
                            "Request ID": f"AUTO-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "Buyer Name": row.get("Contractor", "Unknown"),
                            "Buyer Email": row.get("Email", ""),
                            "Buyer Phone": row.get("Phone", ""),
                            "Waste ID": row.get("Waste ID", f"AUTO-{index}"),
                            "Requested Waste Type": "Mixed",
                            "Requested Quantity (kg)": row.get("Total Quantity (kg)", 0),
                            "Proposed Price (INR)": "",
                            "Agreed Amount (INR)": highest_bid_price,
                            "Status": "Approved",
                            "Remarks": row.get("Remarks", ""),
                            "Request Date": datetime.datetime.now().strftime('%Y-%m-%d')
                        }

                        reuse_df = pd.concat([reuse_df, pd.DataFrame([new_request])], ignore_index=True)
                        reuse_df.to_csv("reuse_requests.csv", index=False)

                    if col2.button(f"❌ Reject #{index}", key=f"reject_{index}"):
                        df.at[index, "Status"] = "Rejected"
                        df.at[index, "Action Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.warning(f"❌ Log #{index + 1} rejected.")

                    if col3.button(f"🗑 Delete #{index}", key=f"delete_{index}"):
                        df = df.drop(index)
                        st.error(f"🗑 Log #{index + 1} deleted.")
        else:
            st.success("✅ No pending logs to review.")

        st.markdown("---")
        st.write("### ✏ Edit Approved/Rejected Logs")

        editable_logs = df[df["Status"].isin(["Approved", "Rejected"])]
        for index, row in editable_logs.iterrows():
            with st.expander(f"✏ Edit Entry #{index + 1} | {row['Location']}"):
                with st.form(f"form_{index}"):
                    location = st.text_input(f"Location for #{index}", row["Location"], key=f"loc_{index}")
                    remarks = st.text_input(f"Remarks for #{index}", row.get("Remarks", ""), key=f"rmk_{index}")

                    updated_quantities = {}
                    for mat in ["Concrete", "Steel", "Wood", "Sand", "Soil", "Rubber"]:
                        if mat in df.columns:
                            qty = st.number_input(f"{mat} Quantity (kg)", value=float(row.get(mat, 0)), min_value=0.0, step=1.0, key=f"{mat}_{index}")
                            updated_quantities[mat] = qty

                    submitted = st.form_submit_button(f"📂 Save Changes #{index}")
                    if submitted:
                        df.at[index, "Location"] = location
                        df.at[index, "Remarks"] = remarks
                        df.at[index, "Edit Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        for mat, qty in updated_quantities.items():
                            df.at[index, mat] = qty
                        st.success(f"✅ Log #{index + 1} updated.")

        st.markdown("---")
        st.write("### 🔎 Filter Logs by Status")

        filter_option = st.selectbox("Choose status to view:", ["All", "Approved", "Rejected", "Pending"])
        if filter_option == "All":
            st.dataframe(df)
        else:
            st.dataframe(df[df["Status"] == filter_option])

        df.to_csv("waste_log.csv", index=False)  # Save changes to waste_log.csv



        st.markdown("---")
        st.header("📁 Reuse Bids Management")

        try:
            bids_df = pd.read_csv("reuse_bids.csv")
            for waste_id in bids_df["Waste ID"].unique():
                bids = bids_df[bids_df["Waste ID"] == waste_id]
                with st.expander(f"🆔 Waste ID: {waste_id} | {len(bids)} bids"):
                    st.dataframe(bids.sort_values("Bid Price", ascending=False))

                    highest = bids.loc[bids["Bid Price"].idxmax()]
                    st.success(f"🔝 Highest Bid: ₹{highest['Bid Price']} by {highest['Bidder']} ({highest['Contact']})")

                    if st.button(f"✔ Mark as Sold to {highest['Bidder']} for {waste_id}", key=f"sold_{waste_id}"):
                        bids_df.loc[bids_df["Waste ID"] == waste_id, "Status"] = "Not Selected"
                        bids_df.loc[(bids_df["Waste ID"] == waste_id) & (bids_df["Bidder"] == highest["Bidder"]), "Status"] = "Selected"

                        df.loc[df["Waste ID"] == waste_id, "Status"] = "Sold"

                        try:
                            reuse_req_df = pd.read_csv("reuse_requests.csv")
                            selected_bid_row = bids_df[(bids_df["Waste ID"] == waste_id) & (bids_df["Bidder"] == highest["Bidder"])]
                            if not selected_bid_row.empty:
                                selected_bid_row = selected_bid_row.iloc[0]

                                reuse_match = reuse_req_df[(reuse_req_df["Waste ID"].str.strip() == waste_id.strip()) & (reuse_req_df["Buyer Email"].str.strip().str.lower() == selected_bid_row.get("Email", "").strip().lower())]
                                if not reuse_match.empty:
                                    req_row = reuse_match.iloc[0]
                                    request_id = req_row["Request ID"]
                                    buyer_email = req_row["Buyer Email"]
                                    buyer_phone = req_row["Buyer Phone"]
                                    waste_type = req_row["Requested Waste Type"]
                                    quantity = req_row["Requested Quantity (kg)"]
                                    agreed_amount = req_row.get("Agreed Amount (INR)", "N/A") or "N/A"
                                else:
                                    request_id = f"AUTO-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                                    buyer_email = selected_bid_row["Email"]
                                    buyer_phone = selected_bid_row["Contact"]
                                    waste_type = "N/A"
                                    quantity = "N/A"
                                    agreed_amount = selected_bid_row["Bid Price"]

                                waste_row = df[df["Waste ID"] == waste_id].iloc[0]
                                contractor_name = waste_row.get("Contractor", "N/A")
                                contractor_phone = waste_row.get("Phone", "N/A")
                                contractor_email = waste_row.get("Email", "N/A")
                                location = waste_row.get("Location", "N/A")

                                email_subject = f"✅ Reuse Request {request_id} Approved!"
                                email_content = f"""
Hi,

🎉 Good news! Your reuse request has been APPROVED.

🆔 Request ID: {request_id}  
🆔 Waste ID: {waste_id}  
📦 Material: {waste_type}  
⚖ Quantity: {quantity} kg  
💰 Final Deal: ₹{agreed_amount}  
📍 Location: {location}

👷 Contractor Details:
Name: {contractor_name}  
Phone: {contractor_phone}  
Email: {contractor_email}

Please coordinate for pickup and payment.

Regards,  
DMRC C&D Waste Tracker Team
"""
                                from notifications import send_email, send_sms
                                send_email(to_email=buyer_email, subject=email_subject, content=email_content)

                                sms_body = f"✅ Request {request_id} approved. Deal ₹{agreed_amount}. Contact {contractor_name} at {contractor_phone} – DMRC Tracker"
                                send_sms(to_number=buyer_phone, body_text=sms_body)

                                st.success("📤 Notification sent to bidder.")

                        except Exception as e:
                            st.error(f"❌ Failed to send reuse approval notification: {e}")

                        bids_df.to_csv("reuse_bids.csv", index=False)
                        df.to_csv("waste_log.csv", index=False)

        except FileNotFoundError:
            st.info("⚠ No reuse bids available.")
        except Exception as e:
            st.error(f"❌ Error loading bid data: {e}")

    except FileNotFoundError:
        st.warning("⚠ No waste log file found.")
    except Exception as e:
        st.error(f"❌ Error in Admin Panel: {e}")


    st.markdown("---")
    from notifications import send_email  

    st.markdown("### ♻ Auto-Recycle Check (After 3 Days of Approval)")

try:
    waste_df = pd.read_csv("waste_log.csv")
    bid_df = pd.read_csv("reuse_bids.csv")

    waste_df['Action Timestamp'] = pd.to_datetime(waste_df['Action Timestamp'], errors='coerce')
    today = datetime.datetime.now()

    try:
        recycle_df = pd.read_csv("recycling_station.csv")
    except FileNotFoundError:
        recycle_df = pd.DataFrame(columns=[
            "Waste ID", "Waste Types", "Original Value", "Status", "Assigned To", "Date",
            "Location", "Remarks", "Image", "Total Quantity (kg)", "Total Quantity (tons)",
            "Market Value", "Recycled On"
        ])

    recycled_count   = 0
    recycled_ids = []

    for index, row in waste_df.iterrows():
        waste_id = str(row.get("Waste ID", "")).strip()
        waste_types = str(row.get("Waste Types", "")).strip()
        approval_date = row.get("Action Timestamp")
        status = str(row.get("Status", "Pending")).strip()

        if status != "Approved" or pd.isna(approval_date):
            continue

        if (today - approval_date).days < 3:
            continue

        clean_type = waste_types.encode('ascii', 'ignore').decode().strip()
        bids = bid_df[bid_df["Waste ID"].astype(str).str.strip() == waste_id]
        valid_bid_exists = not bids.empty

        if not valid_bid_exists and waste_id not in recycle_df["Waste ID"].astype(str).values:
            waste_df.at[index, "Status"] = "Recycled"
            waste_df.at[index, "Assigned To"] = "Recycling Station"

            recycled_entry = {
                "Waste ID": waste_id,
                "Waste Types": clean_type,
                "Original Value": "",
                "Status": "Recycled",
                "Assigned To": "Recycling Station",
                "Date": today.strftime("%Y-%m-%d"),
                "Location": row.get("Location", "N/A"),
                "Remarks": row.get("Remarks", ""),
                "Image": row.get("Image", ""),
                "Total Quantity (kg)": row.get("Total Quantity (kg)", ""),
                "Total Quantity (tons)": row.get("Total Quantity (tons)", ""),
                "Market Value": "",
                "Recycled On": today.strftime("%Y-%m-%d")
            }

            recycle_df = pd.concat([recycle_df, pd.DataFrame([recycled_entry])], ignore_index=True)
            recycled_ids.append(waste_id)
            recycled_count += 1

            # 🔔 Send email notification to recycling station
            try:   
                send_email(
                    to_email="recyclingstation@dmrc.org",
                    subject=f"♻ Waste ID {waste_id} Auto-Recycled",
                    content=f"""
Hello,

This is an automated alert from the DMRC Smart C&D Waste Tracker.

The following waste item is being unclaimed for 3 days: 

🆔 Waste ID: {waste_id}  
🧱 Type: {clean_type}  
📍 Location: {row.get('Location', 'N/A')}  
⚖ Quantity: {row.get('Total Quantity (kg)', 'N/A')} kg  
🗓 Date: {today.strftime('%Y-%m-%d')}  


🔽 Logged By  
👤 Name: {row.get('Logged By', 'Unknown')}  
📧 Email: {row.get('Logged Email', 'N/A')}  
📞 Phone: {row.get('Logged Phone', 'N/A')}

Please collect the waste and begin recycling operations.

Regards,  
Smart C&D Waste Tracker System
"""
                )
            except Exception as e:
                st.warning(f"⚠ Email failed for Waste ID {waste_id}: {e}")

        waste_df.to_csv("waste_log.csv", index=False)
        recycle_df.to_csv("recycling_station.csv", index=False)

        if recycled_count > 0:
            st.success(f"✅ {recycled_count} waste item(s) moved to Recycling Station and notifications sent.")
     
        else:
            st.info("No items auto-moved to Recycling Station today. ") 
except Exception as e:
    st.error(f"❌ Something went wrong: {e}")