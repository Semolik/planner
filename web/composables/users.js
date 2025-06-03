const useFullName = (user) => {
    if (!user) return;
    return [user.first_name, user.last_name].filter((el) => !!el).join(" ");
};
export { useFullName };
