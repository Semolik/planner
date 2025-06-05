export function getDateString(date) {
    return new Date(date).toLocaleDateString("ru-RU", {
        day: "2-digit",
        month: "long",
    });
}
