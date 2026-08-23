/**
 * MediFinder 2.0 Client Engine
 * Live Leaflet Maps, Geolocation, Autocomplete, and Fast Async Reservations
 */

const MediFinder = (() => {
  let mapInstance = null;
  let markersLayer = null;
  let userCoords = { lat: 25.6110, lng: 85.1430 }; // Default Patna
  let hasUserCoords = false;

  // Init Geolocation
  function initGeolocation(callback) {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          userCoords.lat = pos.coords.latitude;
          userCoords.lng = pos.coords.longitude;
          hasUserCoords = true;
          sessionStorage.setItem("user_lat", userCoords.lat);
          sessionStorage.setItem("user_lng", userCoords.lng);
          if (callback) callback(userCoords);
        },
        (err) => {
          console.warn("Geolocation denied or unavailable:", err.message);
          const savedLat = sessionStorage.getItem("user_lat");
          const savedLng = sessionStorage.getItem("user_lng");
          if (savedLat && savedLng) {
            userCoords.lat = parseFloat(savedLat);
            userCoords.lng = parseFloat(savedLng);
            hasUserCoords = true;
          }
          if (callback) callback(userCoords);
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    } else {
      if (callback) callback(userCoords);
    }
  }

  // Setup Autocomplete
  function initAutocomplete(inputElementId, dropdownId, onSelect) {
    const input = document.getElementById(inputElementId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;

    let debounceTimer;

    input.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      if (query.length < 2) {
        dropdown.style.display = "none";
        dropdown.innerHTML = "";
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/v1/medicines/autocomplete?q=${encodeURIComponent(query)}`);
          const json = await res.json();
          if (json.success && json.data.length > 0) {
            dropdown.innerHTML = json.data
              .map(
                (item) => `
              <div class="autocomplete-item" data-name="${item.name}" data-salt="${item.salt}">
                <div>
                  <strong>${item.name}</strong>
                  <div class="text-muted small">${item.salt || ""} ${item.dosage ? "• " + item.dosage : ""}</div>
                </div>
                <span class="badge bg-light text-primary border">Select</span>
              </div>
            `
              )
              .join("");
            dropdown.style.display = "block";

            dropdown.querySelectorAll(".autocomplete-item").forEach((el) => {
              el.addEventListener("click", () => {
                input.value = el.getAttribute("data-name");
                dropdown.style.display = "none";
                if (onSelect) {
                  onSelect(el.getAttribute("data-name"), el.getAttribute("data-salt"));
                }
              });
            });
          } else {
            dropdown.style.display = "none";
          }
        } catch (err) {
          console.error("Autocomplete error:", err);
        }
      }, 200);
    });

    document.addEventListener("click", (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = "none";
      }
    });
  }

  // Map Initialization for Search Page
  function initSearchMap(containerId, centerLat, centerLng) {
    const container = document.getElementById(containerId);
    if (!container || typeof L === "undefined") return;

    mapInstance = L.map(containerId).setView([centerLat || userCoords.lat, centerLng || userCoords.lng], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap",
    }).addTo(mapInstance);

    markersLayer = L.layerGroup().addTo(mapInstance);

    // User Location Marker
    if (hasUserCoords) {
      const userIcon = L.divIcon({
        className: "custom-user-pin",
        html: '<div style="background:#0284c7; width:14px; height:14px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 8px rgba(0,0,0,0.4);"></div>',
        iconSize: [14, 14],
      });
      L.marker([userCoords.lat, userCoords.lng], { icon: userIcon }).addTo(mapInstance).bindPopup("<b>Your Location</b>");
    }
  }

  // Render Map Markers
  function renderPharmacyMarkers(pharmacies) {
    if (!markersLayer || !mapInstance) return;
    markersLayer.clearLayers();

    const bounds = [];
    if (hasUserCoords) bounds.push([userCoords.lat, userCoords.lng]);

    pharmacies.forEach((p) => {
      if (p.lat && p.lng) {
        const marker = L.marker([p.lat, p.lng]).addTo(markersLayer);
        marker.bindPopup(`
          <div style="min-width: 180px;">
            <h6 class="mb-1 fw-bold text-primary">${p.name}</h6>
            <p class="small text-muted mb-1">${p.address || ""}</p>
            <div class="d-flex justify-content-between align-items-center mt-2">
              <span class="badge ${p.is_open_24h ? "bg-success" : "bg-light text-dark"}">
                ${p.is_open_24h ? "24/7 Open" : p.open_time + " - " + p.close_time}
              </span>
              <a href="/pharmacy/${p.id}" class="btn btn-sm btn-outline-primary py-0 px-2">Store</a>
            </div>
          </div>
        `);
        bounds.push([p.lat, p.lng]);
      }
    });

    if (bounds.length > 0) {
      mapInstance.fitBounds(bounds, { padding: [30, 30], maxZoom: 14 });
    }
  }

  // Open Medicine Reservation Modal
  function openReservationModal(inventoryId, pharmacyId, medName, dosage, price, pharmacyName) {
    const modalEl = document.getElementById("reservationModal");
    if (!modalEl) return;

    document.getElementById("resInvId").value = inventoryId;
    document.getElementById("resShopId").value = pharmacyId;
    document.getElementById("resMedName").textContent = medName;
    document.getElementById("resDosage").textContent = dosage || "";
    document.getElementById("resPrice").textContent = `₹${price}`;
    document.getElementById("resShopName").textContent = pharmacyName;

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }

  // Submit Reservation via REST API
  async function submitReservation(formElement) {
    const submitBtn = formElement.querySelector('button[type="submit"]');
    const origText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Reserving...';

    const payload = {
      inventory_id: document.getElementById("resInvId").value,
      pharmacy_id: document.getElementById("resShopId").value,
      customer_phone: document.getElementById("resPhone").value,
      customer_name: document.getElementById("resName").value,
      quantity: parseInt(document.getElementById("resQty").value, 10) || 1,
      note: document.getElementById("resNote").value,
    };

    try {
      const res = await fetch("/api/v1/reservations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.success) {
        alert("🎉 Reservation confirmed! Medicine is held for 2 hours at the pharmacy.");
        window.location.reload();
      } else {
        alert("Reservation failed: " + (data.error || "Unable to hold stock."));
        submitBtn.disabled = false;
        submitBtn.innerHTML = origText;
      }
    } catch (err) {
      alert("Network error. Please try again.");
      submitBtn.disabled = false;
      submitBtn.innerHTML = origText;
    }
  }

  return {
    initGeolocation,
    initAutocomplete,
    initSearchMap,
    renderPharmacyMarkers,
    openReservationModal,
    submitReservation,
    getUserCoords: () => userCoords,
  };
})();
