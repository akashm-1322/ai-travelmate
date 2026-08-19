import { openDB } from "idb";

const DB_NAME = "ai-travelmate";
const DB_VERSION = 1;

const dbPromise = openDB(
  DB_NAME,
  DB_VERSION,
  {
    upgrade(db) {
      if (!db.objectStoreNames.contains("trips")) {
        db.createObjectStore("trips", {
          keyPath: "id",
        });
      }

      if (!db.objectStoreNames.contains("messages")) {
        db.createObjectStore("messages", {
          keyPath: "id",
        });
      }

      if (!db.objectStoreNames.contains("guides")) {
        db.createObjectStore("guides", {
          keyPath: "id",
        });
      }

      if (!db.objectStoreNames.contains("expenses")) {
        db.createObjectStore("expenses", {
          keyPath: "id",
        });
      }
    },
  }
);

export async function saveTrip(trip) {
  const db = await dbPromise;

  await db.put("trips", trip);

  return trip;
}

export async function getTrip(id) {
  const db = await dbPromise;

  return db.get("trips", id);
}

export async function saveMessage(message) {
  const db = await dbPromise;

  await db.put("messages", message);

  return message;
}

export async function getMessages() {
  const db = await dbPromise;

  return db.getAll("messages");
}

export async function saveGuide(guide) {
  const db = await dbPromise;

  await db.put("guides", guide);

  return guide;
}

export async function saveExpense(expense) {
  const db = await dbPromise;

  await db.put("expenses", expense);

  return expense;
}