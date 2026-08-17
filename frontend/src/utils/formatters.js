/**
 * Consolidated number, currency, and date/time formatter utilities.
 */

/**
 * Formats a numeric price into a localized string with proper decimal precision.
 * Integer prices get 2 decimal places, while floats get up to 6 decimal places.
 *
 * @param {number|string} price - The raw price value.
 * @returns {string} Formatted price or 'N/A'.
 */
export const formatPrice = (price) => {
  const num = Number(price);
  if (!Number.isFinite(num)) return 'N/A';
  return num.toLocaleString(undefined, {
    minimumFractionDigits: Number.isInteger(num) ? 2 : 0,
    maximumFractionDigits: Number.isInteger(num) ? 2 : 6,
  });
};

/**
 * Formats a 24h price change percentage with sign and 2 decimals.
 *
 * @param {number|string} priceChange - The raw price change percentage.
 * @returns {string} Formatted percentage (e.g. '+2.50%') or 'N/A'.
 */
export const formatPriceChange = (priceChange) => {
  const num = Number(priceChange);
  if (!Number.isFinite(num)) return 'N/A';
  return `${num > 0 ? '+' : ''}${num.toFixed(2)}%`;
};

/**
 * Returns the CSS class corresponding to the direction of a price change.
 *
 * @param {number|string} priceChange - The raw price change percentage.
 * @returns {string} 'price-up', 'price-down', or 'price-neutral'.
 */
export const getPriceChangeClass = (priceChange) => {
  const num = Number(priceChange);
  if (!Number.isFinite(num)) return 'price-neutral';
  return num >= 0 ? 'price-up' : 'price-down';
};

/**
 * Formats a raw market volume or currency number into USD currency string.
 *
 * @param {number|string} amount - The numeric volume or amount.
 * @returns {string} Formatted USD currency string.
 */
export const formatCurrency = (amount) => {
  const num = Number(amount);
  if (!Number.isFinite(num)) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(num);
};

// Alias for formatCurrency
export const formatCur = formatCurrency;

/**
 * Formats a date/timestamp string into a localized 12-hour AM/PM time string.
 *
 * @param {string|number|Date} date - The date or timestamp.
 * @returns {string} Formatted time string.
 */
export const formatTime = (date) => {
  if (!date) return 'N/A';
  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) return 'N/A';

  let hours = dateObj.getHours();
  const minutes = String(dateObj.getMinutes()).padStart(2, '0');
  const seconds = String(dateObj.getSeconds()).padStart(2, '0');

  if (hours > 12) {
    hours -= 12;
    return `${String(hours).padStart(2, '0')}:${minutes}:${seconds} PM`;
  }

  if (hours === 0) {
    return `12:${minutes}:${seconds} AM`;
  }

  return `${String(hours).padStart(2, '0')}:${minutes}:${seconds} AM`;
};
