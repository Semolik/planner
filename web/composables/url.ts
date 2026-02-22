export const validateUrl = (url: string): boolean => {
    const urlPattern = /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)(\/[\w- .\/?%&=]*)?$/;
    return urlPattern.test(url);
};

