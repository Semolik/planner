export const validateUrl = (url) => {
    const urlPattern = /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)(\/[\w- .\/?%&=]*)?$/;
    return urlPattern.test(url);
};
