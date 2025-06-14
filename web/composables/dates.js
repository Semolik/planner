export function getDateString(date) {
    return new Date(date).toLocaleDateString("ru-RU", {
        day: "2-digit",
        month: "long",
    });
}
export function addDays(date, days) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}
export const addDaysToDate = (date, days) => {
    const deadlineDate = new Date(date);
    deadlineDate.setDate(deadlineDate.getDate() + days);
    return deadlineDate.toISOString().split("T")[0];
};
