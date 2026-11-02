# Smart Product Scanner: YOLO-Based Autonomous Billing & Inventory System 🛒⚡

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.x-black.svg)](https://flask.palletsprojects.com/)
[![YOLO](https://img.shields.io/badge/Ultralytics-YOLO-00FFFF.svg)](https://docs.ultralytics.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.8%2B-EE4C2C.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, deep learning-powered retail self-checkout and POS billing system built with **Flask**, **Ultralytics YOLO**, and **WebRTC**. The system transforms commodity webcams into visual product scanners—recognizing items in real time, suppressing human/background false positives, calculating itemized GST and discounts, and synchronizing store inventory automatically.

---

## 🌟 Key Features

* **⚡ Real-Time Object Recognition**: Powered by YOLO to detect retail items in sub-50ms inference latency without requiring physical barcodes.
* **🚫 Target Class Whitelisting (Person-Suppression)**: Strictly whitelists catalog product IDs during inference. Shoppers standing in front of the camera are **never** falsely detected or billed as a `person`.
* **🖐️ Hand-Occlusion Optimization**: Fine-tuned confidence threshold (`0.20`), container alias mapping (`cup` ➔ `bottle`), and 720p HD ingestion enable reliable detection of small items held by fingers (e.g., wireless mice, water bottles).
* **📦 Dynamic Live Inventory**: Deducts stock immediately upon product scan, triggers real-time health alerts (`AVAILABLE`, `LOW STOCK`, `OUT OF STOCK`), and automatically restores stock when items are deleted or when the bill is cleared.
* **🧾 Automated Multi-Tier Taxation & Discounts**: Computes line-item subtotals, category promotional discounts, and statutory GST slabs (5% for basic goods, 18% for electronics) dynamically.
* **📷 WebRTC POS Dashboard**: Intuitive, responsive workstation featuring live camera streaming, real-time annotated bounding box preview, and interactive cart controls.

---

## 🛍️ Supported Product Catalog

| Product Class | Display Name | Unit Price (₹) | Category Discount | GST Slab | Initial Stock |
|---|---|:---:|:---:|:---:|:---:|
| `cell phone` | Mobile Phone | ₹25,000 | 5% | 18% | 10 |
| `laptop` | MacBook | ₹85,000 | 8% | 18% | 5 |
| `bottle` | Water Bottle | ₹100 | 0% | 5% | 20 |
| `mouse` | Wireless Mouse | ₹800 | 10% | 18% | 15 |
| `clock` | Analog Watch | ₹1,500 | 5% | 18% | 8 |
| `keyboard` | Keyboard | ₹1,200 | 5% | 18% | 10 |
| `book` | Notebook | ₹80 | 0% | 5% | 25 |

---

## 🏗️ System Architecture & Workflow

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT BROWSER                                    |
|   [ WebRTC Camera (720p) ] ---> [ HTML5 Canvas ] ---> [ FormData (JPEG Blob) ]    |
+-----------------------------------------------------------------------------------+
                                         |
                               POST /api/detect
                                         v
+-----------------------------------------------------------------------------------+
|                            FLASK APPLICATION SERVER                               |
|                                                                                   |
|   +---------------------+   +-----------------------+   +---------------------+   |
|   | services/detector.py|   | services/inventory.py |   | services/billing.py |   |
|   | - YOLO Inference    |   | - Atomic Deductions   |   | - Multi-tier GST    |   |
|   | - Class Whitelist   |   | - Stock Replenishment |   | - Discounts         |   |
|   | - Conf Threshold 0.2|   | - Status Thresholds   |   | - Invoice Summary   |   |
|   +---------------------+   +-----------------------+   +---------------------+   |
+-----------------------------------------------------------------------------------+
             |                                    |                    |
             v                                    v                    v
    [ model/yolo26n.pt ]                [ config/products.json ] [ data/database.json ]
```

1. **Capture**: The browser streams video via WebRTC at 1280x720 HD. On clicking **"Scan Product"**, the frame is serialized as a JPEG blob.
2. **Inference**: Flask receives the frame at `/api/detect`. YOLO runs inference with `classes=allowed_ids`, ignoring class `0` (`person`) and drawing bounding boxes on detected products.
3. **Cart & Inventory**: The top detected class is posted to `/api/add-item`. If stock is available, catalog stock decrements by 1 and the itemized bill recalculates in real time.
4. **Restoration**: Deleting an item or clearing the bill restores stock back to the catalog immediately.

---

## 📁 Project Directory Structure

```
DL project/
│
├── app.py                     # Main Flask web application & REST API routes
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive project documentation
├── .gitignore                 # Git ignore rules for virtualenvs, temporary & doc files
│
├── model/
│   └── yolo26n.pt             # YOLO Nano neural weights checkpoint (6.2 MB)
│
├── config/
│   └── products.json          # Retail catalog schema & product definitions
│
├── services/
│   ├── detector.py            # YOLO inference with person-filtering & alias mapping
│   ├── billing.py             # Billing logic, GST slabs (5%/18%) & discount calculations
│   └── inventory.py           # Stock management, persistence & threshold statuses
│
├── data/
│   ├── database.json          # Active transaction bill ledger
│   └── uploads/               # Temporary directory for scanned frames
│
├── templates/
│   └── index.html             # Single-page POS workstation interface
│
└── static/
    ├── css/
    │   └── style.css          # Modern responsive POS styling
    └── js/
        └── app.js             # WebRTC streaming, canvas capture & asynchronous DOM updates
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
* Python 3.9 or higher
* Modern web browser (Google Chrome, Mozilla Firefox, Apple Safari, or Microsoft Edge)
* Built-in or USB webcam

### 2. Clone the Repository
```bash
git clone https://github.com/samit-ops/YOLO-Based-Billing-System.git
cd YOLO-Based-Billing-System
```

### 3. Set Up Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch Application Server
```bash
python3 app.py
```

*Note: On macOS, the server automatically checks if port 5000 is occupied by AirPlay Receiver and binds to port **5001** automatically.*

### 6. Open in Browser
Navigate to:
👉 **`http://127.0.0.1:5001`** *(or `http://127.0.0.1:5000`)*

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the single-page POS terminal UI |
| `POST` | `/api/detect` | Ingests camera frame, executes YOLO inference, returns detections & annotated image |
| `POST` | `/api/add-item` | Validates stock, decrements catalog inventory, and appends item to bill |
| `DELETE` | `/api/remove-item/<product_class>` | Removes item quantity from bill and replenishes stock |
| `POST` | `/api/clear-bill` | Empties the bill and fully restores all item quantities to catalog |
| `GET` | `/api/bill` | Retrieves active bill calculations, subtotals, taxes, and grand total |
| `GET` | `/api/inventory` | Retrieves live catalog stock quantities and health statuses |

---

## 🧮 Taxation & Financial Formulas

The billing engine computes exact statutory taxation and commercial discounts:

$$\text{Item Subtotal} = \text{Price} \times \text{Quantity}$$
$$\text{Discount Amount} = \text{Item Subtotal} \times \left(\frac{\text{Discount \%}}{100}\right)$$
$$\text{Taxable Base} = \text{Item Subtotal} - \text{Discount Amount}$$
$$\text{GST Amount} = \text{Taxable Base} \times \left(\frac{\text{GST \%}}{100}\right)$$
$$\text{Final Line Total} = \text{Taxable Base} + \text{GST Amount}$$
$$\text{Grand Total} = \sum \text{Subtotals} - \sum \text{Discounts} + \sum \text{GST Amounts}$$

---

## 👥 Authors & Academic Credits

Developed as a Deep Learning Capstone Project by:

* **Samit Kumar**  
  * Roll No.: `2401331530210`  
  * ERP ID: `0241csml009`  
  * GitHub: [@samit-ops](https://github.com/samit-ops)
* **Ryan Kapoor**  
  * Roll No.: `240131530195`  
  * ERP ID: `0241csml026`  

**Branch**: Computer Science & Engineering (Artificial Intelligence - Machine Learning), Section C  
**Institution**: Noida Institute of Engineering and Technology (NIET), Greater Noida  
**Supervision**: **Mr. Faizan Ahmad**, Assistant Professor, Department of CSE-AIML  

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
