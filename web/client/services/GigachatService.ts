/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BalanceResponse } from '../models/BalanceResponse';
import type { Body_set_token_gigachat_token_post } from '../models/Body_set_token_gigachat_token_post';
import type { StatusResponse } from '../models/StatusResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GigachatService {
    /**
     * Get Status
     * Получить статус наличия GigaChat токена
     * @returns StatusResponse Successful Response
     * @throws ApiError
     */
    public static getStatusGigachatStatusGet(): CancelablePromise<StatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/gigachat/status',
        });
    }
    /**
     * Set Token
     * @param formData
     * @returns void
     * @throws ApiError
     */
    public static setTokenGigachatTokenPost(
        formData: Body_set_token_gigachat_token_post,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/gigachat/token',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Token
     * @returns void
     * @throws ApiError
     */
    public static deleteTokenGigachatTokenDelete(): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/gigachat/token',
        });
    }
    /**
     * Get Balance
     * Получить информацию о балансе GigaChat токенов.
     * По умолчанию доступно 900 000 токенов для генерации текста.
     * @returns BalanceResponse Successful Response
     * @throws ApiError
     */
    public static getBalanceGigachatBalanceGet(): CancelablePromise<BalanceResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/gigachat/balance',
        });
    }
}
