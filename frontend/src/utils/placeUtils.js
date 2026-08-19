export function getCategoryIcon(category = "") {
    const normalized = category
      .toLowerCase()
      .trim();
  
    const icons = {
      origin: "🚩",
      destination: "🏁",
      place_of_worship: "🛕",
      restaurant: "🍽️",
      cafe: "☕",
      beach: "🌊",
      park: "🌳",
      museum: "🏛️",
      shopping: "🛍️",
      hotel: "🏨",
      attraction: "📍",
      custom_location: "⭐",
    };
  
    return icons[normalized] || "📍";
  }
  
  
  export function formatCategory(category = "") {
    if (!category) {
      return "Place";
    }
  
    return category
      .replaceAll("_", " ")
      .replace(/\b\w/g, (character) =>
        character.toUpperCase()
      );
  }