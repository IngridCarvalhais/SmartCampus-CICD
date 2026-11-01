"use strict";

const API_BASE = "/api";

function setState(panel, state, message) {
  panel.querySelectorAll("[data-state]").forEach((element) => {
    element.hidden = element.dataset.state !== state;
  });

  const errorMessage = panel.querySelector("[data-error-message]");
  if (errorMessage && message) {
    errorMessage.textContent = message;
  }
}

async function fetchCollection(path) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new Error(
      "No se pudo conectar con el servicio. Comprueba que el backend esté disponible.",
    );
  }

  if (!response.ok) {
    throw new Error(`El servidor respondió con el estado ${response.status}.`);
  }

  const data = await response.json();
  if (!Array.isArray(data)) {
    throw new Error("La respuesta del servidor no tiene el formato esperado.");
  }

  return data;
}

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) {
    element.className = className;
  }
  if (text !== undefined) {
    element.textContent = text;
  }
  return element;
}

function makeIcon(name) {
  const icon = document.createElement("span");
  icon.className = "room-icon";
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = name;
  return icon;
}

function renderRooms(container, rooms) {
  const fragment = document.createDocumentFragment();

  rooms.forEach((room) => {
    const card = makeElement("article", "room-card");
    const top = makeElement("div", "room-card-top");
    top.append(makeIcon("⌂"), makeElement("span", "room-id", `AULA #${room.id}`));

    const title = makeElement("h3", "", room.nombre);
    const building = makeElement("p", "room-building", room.edificio);
    const capacity = makeElement("div", "room-meta");
    capacity.setAttribute("aria-label", `Capacidad: ${room.capacidad} personas`);
    capacity.append(
      makeElement("span", "", "◉"),
      makeElement("span", "", `${room.capacidad} plazas`),
    );

    const equipmentLabel = makeElement("span", "equipment-label", "Equipamiento");
    const equipmentList = makeElement("div", "equipment-list");
    if (room.equipamiento.length > 0) {
      room.equipamiento.forEach((item) => {
        equipmentList.append(makeElement("span", "equipment-chip", item));
      });
    } else {
      equipmentList.append(makeElement("span", "equipment-none", "No especificado"));
    }

    card.append(top, title, building, capacity, equipmentLabel, equipmentList);
    fragment.append(card);
  });

  container.replaceChildren(fragment);
}

function formatDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(year, month - 1, day);
  return new Intl.DateTimeFormat("es-ES", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(date);
}

function formatTime(value) {
  return value.slice(0, 5);
}

function renderBookings(container, bookings, rooms) {
  const roomsById = new Map(rooms.map((room) => [room.id, room]));
  const fragment = document.createDocumentFragment();

  bookings.forEach((booking) => {
    const room = roomsById.get(booking.aula_id);
    const card = makeElement("article", "booking-card");
    const top = makeElement("div", "booking-card-top");
    const roomInfo = makeElement("div", "booking-room");
    const roomText = makeElement("div");
    roomText.append(
      makeElement("h3", "", room ? room.nombre : `Aula #${booking.aula_id}`),
      makeElement("p", "booking-building", room ? room.edificio : "Edificio no disponible"),
    );
    roomInfo.append(makeIcon("⌂"), roomText);
    top.append(roomInfo, makeElement("span", "booking-id", `#${booking.id}`));

    const details = makeElement("div", "booking-details");
    details.append(
      makeElement("span", "booking-detail", `Usuario: ${booking.usuario}`),
      makeElement("span", "booking-detail", formatDate(booking.fecha)),
      makeElement(
        "span",
        "booking-detail",
        `Inicio: ${formatTime(booking.hora_inicio)}`,
      ),
      makeElement("span", "booking-detail", `Fin: ${formatTime(booking.hora_fin)}`),
    );
    card.append(top, details);
    fragment.append(card);
  });

  container.replaceChildren(fragment);
}

async function loadRooms() {
  const panel = document.querySelector("#aulas .data-panel");
  const container = panel.querySelector("[data-room-list]");
  container.setAttribute("aria-busy", "true");
  setState(panel, "loading");

  try {
    const rooms = await fetchCollection("/rooms");
    if (rooms.some((room) => !Array.isArray(room.equipamiento))) {
      throw new Error("Los datos de equipamiento de las aulas no son válidos.");
    }
    renderRooms(container, rooms);
    container.setAttribute("aria-busy", "false");
    setState(panel, rooms.length ? "results" : "empty");
    return rooms;
  } catch (error) {
    container.setAttribute("aria-busy", "false");
    setState(panel, "error", error.message);
    return null;
  }
}

async function loadBookings(roomsPromise) {
  const panel = document.querySelector("#reservas .data-panel");
  const container = panel.querySelector("[data-booking-list]");
  container.setAttribute("aria-busy", "true");
  setState(panel, "loading");

  try {
    const [bookings, rooms] = await Promise.all([
      fetchCollection("/bookings"),
      roomsPromise,
    ]);
    renderBookings(container, bookings, rooms || []);
    container.setAttribute("aria-busy", "false");
    setState(panel, bookings.length ? "results" : "empty");
  } catch (error) {
    container.setAttribute("aria-busy", "false");
    setState(panel, "error", error.message);
  }
}

async function initialize() {
  const roomsPromise = loadRooms();
  await loadBookings(roomsPromise);
}

document.addEventListener("DOMContentLoaded", initialize);