import type { UserReadWithEmail } from "@/client";

const useFullName = (user?: Partial<UserReadWithEmail> | null): string | undefined => {
    if (!user) return;
    return [user.first_name, user.last_name].filter((el) => !!el).join(" ");
};

export { useFullName };

