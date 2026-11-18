/** Single source of truth for business contact details. */
export const BUSINESS = {
  name: "Pizza King",
  tagline: "Fast Food. Big Taste. King Vibes.",
  type: "Fast Food Restaurant",
  address: "PWD Islamabad, Opposite London Bakery, Mankiala, Rawalpindi",
  phone: "0349 8190030",
  phoneIntl: "+92 3498190030",
  whatsapp: "923173712950",
  email: "info@pizzaking.pk",
} as const;

/** Software/website developer credit (kept subtle, secondary to the restaurant brand). */
export const DEVELOPER = {
  name: "AM Enterprises",
  phone: "03173712950",
} as const;

export const waLink = (text: string) =>
  `https://wa.me/${BUSINESS.whatsapp}?text=${encodeURIComponent(text)}`;
