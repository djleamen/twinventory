import type { Product } from "@/lib/types"

export type SlotId = "top" | "bottom" | "full" | "outer" | "shoes" | "accessory"

export type Slot = { id: SlotId; label: string; categories: string[] }

/** Category names exactly as stored in the catalog. */
export const SLOTS: Slot[] = [
  {
    id: "top",
    label: "Top",
    categories: ["Shirts", "Blouses", "T-Shirts", "Clothing Tops", "Sweaters", "Hoodies", "Activewear Tops"],
  },
  { id: "bottom", label: "Bottom", categories: ["Pants", "Trousers", "Palazzo Pants", "Shorts", "Leggings"] },
  {
    id: "full",
    label: "Full outfit",
    categories: [
      "Dresses", "Suits", "Outfit Sets", "Loungewear Sets", "Pajamas", "Robes",
      "Uniforms & Workwear", "Lingerie", "Traditional & Ceremonial Clothing",
    ],
  },
  { id: "outer", label: "Outerwear", categories: ["Coats & Jackets", "Cardigans", "Vests", "Blazers"] },
  { id: "shoes", label: "Shoes", categories: ["Shoes", "Athletic Shoes"] },
  { id: "accessory", label: "Accessory", categories: ["Watches", "Belts", "Scarves & Shawls"] },
]

export const HIDDEN_CATEGORIES = new Set(["Baby & Children's Clothing"])

export const ALL_CATEGORIES = SLOTS.flatMap((s) => s.categories)

export function slotForCategory(category: string): SlotId | undefined {
  return SLOTS.find((s) => s.categories.includes(category))?.id
}

export type Outfit = Partial<Record<SlotId, Product>>

/** Puts a product in its slot. Full outfit and top/bottom replace each other. */
export function addToOutfit(outfit: Outfit, product: Product): Outfit {
  const slot = slotForCategory(product.category)
  if (!slot) return outfit
  const next: Outfit = { ...outfit, [slot]: product }
  if (slot === "full") {
    delete next.top
    delete next.bottom
  }
  if (slot === "top" || slot === "bottom") delete next.full
  return next
}

export function removeFromOutfit(outfit: Outfit, slot: SlotId): Outfit {
  const next = { ...outfit }
  delete next[slot]
  return next
}

export function outfitItems(outfit: Outfit): Product[] {
  return SLOTS.map((s) => outfit[s.id]).filter((p): p is Product => !!p)
}
