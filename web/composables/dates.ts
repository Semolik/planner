export function getDateString(date: string | Date): string {
    return new Date(date).toLocaleDateString("ru-RU", {
        day: "2-digit",
        month: "long",
    });
}

export function addDays(date: string | Date, days: number): Date {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

export const addDaysToDate = (date: string | Date, days: number): string => {
    const deadlineDate = new Date(date);
    deadlineDate.setDate(deadlineDate.getDate() + days);
    return deadlineDate.toISOString().split("T")[0];
};

