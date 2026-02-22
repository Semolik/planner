interface ErrorMessage {
    message: string;
    status: number | null;
}

interface ErrorResponse {
    detail?: string | Array<{ msg: string }>;
    message?: string;
}

interface AxiosError {
    response?: {
        status: number;
        data?: ErrorResponse;
        message?: string;
    };
    request?: any;
    message?: string;
}

interface OpenApiError {
    body?: ErrorResponse;
    status?: number;
    request?: {
        errors?: Record<string, string>;
    };
    message?: string;
}

const messages: Record<string, string> = {
    RESET_PASSWORD_BAD_TOKEN: "Запрос на сброс пароля устарел.",
    VERIFY_USER_ALREADY_VERIFIED: "Пользователь уже подтвержден.",
    LOGIN_BAD_CREDENTIALS: "Неверный логин или пароль.",
};

const getErrorMessage = (error_code: string | number): string => {
    return messages[String(error_code)] || String(error_code);
};

const HandleAxiosError = (error: AxiosError, errorText?: string): ErrorMessage => {
    if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.detail || errorText || error.message;
        return {
            message: Array.isArray(message)
                ? message
                      .map((msg: any) => getErrorMessage(msg.msg))
                      .join("\n")
                : getErrorMessage(String(message)),
            status: status,
        };
    } else if (error.request) {
        return {
            message: "Сервер не ответил на запрос",
            status: null,
        };
    } else {
        return {
            message: "Произошла ошибка",
            status: null,
        };
    }
};

const HandleOpenApiError = (error: OpenApiError, errorText?: string): ErrorMessage => {
    if (error.body) {
        const message = error.body?.detail || errorText;
        if (message) {
            return {
                message: getErrorMessage(String(message)),
                status: error.status || null,
            };
        }
    } else if (error.request) {
        return {
            message: "Сервер не ответил на запрос",
            status: null,
        };
    } else if (error.request) {
        if (error.request.errors) {
            const statusCodes = Object.keys(error.request.errors);
            if (statusCodes.includes("401")) {
                return {
                    message: "Неверный логин или пароль",
                    status: 401,
                };
            }
            return {
                message: getErrorMessage(error.request.errors[statusCodes[0]]),
                status: Number(statusCodes[0]),
            };
        }
    }
    return {
        message: "Произошла ошибка",
        status: null,
    };
};

export { HandleAxiosError, HandleOpenApiError };

