const camera = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const startCameraButton = document.getElementById("startCamera");
const scanProductButton = document.getElementById("scanProduct");
const clearBillButton = document.getElementById("clearBill");
const uploadButton = document.getElementById("uploadButton");
const uploadImage = document.getElementById("uploadImage");
const annotatedImage = document.getElementById("annotatedImage");

const detectionStatus = document.getElementById("detectionStatus");

let cameraStream = null;
let lastScannedProduct = null;
let isScanning = false;


startCameraButton.addEventListener("click", async () => {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: "user"
            },
            audio: false
        });

        camera.srcObject = cameraStream;
        detectionStatus.textContent = "Camera started. Hold a product in front of the lens.";
    } catch (error) {
        detectionStatus.textContent =
            "Camera access denied or unavailable. You can use the Upload Image button.";
        console.error(error);
    }
});


scanProductButton.addEventListener("click", async () => {
    if (!cameraStream) {
        detectionStatus.textContent = "Please start the camera first.";
        return;
    }

    if (isScanning) {
        return;
    }

    isScanning = true;
    scanProductButton.disabled = true;
    detectionStatus.textContent = "Scanning frame for products...";

    canvas.width = camera.videoWidth || 640;
    canvas.height = camera.videoHeight || 480;

    const context = canvas.getContext("2d");
    context.drawImage(camera, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        try {
            const formData = new FormData();
            formData.append("image", blob, "camera.jpg");

            const response = await fetch("/api/detect", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            // Display annotated detection preview with bounding boxes
            if (data.annotated_image && annotatedImage) {
                annotatedImage.src = data.annotated_image + "?t=" + Date.now();
                annotatedImage.style.display = "block";
            }

            if (!data.success || !data.detections || data.detections.length === 0) {
                detectionStatus.textContent =
                    "No product detected. Hold the item steady, close to the camera, and try again.";
                lastScannedProduct = null;
                return;
            }

            const bestDetection = data.detections[0];
            const productClass = bestDetection.class;
            const confidence = Math.round(bestDetection.confidence * 100);

            detectionStatus.textContent =
                `Recognized ${productClass} (${confidence}% confidence). Adding to bill...`;

            const addResponse = await fetch("/api/add-item", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product_class: productClass
                })
            });

            const addData = await addResponse.json();

            if (!addData.success) {
                detectionStatus.textContent = addData.message;
                return;
            }

            lastScannedProduct = productClass;
            detectionStatus.textContent = `✓ ${addData.message} (${productClass} - ${confidence}%)`;

            updateBill(addData.bill);
            updateInventory(addData.inventory);
        } catch (err) {
            console.error("Scan error:", err);
            detectionStatus.textContent = "Error scanning image. Please try again.";
        } finally {
            // Short debounce to prevent accidental double-clicks while allowing next scans
            setTimeout(() => {
                isScanning = false;
                scanProductButton.disabled = false;
            }, 800);
        }
    }, "image/jpeg", 0.95);
});


if (uploadButton && uploadImage) {
    uploadButton.addEventListener("click", () => {
        uploadImage.click();
    });

    uploadImage.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("image", file, file.name);

        detectionStatus.textContent = "Detecting product from uploaded image...";

        try {
            const response = await fetch("/api/detect", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.annotated_image && annotatedImage) {
                annotatedImage.src = data.annotated_image + "?t=" + Date.now();
                annotatedImage.style.display = "block";
            }

            if (!data.success || !data.detections || data.detections.length === 0) {
                detectionStatus.textContent = "Product not detected in image.";
                return;
            }

            const bestDetection = data.detections[0];
            const productClass = bestDetection.class;
            const confidence = Math.round(bestDetection.confidence * 100);

            detectionStatus.textContent =
                `Recognized ${productClass} (${confidence}% confidence). Adding to bill...`;

            const addResponse = await fetch("/api/add-item", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product_class: productClass
                })
            });

            const addData = await addResponse.json();

            if (!addData.success) {
                detectionStatus.textContent = addData.message;
                return;
            }

            detectionStatus.textContent = `✓ ${addData.message} (${productClass} - ${confidence}%)`;

            updateBill(addData.bill);
            updateInventory(addData.inventory);
        } catch (err) {
            detectionStatus.textContent = "Error scanning uploaded image.";
            console.error(err);
        }
    });
}


clearBillButton.addEventListener("click", async () => {
    const response = await fetch("/api/clear-bill", {
        method: "POST"
    });

    const data = await response.json();

    updateBill(data.bill);
    updateInventory(data.inventory);

    lastScannedProduct = null;
    detectionStatus.textContent = "Bill cleared successfully.";

    if (annotatedImage) {
        annotatedImage.style.display = "none";
    }
});


function updateBill(bill) {
    const billItems = document.getElementById("billItems");

    if (!bill.items || bill.items.length === 0) {
        billItems.innerHTML = "<p>No items added.</p>";
    } else {
        billItems.innerHTML = "";

        bill.items.forEach(item => {
            const row = document.createElement("div");
            row.className = "bill-row";

            row.innerHTML = `
                <span>
                    <strong>${item.name}</strong> x ${item.quantity}
                    <br>
                    <small>₹${item.final_amount.toFixed(2)} (incl. ${item.gst}% GST, -${item.discount}% off)</small>
                </span>

                <button onclick="removeItem('${item.class}')">
                    Delete
                </button>
            `;

            billItems.appendChild(row);
        });
    }

    document.getElementById("subtotal").textContent =
        (bill.subtotal || 0).toFixed(2);

    document.getElementById("discount").textContent =
        (bill.total_discount || 0).toFixed(2);

    document.getElementById("gst").textContent =
        (bill.total_gst || 0).toFixed(2);

    document.getElementById("total").textContent =
        (bill.total || 0).toFixed(2);
}


async function removeItem(productClass) {
    const response = await fetch(
        `/api/remove-item/${encodeURIComponent(productClass)}`,
        {
            method: "DELETE"
        }
    );

    const data = await response.json();

    updateBill(data.bill);
    updateInventory(data.inventory);

    lastScannedProduct = null;
    detectionStatus.textContent = data.message;
}


function updateInventory(inventory) {
    const inventoryTable =
        document.getElementById("inventoryTable");

    inventoryTable.innerHTML = "";

    inventory.forEach(item => {
        const row = document.createElement("tr");

        let statusClass = "available";

        if (item.status === "LOW STOCK") {
            statusClass = "low-stock";
        }

        if (item.status === "OUT OF STOCK") {
            statusClass = "out-of-stock";
        }

        row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.stock}</td>
            <td class="${statusClass}">
                ${item.status}
            </td>
        `;

        inventoryTable.appendChild(row);
    });
}


async function loadInitialData() {
    try {
        const billResponse = await fetch("/api/bill");
        const bill = await billResponse.json();
        updateBill(bill);

        const inventoryResponse = await fetch("/api/inventory");
        const inventory = await inventoryResponse.json();
        updateInventory(inventory);
    } catch (e) {
        console.error("Failed to load initial data:", e);
    }
}


loadInitialData();
