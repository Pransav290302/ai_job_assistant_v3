/**
 * Strip HTML tags and decode common entities so job descriptions
 * from scrapers (e.g. containing <b>, &nbsp;) display as plain text.
 */
export function stripHtml(html: string): string {
  if (!html || typeof html !== "string") return "";
  let text = html
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/g, "\u00A0")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'");
  return text.replace(/\s+/g, " ").trim();
}
