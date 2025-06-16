/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_set_token_vk_token_post } from '../models/Body_set_token_vk_token_post';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class VkService {
    /**
     * Set Token
     * @param formData
     * @returns void
     * @throws ApiError
     */
    public static setTokenVkTokenPost(
        formData: Body_set_token_vk_token_post,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/vk/token',
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
    public static deleteTokenVkTokenDelete(): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/vk/token',
        });
    }
    /**
     * Get Token Status
     * @returns boolean Successful Response
     * @throws ApiError
     */
    public static getTokenStatusVkTokenStatusGet(): CancelablePromise<boolean> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/vk/token/status',
        });
    }
}
