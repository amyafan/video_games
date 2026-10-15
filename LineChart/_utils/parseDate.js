export default function parseDate(date) {
	if (date instanceof Date) return date;
	const [yyyy, mm, dd] = date.split('-').map(Number);
	return new Date(yyyy, mm - 1, dd);
}
